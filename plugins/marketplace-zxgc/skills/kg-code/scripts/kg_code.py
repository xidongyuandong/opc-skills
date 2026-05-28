#!/usr/bin/env python3
"""kg-code command helper.

Two operations are intentionally exposed:
- create: build or refresh code graph artifacts for one or more repositories.
- query: search existing graph artifacts and Markdown/docs for evidence.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Iterable


CORE_DEPENDENT_SKILLS = [
    "marketplace-zxgc",
    "codex-remote-container",
    "codex-ssh-remote-config",
]

REMOTE_DEPENDENT_SKILLS = [
    "c250",
]

DEFAULT_ALIASES = {
    "rllm": "/Users/zhengyuyu/programs/lixiang/rllm",
    "code-complete": "/Users/zhengyuyu/programs/lixiang/code-complete",
    "team-workspace": "/Users/zhengyuyu/programs/lixiang/agent_create_code/output/开发模式/team-workspace",
}

REMOTE_ALIASES = {
    "cov-evalution": {
        "kind": "c250",
        "repo": "/home/chehejia/cov-evalution",
        "gitnexus": "cov-evalution",
    },
    "cov-evalution-qwen3_6": {
        "kind": "c250",
        "repo": "/home/chehejia/cov-evalution-qwen3_6-eval-0521",
        "gitnexus": "cov-evalution-qwen3_6",
    },
    "code-complete-c250": {
        "kind": "c250",
        "repo": "/home/chehejia/code-complete",
        "gitnexus": "code-complete-c250",
    },
    "rllm-lpai-dev": {
        "kind": "ssh",
        "host": "lpai-zyy-dev",
        "repo": "/lpai/code/rllm",
        "gitnexus": "rllm-lpai-dev",
    },
    "code-complete-lpai-dev": {
        "kind": "ssh",
        "host": "lpai-zyy-dev",
        "repo": "/lpai/code/code-complete",
        "gitnexus": "code-complete-lpai-dev",
    },
}


def codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def active_skill_dir(name: str) -> Path:
    return codex_home() / "skills" / name


def is_skill_installed(name: str) -> bool:
    return (active_skill_dir(name) / "SKILL.md").is_file()


def default_skill_source_roots() -> list[Path]:
    roots = []
    env_roots = os.environ.get("KG_CODE_SKILL_SOURCE_ROOTS", "")
    for raw in env_roots.split(os.pathsep):
        if raw:
            roots.append(Path(raw).expanduser())
    roots.extend(
        [
            skill_root().parent,
            Path("~/marketplace-zxgc/plugins/marketplace-zxgc/skills").expanduser(),
            Path("~/.codex/skills").expanduser(),
            Path("~/.agents/skills").expanduser(),
            Path("~/.claude/skills").expanduser(),
            Path("/data/jenkins/marketplace-zxgc/plugins/marketplace-zxgc/skills"),
            Path("/data/jenkins/.codex/home/skills"),
        ]
    )
    deduped = []
    seen = set()
    for root in roots:
        try:
            key = str(root.resolve())
        except OSError:
            key = str(root)
        if key not in seen:
            seen.add(key)
            deduped.append(root)
    return deduped


def find_skill_source(name: str) -> Path | None:
    target = active_skill_dir(name).resolve()
    for root in default_skill_source_roots():
        candidate = root / name
        if not (candidate / "SKILL.md").is_file():
            continue
        try:
            if candidate.resolve() == target:
                continue
        except OSError:
            pass
        return candidate
    return None


def copy_skill_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        backup = codex_home() / "backups" / "skills" / f"kg-code-autoinstall-{os.getpid()}" / dst.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dst), str(backup))

    def ignore(_dir: str, names: list[str]) -> set[str]:
        return {name for name in names if name == "__pycache__" or name.endswith(".pyc") or name == ".DS_Store"}

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=ignore)


def ensure_dependent_skills(extra: Iterable[str] = (), install: bool = True) -> list[dict]:
    wanted = [*CORE_DEPENDENT_SKILLS, *extra]
    results = []
    seen = set()
    for name in wanted:
        if not name or name in seen:
            continue
        seen.add(name)
        dst = active_skill_dir(name)
        if is_skill_installed(name):
            results.append({"skill": name, "status": "present", "path": str(dst)})
            continue
        if not install:
            results.append({"skill": name, "status": "missing", "path": str(dst)})
            continue
        src = find_skill_source(name)
        if not src:
            results.append(
                {
                    "skill": name,
                    "status": "missing-source",
                    "path": str(dst),
                    "searched": [str(root) for root in default_skill_source_roots()],
                }
            )
            continue
        try:
            copy_skill_tree(src, dst)
            results.append({"skill": name, "status": "installed", "source": str(src), "path": str(dst)})
        except OSError as exc:
            results.append({"skill": name, "status": "error", "source": str(src), "path": str(dst), "error": str(exc)})
    return results


def ensure_for_repo(repo_value: str | None, install: bool = True) -> list[dict]:
    extra = []
    if repo_value in REMOTE_ALIASES and REMOTE_ALIASES[repo_value]["kind"] == "c250":
        extra.extend(REMOTE_DEPENDENT_SKILLS)
    return ensure_dependent_skills(extra=extra, install=install)


def resolve_repo(value: str) -> Path:
    raw = DEFAULT_ALIASES.get(value, value)
    return Path(raw).expanduser().resolve()


def run(cmd: list[str], cwd: Path | None = None, check: bool = False) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stdout}")
    return proc.returncode, proc.stdout


def run_remote(spec: dict, script: str, check: bool = False) -> tuple[int, str]:
    if spec["kind"] == "c250":
        cmd = ["c250-exec", "-C", spec["repo"], f"python3 - <<'PY'\n{script}\nPY"]
    elif spec["kind"] == "ssh":
        cmd = ["/usr/bin/ssh", spec["host"], f"cd {sh_quote(spec['repo'])} && python3 - <<'PY'\n{script}\nPY"]
    else:
        raise ValueError(f"unsupported remote kind: {spec['kind']}")
    return run(cmd, check=check)


def sh_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def make_understand_compatible(repo: Path) -> dict:
    graph_path = repo / "graphify-out" / "graph.json"
    out_dir = repo / ".understand-anything"
    out_path = out_dir / "knowledge-graph.json"
    meta_path = out_dir / "meta.json"
    if not graph_path.exists():
        return {"tool": "understand-compatible", "status": "skipped", "reason": f"missing {graph_path}"}

    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    links = data.get("links", data.get("edges", []))
    layers = sorted({str(n.get("source_file") or n.get("filePath") or "") for n in nodes if n.get("source_file") or n.get("filePath")})
    compatible = {
        "schema": "kg-code-understand-compatible-v1",
        "source": str(graph_path),
        "nodes": nodes,
        "edges": links,
        "layers": layers,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(compatible, ensure_ascii=False, indent=2), encoding="utf-8")
    meta_path.write_text(
        json.dumps(
            {
                "source": str(graph_path),
                "nodes": len(nodes),
                "edges": len(links),
                "layers": len(layers),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"tool": "understand-compatible", "status": "ok", "nodes": len(nodes), "edges": len(links), "layers": len(layers)}


def create_repo(repo: Path, tools: set[str], register_alias: str | None) -> list[dict]:
    if not repo.exists():
        return [{"repo": str(repo), "tool": "repo", "status": "error", "reason": "path does not exist"}]

    results: list[dict] = []
    if "code-review-graph" in tools:
        if register_alias:
            code, out = run(["code-review-graph", "register", str(repo), "--alias", register_alias])
            results.append({"tool": "code-review-graph-register", "status": "ok" if code == 0 else "error", "output": out.strip()[-800:]})
        code, out = run(["code-review-graph", "update", "--repo", str(repo)])
        if code != 0:
            code, out = run(["code-review-graph", "build", "--repo", str(repo)])
        results.append({"tool": "code-review-graph", "status": "ok" if code == 0 else "error", "output": out.strip()[-1200:]})

    if "graphify" in tools:
        if shutil.which("graphify"):
            code, out = run(["graphify", "update", str(repo)])
            results.append({"tool": "graphify", "status": "ok" if code == 0 else "error", "output": out.strip()[-1200:]})
        else:
            results.append({"tool": "graphify", "status": "skipped", "reason": "graphify not in PATH"})

    if "gitnexus" in tools:
        if shutil.which("gitnexus"):
            name = register_alias or repo.name
            code, out = run(
                ["gitnexus", "analyze", "--index-only", "--drop-embeddings", "--name", name, str(repo)],
                cwd=repo,
            )
            results.append({"tool": "gitnexus", "status": "ok" if code == 0 else "error", "output": out.strip()[-1200:]})
        else:
            results.append({"tool": "gitnexus", "status": "skipped", "reason": "gitnexus not in PATH"})

    if "understand" in tools or "understand-compatible" in tools:
        results.append(make_understand_compatible(repo))

    return results


def terms(text: str) -> list[str]:
    low = text.lower()
    result = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", low)
    expansions = {
        "shell": ["sh", "shell"],
        "脚本": ["sh", "script"],
        "训练": ["train", "training"],
        "强化": ["prod", "ppo", "rl", "reinforcement", "smolagents"],
        "评测": ["eval", "evaluation", "run_batch", "agent_eval"],
        "日志": ["log", "logs"],
        "轨迹": ["trace", "memory", "json-output"],
        "文档": ["md", "docs", "readme"],
        "哪个": [],
        "文件": [],
        "进行": [],
    }
    for key, values in expansions.items():
        if key in low:
            result.extend(values)
    if "sft" in low:
        result.extend(["sft", "full_parameter", "supervised"])
    if "qwen3.6" in low or "qwen3_6" in low:
        result.extend(["qwen3_6", "qwen3", "3_6"])
    if "apr" in low:
        result.append("apr")
    seen = set()
    deduped = []
    for item in result:
        if item and item not in seen:
            seen.add(item)
            deduped.append(item)
    return deduped


def like_expr(query: str) -> tuple[str, list[str]]:
    ts = terms(query) or [query.lower()]
    clauses = []
    params: list[str] = []
    for term in ts:
        clauses.append("(lower(name) LIKE ? OR lower(qualified_name) LIKE ? OR lower(file_path) LIKE ?)")
        params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])
    return " OR ".join(clauses), params


def score_text(text: str, query: str) -> int:
    low = text.lower()
    ts = terms(query)
    if not ts:
        return int(query.lower() in low)
    score = 0
    for term in ts:
        variants = {term}
        variants.add(term.replace(".", "_"))
        variants.add(term.replace("_", "."))
        if term.endswith("ing") and len(term) > 5:
            variants.add(term[:-3])
        if term.endswith("ed") and len(term) > 4:
            variants.add(term[:-2])
        if any(v and v in low for v in variants):
            score += 1
    return score


def query_sqlite(repo: Path, query: str, limit: int) -> list[dict]:
    db = repo / ".code-review-graph" / "graph.db"
    if not db.exists():
        return []
    where, params = like_expr(query)
    sql = f"""
        SELECT kind, name, qualified_name, file_path, line_start, line_end
        FROM nodes
        WHERE {where}
        ORDER BY file_path, line_start
        LIMIT ?
    """
    conn = sqlite3.connect(str(db))
    try:
        rows = conn.execute(sql, [*params, limit]).fetchall()
    finally:
        conn.close()
    return [
        {
            "source": "code-review-graph",
            "kind": row[0],
            "name": row[1],
            "qualified_name": row[2],
            "file_path": row[3],
            "line_start": row[4],
            "line_end": row[5],
            "score": score_text(" ".join(str(part or "") for part in row[:4]), query),
        }
        for row in rows
    ]


def walk_files(repo: Path, suffixes: Iterable[str]) -> Iterable[Path]:
    skip = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        ".pytest_cache",
        ".worktrees",
        ".code-review-graph",
        ".gitnexus",
        ".understand-anything",
        "graphify-out",
    }
    suffixes = tuple(suffixes)
    repo = repo.resolve()
    for root, dirs, files in os.walk(repo):
        root_path = Path(root)
        dirs[:] = [
            d
            for d in dirs
            if d not in skip
            and not d.startswith(".")
            and not ((root_path / d / ".git").exists() and (root_path / d).resolve() != repo)
        ]
        for name in files:
            path = Path(root) / name
            if path.suffix in suffixes:
                yield path


def query_markdown(repo: Path, query: str, limit: int) -> list[dict]:
    results: list[dict] = []
    for path in walk_files(repo, [".md", ".sh", ".py", ".toml", ".yaml", ".yml"]):
        rel = str(path.relative_to(repo))
        rel_score = score_text(rel, query)
        hit = rel_score > 0
        snippet = ""
        content_score = 0
        line_no = None
        if path.stat().st_size < 400_000:
            try:
                for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    line_score = score_text(line, query)
                    if line_score > content_score:
                        content_score = line_score
                        hit = True
                        snippet = line.strip()[:240]
                        line_no = idx
            except OSError:
                line_no = None
        if hit:
            score = rel_score * 2 + content_score
            if path.suffix == ".sh":
                score += 2
            if "/examples/" in f"/{rel}":
                score += 1
            if "sft" in query.lower() and "/sft/" in f"/{rel}":
                score += 4
            if "sft" in query.lower() and "test_sft_development-space.sh" in rel:
                score += 8
            if "强化" in query.lower() and "train_smolagents_prod.sh" in rel:
                score += 5
            if ("评测" in query.lower() or "eval" in query.lower()) and ("eval" in rel or "run_batch" in rel):
                score += 4
            if ("qwen3.6" in query.lower() or "qwen3_6" in query.lower()) and "task052101_run_batch.sh" in rel:
                score += 14
            if "pyproject" in query.lower() and rel.endswith("pyproject.toml"):
                score += 12
            if "uv" in query.lower() and rel.endswith("pyproject.toml"):
                score += 6
            results.append({"source": "file-scan", "file_path": rel, "line": line_no, "snippet": snippet, "score": score})
    results.sort(key=lambda item: (-item.get("score", 0), len(str(item.get("file_path", "")).split("/")), item.get("file_path", "")))
    return results[:limit]


def query_graphify(repo: Path, query: str, limit: int) -> list[dict]:
    graph = repo / "graphify-out" / "graph.json"
    if not graph.exists():
        graph = repo / ".understand-anything" / "knowledge-graph.json"
    if not graph.exists():
        return []
    data = json.loads(graph.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    results = []
    for node in nodes:
        hay = " ".join(str(node.get(k, "")) for k in ("label", "name", "id", "source_file", "filePath", "type")).lower()
        score = score_text(hay, query)
        if score > 0:
            results.append(
                {
                    "source": "graphify",
                    "label": node.get("label") or node.get("name") or node.get("id"),
                    "file_path": node.get("source_file") or node.get("filePath"),
                    "location": node.get("source_location"),
                    "kind": (node.get("metadata") or {}).get("kind") or node.get("type"),
                    "score": score,
                }
            )
    results.sort(key=lambda item: (-item.get("score", 0), item.get("file_path") or "", item.get("label") or ""))
    return results[:limit]


def remote_scan_script(repo: str, query: str, limit: int) -> str:
    return f"""
