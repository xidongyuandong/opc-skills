#!/usr/bin/env ruby
# frozen_string_literal: true

require "open3"
require "optparse"
require "yaml"

options = {
  static_proxy_name: "cliproxy-static",
  auto_group_name: "auto-best",
  static_group_name: "🌐 静态IP出口",
  entry_group_name: "Proxy"
}
OptionParser.new do |parser|
  parser.banner = "Usage: verify_sidecar_profile.rb --profile FILE [options]"
  parser.on("--profile FILE") { |value| options[:profile] = value }
  parser.on("--static-proxy-name NAME") { |value| options[:static_proxy_name] = value }
  parser.on("--auto-group-name NAME") { |value| options[:auto_group_name] = value }
  parser.on("--static-group-name NAME") { |value| options[:static_group_name] = value }
  parser.on("--entry-group-name NAME") { |value| options[:entry_group_name] = value }
  parser.on("--mihomo-bin FILE") { |value| options[:mihomo] = value }
end.parse!
abort "ERROR: --profile is required" unless options[:profile]

begin
  config = YAML.safe_load(File.read(options[:profile]), permitted_classes: [], permitted_symbols: [], aliases: true)
rescue Psych::SyntaxError => e
  abort "ERROR: #{options[:profile]}: invalid YAML at line #{e.line}"
rescue Errno::ENOENT
  abort "ERROR: #{options[:profile]}: file not found"
end
abort "ERROR: YAML root must be a mapping" unless config.is_a?(Hash)

errors = []
proxies = config["proxies"].is_a?(Array) ? config["proxies"] : []
groups = config["proxy-groups"].is_a?(Array) ? config["proxy-groups"] : []
static_proxies = proxies.select { |proxy| proxy.is_a?(Hash) && proxy["name"] == options[:static_proxy_name] }
auto_groups = groups.select { |group| group.is_a?(Hash) && group["name"] == options[:auto_group_name] }
static_groups = groups.select { |group| group.is_a?(Hash) && group["name"] == options[:static_group_name] }
entry_groups = groups.select { |group| group.is_a?(Hash) && group["name"] == options[:entry_group_name] }

errors << "static proxy must appear exactly once" unless static_proxies.length == 1
errors << "Auto-Best group must appear exactly once" unless auto_groups.length == 1
errors << "static exit group must appear exactly once" unless static_groups.length == 1
errors << "entry group must appear exactly once" unless entry_groups.length == 1
if static_proxies.length == 1 && static_proxies.first["dialer-proxy"] != options[:auto_group_name]
  errors << "static proxy dialer-proxy must point to Auto-Best"
end
if auto_groups.length == 1
  members = auto_groups.first["proxies"]
  errors << "Auto-Best must contain at least one upstream proxy" unless members.is_a?(Array) && !members.empty?
end
if static_groups.length == 1 && static_groups.first["proxies"] != [options[:static_proxy_name]]
  errors << "static exit group must contain only the static proxy"
end
if entry_groups.length == 1
  members = entry_groups.first["proxies"]
  unless members.is_a?(Array) && members.include?(options[:static_group_name]) && members.include?(options[:auto_group_name])
    errors << "entry group must contain both static exit and Auto-Best"
  end
end

known = proxies.map { |proxy| proxy["name"] if proxy.is_a?(Hash) }.compact
known += groups.map { |group| group["name"] if group.is_a?(Hash) }.compact
builtins = %w[DIRECT REJECT PASS COMPATIBLE]
groups.each do |group|
  next unless group.is_a?(Hash) && group["proxies"].is_a?(Array)
  missing = group["proxies"].reject { |member| known.include?(member) || builtins.include?(member) }
  errors << "group #{group['name']} references missing members" unless missing.empty?
end

if options[:mihomo]
  stdout, stderr, status = Open3.capture3(options[:mihomo], "-t", "-f", options[:profile])
  errors << "mihomo syntax check failed: #{(stderr.empty? ? stdout : stderr).lines.first.to_s.strip}" unless status.success?
end

unless errors.empty?
  errors.each { |error| warn "FAIL: #{error}" }
  exit 1
end

puts "PASS: sidecar-composed static route structure is internally consistent"
puts "Summary: proxies=#{proxies.length} groups=#{groups.length} auto_candidates=#{auto_groups.first['proxies'].length}"
puts "Boundary: this does not prove runtime selection, external IP identity, update/restart persistence, TUN coverage, or long-term IP stability"
