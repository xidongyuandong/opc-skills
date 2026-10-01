#!/usr/bin/env ruby
# frozen_string_literal: true

require "open3"
require "optparse"
require "yaml"

STATIC_PROXY = "cliproxy-static"
STATIC_GROUP = "🌐 静态IP出口"
DIALER_GROUP = "🚀 Auto-Best"

def fail_check(errors, message)
  errors << message
end

options = {}
OptionParser.new do |parser|
  parser.banner = "Usage: verify_static_ip_profile.rb --profile FILE [--mihomo-bin FILE]"
  parser.on("--profile FILE") { |v| options[:profile] = v }
  parser.on("--mihomo-bin FILE") { |v| options[:mihomo] = v }
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
rules = config["rules"].is_a?(Array) ? config["rules"] : []

static_proxies = proxies.select { |p| p.is_a?(Hash) && p["name"] == STATIC_PROXY }
fail_check(errors, "#{STATIC_PROXY} must appear exactly once") unless static_proxies.length == 1
if static_proxies.length == 1
  fail_check(errors, "#{STATIC_PROXY} dialer-proxy must be #{DIALER_GROUP}") unless static_proxies.first["dialer-proxy"] == DIALER_GROUP
end

static_groups = groups.select { |g| g.is_a?(Hash) && g["name"] == STATIC_GROUP }
fail_check(errors, "#{STATIC_GROUP} must appear exactly once") unless static_groups.length == 1
if static_groups.length == 1
  fail_check(errors, "#{STATIC_GROUP} must contain only #{STATIC_PROXY}") unless static_groups.first["proxies"] == [STATIC_PROXY]
end

match_rules = rules.select { |r| r.to_s.match?(/\A\s*MATCH(?:-|,|\z)/i) }
fail_check(errors, "there must be exactly one MATCH rule") unless match_rules == ["MATCH,#{STATIC_GROUP}"]
fail_check(errors, "MATCH rule must be last") unless rules.last == "MATCH,#{STATIC_GROUP}"

proxy_names = proxies.map { |p| p["name"] if p.is_a?(Hash) }.compact.each_with_object({}) { |name, memo| memo[name] = true }
group_names = groups.map { |g| g["name"] if g.is_a?(Hash) }.compact.each_with_object({}) { |name, memo| memo[name] = true }
known_names = proxy_names.merge(group_names)
groups.each do |group|
  next unless group.is_a?(Hash) && group["proxies"].is_a?(Array)
  group["proxies"].each do |member|
    next if known_names[member] || %w[DIRECT REJECT PASS COMPATIBLE].include?(member)
    fail_check(errors, "group #{group['name']} references missing member #{member}")
  end
end
proxies.each do |proxy|
  next unless proxy.is_a?(Hash) && proxy["dialer-proxy"]
  fail_check(errors, "proxy #{proxy['name']} references missing dialer #{proxy['dialer-proxy']}") unless known_names[proxy["dialer-proxy"]]
end

if options[:mihomo]
  stdout, stderr, status = Open3.capture3(options[:mihomo], "-t", "-f", options[:profile])
  fail_check(errors, "mihomo syntax check failed: #{(stderr.empty? ? stdout : stderr).lines.first.to_s.strip}") unless status.success?
end

unless errors.empty?
  errors.each { |error| warn "FAIL: #{error}" }
  exit 1
end

puts "PASS: static route structure is internally consistent"
puts "Summary: proxies=#{proxies.length} groups=#{groups.length} rules=#{rules.length} match_rules=1"
puts "Boundary: this does not prove runtime selection, external IP identity, persistence, or long-term IP stability"