import json, os, re
from pathlib import Path

repo = Path({repo!r})
query = {query!r}
limit = {limit!r}

def terms(text):
    low = text.lower()
    result = re.findall(r"[a-z0-9]+(?:\\.[0-9]+)?", low)
    expansions = {{
        "shell": ["sh", "shell"],
        "脚本": ["sh", "script"],
        "训练": ["train", "training"],
        "强化": ["prod", "ppo", "rl", "reinforcement", "smolagents"],
        "评测": ["eval", "evaluation", "run_batch", "agent_eval"],
        "日志": ["log", "logs"],
        "轨迹": ["trace", "memory", "json-output"],
        "文档": ["md", "docs", "readme"],
    }}
    for key, values in expansions.items():
        if key in low:
            result.extend(values)
    if "sft" in low:
        result.extend(["sft", "full_parameter", "supervised"])
    if "qwen3.6" in low or "qwen3_6" in low:
        result.extend(["qwen3_6", "qwen3", "3_6"])
    if "apr" in low:
        result.append("apr")
    out = []
    seen = set()
    for item in result:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out

def score_text(text, query):
    low = text.lower()
    score = 0
    for term in terms(query):
        variants = {{term, term.replace(".", "_"), term.replace("_", ".")}}
        if term.endswith("ing") and len(term) > 5:
            variants.add(term[:-3])
        if any(v and v in low for v in variants):
            score += 1
    return score

