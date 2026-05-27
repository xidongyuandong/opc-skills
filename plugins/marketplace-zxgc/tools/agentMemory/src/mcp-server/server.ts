#!/usr/bin/env node

import { StorageManager } from './storage';
import { CacheManager } from './cache';
import { MCPTools } from './tools';
import { SocketBridge } from './socket-bridge';
import { MemoryBankSync } from './memory-bank-sync';
import { StandaloneDashboard } from '../standalone-dashboard';

interface MCPRequest {
    jsonrpc: string;
    id?: string | number;
    method: string;
    params?: any;
}

interface MCPResponse {
    jsonrpc: string;
    id?: string | number;
    result?: any;
    error?: {
        code: number;
        message: string;
        data?: any;
    };
}

/**
 * Simple MCP Server using stdio transport
 * This server implements the Model Context Protocol for memory tools
 */
class MCPServer {
    private storage: StorageManager;
    private cache: CacheManager;
    private tools: MCPTools;
    private projectId: string;
    private syncEngine: MemoryBankSync;
    private framedTransport = false;

    constructor(projectId: string, workspacePath: string) {
        this.projectId = projectId;

        // Use absolute path based on workspace
        const storagePath = workspacePath + '/.agentMemory';
        this.storage = new StorageManager(storagePath);

        this.cache = new CacheManager({
            maxSize: 10000,
            ttl: 3600000 // 1 hour
        });

        // Initialize sync engine
        this.syncEngine = new MemoryBankSync(workspacePath);
        this.tools = new MCPTools(this.storage, this.cache, this.syncEngine);

        console.error(`[MCP Server] Initialized for project: ${projectId}`);
        console.error(`[MCP Server] Workspace path: ${workspacePath}`);
        console.error(`[MCP Server] Storage path: ${storagePath}`);
    }

    /**
     * Handle incoming MCP request (public for socket bridge)
     */
    public async handleRequest(request: MCPRequest): Promise<MCPResponse | null> {
        const { method, params, id } = request;

        // JSON-RPC: If no ID, this is a notification - don't send a response
        if (id === undefined || id === null) {
            console.error(`[MCP Server] Received notification (no response needed): ${method}`);
            return null;
        }

        try {
            switch (method) {
                case 'tools/list':
                    return {
                        jsonrpc: '2.0',
                        id,
                        result: {
                            tools: MCPTools.listTools()
                        }
                    };

                case 'tools/call': {
                    const { name, arguments: args } = params;

                    // Add projectId to arguments
                    const toolArgs = { ...args, projectId: this.projectId };

                    // Call the appropriate tool
                    let result;
                    switch (name) {
                        case 'memory_write':
                            result = await this.tools.memory_write(toolArgs);
                            break;
                        case 'memory_read':
                            result = await this.tools.memory_read(toolArgs);
                            break;
                        case 'memory_search':
                            result = await this.tools.memory_search(toolArgs);
                            break;
                        case 'memory_list':
                            result = await this.tools.memory_list(toolArgs);
                            break;
                        case 'memory_update':
                            result = await this.tools.memory_update(toolArgs);
                            break;
                        case 'project_init':
                            result = await this.tools.project_init(toolArgs);
                            break;
                        case 'memory_stats':
                            result = await this.tools.memory_stats(toolArgs);
                            break;
                        default:
                            throw new Error(`Unknown tool: ${name}`);
                    }

                    return {
                        jsonrpc: '2.0',
                        id,
                        result: {
                            content: [
                                {
                                    type: 'text',
                                    text: JSON.stringify(result, null, 2)
                                }
                            ]
                        }
                    };
                }

                case 'initialize':
                    // Initialize the project
                    await this.tools.project_init({ projectId: this.projectId });
                    return {
                        jsonrpc: '2.0',
                        id,
                        result: {
                            protocolVersion: '2024-11-05',
                            capabilities: {
                                tools: {}
                            },
                            serverInfo: {
                                name: 'agentMemory-mcp-server',
                                version: '0.1.0'
                            }
                        }
                    };

                case 'ping':
                    return {
                        jsonrpc: '2.0',
                        id,
                        result: {}
                    };

                default:
                    throw new Error(`Unknown method: ${method}`);
            }
        } catch (error: any) {
            return {
                jsonrpc: '2.0',
                id,
                error: {
                    code: -32603,
                    message: error.message,
                    data: error.stack
                }
            };
        }
    }

    /**
     * Start the server with stdio transport
     */
    start() {
        console.error('[MCP Server] Starting stdio transport...');

        let buffer: Buffer<ArrayBufferLike> = Buffer.alloc(0);

        process.stdin.on('data', async (chunk) => {
            const incoming = Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk);
            buffer = Buffer.concat([buffer, incoming]);

            const prefix = buffer.toString('utf8', 0, Math.min(buffer.length, 64)).trimStart();
            if (prefix.startsWith('Content-Length:')) {
                this.framedTransport = true;
            }

            if (this.framedTransport) {
                buffer = await this.processFramedMessages(buffer);
            } else {
                buffer = await this.processLineMessages(buffer);
            }
        });

        process.stdin.on('end', () => {
            console.error('[MCP Server] stdin closed, shutting down...');
            process.exit(0);
        });

        console.error('[MCP Server] Ready and listening on stdio');
    }

    private async processLineMessages(buffer: Buffer<ArrayBufferLike>): Promise<Buffer<ArrayBufferLike>> {
        const text = buffer.toString('utf8');
        const lines = text.split('\n');
        const remainder = lines.pop() || '';

        for (const line of lines) {
            await this.processMessage(line.trim());
        }

        return Buffer.from(remainder, 'utf8');
    }

    private async processFramedMessages(buffer: Buffer<ArrayBufferLike>): Promise<Buffer<ArrayBufferLike>> {
        let offset = 0;

        while (offset < buffer.length) {
            const headerEnd = this.findHeaderEnd(buffer, offset);
            if (headerEnd === null) break;

            const headerText = buffer.toString('utf8', offset, headerEnd.headerEnd);
            const match = headerText.match(/Content-Length:\s*(\d+)/i);
            if (!match) {
                console.error('[MCP Server] Missing Content-Length header');
                offset = headerEnd.bodyStart;
                continue;
            }

            const contentLength = Number(match[1]);
            const bodyEnd = headerEnd.bodyStart + contentLength;
            if (buffer.length < bodyEnd) break;

            const body = buffer.toString('utf8', headerEnd.bodyStart, bodyEnd);
            await this.processMessage(body.trim());
            offset = bodyEnd;
        }

        return buffer.subarray(offset);
    }

    private findHeaderEnd(buffer: Buffer<ArrayBufferLike>, offset: number): { headerEnd: number; bodyStart: number } | null {
        const crlf = buffer.indexOf('\r\n\r\n', offset, 'utf8');
        if (crlf !== -1) {
            return { headerEnd: crlf, bodyStart: crlf + 4 };
        }

        const lf = buffer.indexOf('\n\n', offset, 'utf8');
        if (lf !== -1) {
            return { headerEnd: lf, bodyStart: lf + 2 };
        }

        return null;
    }

    private async processMessage(message: string): Promise<void> {
        if (!message) return;

        try {
            const request = JSON.parse(message) as MCPRequest;
            console.error(`[MCP Server] Received: ${request.method}`);

            const response = await this.handleRequest(request);
            if (response !== null) {
                this.writeResponse(response);
            }
        } catch (error: any) {
            console.error('[MCP Server] Error processing message:', error);
            this.writeResponse({
                jsonrpc: '2.0',
                error: {
                    code: -32700,
                    message: 'Parse error',
                    data: error.message
                }
            });
        }
    }

    private writeResponse(response: MCPResponse): void {
        const payload = JSON.stringify(response);

        if (this.framedTransport) {
            const length = Buffer.byteLength(payload, 'utf8');
            process.stdout.write(`Content-Length: ${length}\r\n\r\n${payload}`);
            return;
        }

        process.stdout.write(payload + '\n');
    }
}

// Main entry point
const projectId = process.argv[2] || 'default-project';
const workspacePath = process.argv[3] || process.cwd();

const server = new MCPServer(projectId, workspacePath);
server.start();

// The Unix socket bridge is useful for KiloCode/RooCode-style clients, but Codex
// only needs stdio. Keep it opt-in to avoid local socket permission/conflict issues.
if (process.env.AGENT_MEMORY_SOCKET_BRIDGE === '1') {
    const socketBridge = new SocketBridge(projectId);
    socketBridge.start((req) => server.handleRequest(req));
}

// The dashboard binds to a local port. Keep it opt-in for MCP clients such as Codex.
if (process.env.AGENT_MEMORY_DASHBOARD === '1') {
    const dashboard = new StandaloneDashboard(workspacePath);
    dashboard.start();
}