skip = {{".git", ".venv", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache", ".worktrees", ".code-review-graph", ".gitnexus", ".understand-anything", "graphify-out"}}
suffixes = {{".md", ".sh", ".py", ".toml", ".yaml", ".yml"}}
results = []
for root, dirs, files in os.walk(repo):
    root_path = Path(root)
    dirs[:] = [d for d in dirs if d not in skip and not d.startswith(".") and not (root_path / d / ".git").exists()]
    for name in files:
        path = root_path / name
        if path.suffix not in suffixes:
            continue
        rel = str(path.relative_to(repo))
        rel_score = score_text(rel, query)
        content_score = 0
        snippet = ""
        line_no = None
        try:
            if path.stat().st_size < 400000:
                for idx, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    line_score = score_text(line, query)
                    if line_score > content_score:
                        content_score = line_score
                        snippet = line.strip()[:240]
                        line_no = idx
        except OSError:
            pass
        if rel_score or content_score:
            score = rel_score * 2 + content_score
            if path.suffix == ".sh":
                score += 2
            if "/agent/shells/" in "/" + rel or "/examples/" in "/" + rel:
                score += 1
            if "qwen3.6" in query.lower() and "qwen3_6" in rel:
                score += 4
            if ("评测" in query.lower() or "eval" in query.lower()) and ("eval" in rel or "run_batch" in rel):
                score += 4
            if ("qwen3.6" in query.lower() or "qwen3_6" in query.lower()) and "task052101_run_batch.sh" in rel:
                score += 14
            if "pyproject" in query.lower() and rel.endswith("pyproject.toml"):
                score += 12
            if "uv" in query.lower() and rel.endswith("pyproject.toml"):
                score += 6
            results.append({{"source": "remote-file-scan", "file_path": rel, "line": line_no, "snippet": snippet, "score": score}})
results.sort(key=lambda item: (-item["score"], item["file_path"]))
print(json.dumps(results[:limit], ensure_ascii=False))
"""


def query_remote(alias: str, spec: dict, query: str, limit: int) -> list[dict]:
    source_limit = max(limit * 4, 20)
    script = remote_scan_script(spec["repo"], query, source_limit)
    code, out = run_remote(spec, script)
    results: list[dict] = []
    if code == 0:
        try:
            results.extend(json.loads(out.strip().splitlines()[-1]))
        except (json.JSONDecodeError, IndexError):
            results.append({"source": "remote-error", "file_path": spec["repo"], "snippet": out.strip()[-500:], "score": 0})
    else:
        results.append({"source": "remote-error", "file_path": spec["repo"], "snippet": out.strip()[-500:], "score": 0})

    git_cmd = f"gitnexus query {sh_quote(query)} -r {sh_quote(spec['gitnexus'])} -l {min(limit, 5)}"
    if spec["kind"] == "c250":
        code, out = run(["c250-exec", "-C", spec["repo"], git_cmd])
    else:
        code, out = run(["/usr/bin/ssh", spec["host"], git_cmd])
    if code == 0 and out.strip():
        results.append({"source": "gitnexus", "file_path": spec["gitnexus"], "snippet": out.strip()[:800], "score": 1})

    results.sort(key=lambda item: (-item.get("score", 0), item.get("file_path") or ""))
    return results[:limit]


def cmd_create(args: argparse.Namespace) -> int:
    dep_results = ensure_dependent_skills(install=not args.no_auto_install_skills)
    dep_errors = [item for item in dep_results if item["status"] in {"missing-source", "error"}]
    if dep_errors:
        print(json.dumps({"dependency_skills": dep_results}, ensure_ascii=False, indent=2), file=sys.stderr)

    tools = set(args.tools.split(","))
    all_results = []
    for repo_arg in args.repo:
        repo = resolve_repo(repo_arg)
        alias = args.alias if len(args.repo) == 1 else None
        all_results.append({"repo": str(repo), "results": create_repo(repo, tools, alias)})
    print(json.dumps(all_results, ensure_ascii=False, indent=2))
    return 0 if all(r.get("status") != "error" for item in all_results for r in item["results"]) else 1


def cmd_query(args: argparse.Namespace) -> int:
    dep_results = ensure_for_repo(args.repo, install=not args.no_auto_install_skills)
    dep_errors = [item for item in dep_results if item["status"] in {"missing-source", "error"}]
    if dep_errors:
        print(json.dumps({"dependency_skills": dep_results}, ensure_ascii=False, indent=2), file=sys.stderr)

    if args.repo in REMOTE_ALIASES:
        spec = REMOTE_ALIASES[args.repo]
        results = query_remote(args.repo, spec, args.query, args.limit)
        payload = {"repo": spec["repo"], "alias": args.repo, "query": args.query, "count": len(results), "results": results}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"repo: {payload['repo']}")
            print(f"alias: {payload['alias']}")
            print(f"query: {payload['query']}")
            print(f"count: {payload['count']}")
            for idx, item in enumerate(payload["results"], 1):
                print(f"{idx}. [{item.get('source')}] {item.get('file_path')}")
                if item.get("snippet"):
                    print(f"   {item.get('snippet')}")
        return 0 if results else 2

    repo = resolve_repo(args.repo)
    results = []
    source_limit = max(args.limit * 4, 20)
    results.extend(query_sqlite(repo, args.query, source_limit))
    results.extend(query_graphify(repo, args.query, source_limit))
    results.extend(query_markdown(repo, args.query, source_limit))
    results.sort(
        key=lambda item: (
            -item.get("score", 0),
            item.get("source", ""),
            item.get("file_path") or item.get("qualified_name") or item.get("label") or "",
        )
    )

    payload = {"repo": str(repo), "query": args.query, "count": len(results), "results": results[: args.limit]}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"repo: {payload['repo']}")
        print(f"query: {payload['query']}")
        print(f"count: {payload['count']}")
        for idx, item in enumerate(payload["results"], 1):
            print(f"{idx}. [{item.get('source')}] {item.get('file_path') or item.get('qualified_name') or item.get('label')}")
            detail = item.get("name") or item.get("label") or item.get("snippet")
            if detail:
                print(f"   {detail}")
    return 0 if results else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="kg-code create/query helper")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create", help="build or refresh code graph artifacts")
    create.add_argument("--repo", action="append", required=True, help="repo path or known alias; repeatable")
    create.add_argument("--alias", help="register alias for a single repo")
    create.add_argument(
        "--tools",
        default="code-review-graph,graphify,understand-compatible",
        help="comma-separated: code-review-graph,graphify,gitnexus,understand-compatible",
    )
    create.add_argument("--no-auto-install-skills", action="store_true", help="only report missing dependent skills")
    create.set_defaults(func=cmd_create)

    query = sub.add_parser("query", help="query existing graph artifacts")
    query.add_argument("--repo", required=True, help="repo path or known alias")
    query.add_argument("query", help="query text")
    query.add_argument("--limit", type=int, default=10)
    query.add_argument("--json", action="store_true")
    query.add_argument("--no-auto-install-skills", action="store_true", help="only report missing dependent skills")
    query.set_defaults(func=cmd_query)

    ensure = sub.add_parser("ensure-skills", help="install missing kg-code dependent skills from known local sources")
    ensure.add_argument("--include-remote", action="store_true", help="also ensure remote-operation skills such as c250")
    ensure.add_argument("--check-only", action="store_true", help="report missing skills without installing them")
    ensure.add_argument("--json", action="store_true")
    ensure.set_defaults(func=cmd_ensure_skills)
    return parser


def cmd_ensure_skills(args: argparse.Namespace) -> int:
    extra = REMOTE_DEPENDENT_SKILLS if args.include_remote else []
    results = ensure_dependent_skills(extra=extra, install=not args.check_only)
    payload = {"codex_home": str(codex_home()), "results": results}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"CODEX_HOME: {payload['codex_home']}")
        for item in results:
            line = f"{item['skill']}: {item['status']}"
            if item.get("source"):
                line += f" from {item['source']}"
            if item.get("path"):
                line += f" -> {item['path']}"
            print(line)
    return 0 if all(item["status"] not in {"missing-source", "error"} for item in results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"kg-code error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
