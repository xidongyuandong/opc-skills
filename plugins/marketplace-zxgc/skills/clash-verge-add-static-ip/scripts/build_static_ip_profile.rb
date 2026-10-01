#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "optparse"
require "set"
require "time"
require "yaml"

STATIC_PROXY = "cliproxy-static"
STATIC_GROUP = "🌐 静态IP出口"
DIALER_GROUP = "🚀 Auto-Best"
SENSITIVE_KEYS = %w[server username password uuid token].freeze

def abort_with(message)
  warn "ERROR: #{message}"
  exit 1
end

def write_profile(path, config)
  directory = File.dirname(File.expand_path(path))
  abort_with("output directory does not exist") unless Dir.exist?(directory)
  File.write(path, YAML.dump(config))
rescue SystemCallError
  abort_with("unable to write output file")
end

def load_yaml(path)
  data = YAML.safe_load(File.read(path), permitted_classes: [], permitted_symbols: [], aliases: true)
  abort_with("#{path}: YAML root must be a mapping") unless data.is_a?(Hash)
  data
rescue Psych::SyntaxError => e
  abort_with("#{path}: invalid YAML at line #{e.line}")
rescue Errno::ENOENT
  abort_with("#{path}: file not found")
end

def named_items(config, key)
  value = config[key] || []
  abort_with("#{key} must be a list") unless value.is_a?(Array)
  value
end

options = { apply: false }
OptionParser.new do |parser|
  parser.banner = "Usage: build_static_ip_profile.rb --reference FILE --target FILE [--output FILE | --apply]"
  parser.on("--reference FILE") { |v| options[:reference] = v }
  parser.on("--target FILE") { |v| options[:target] = v }
  parser.on("--output FILE") { |v| options[:output] = v }
  parser.on("--apply") { options[:apply] = true }
end.parse!

abort_with("--reference is required") unless options[:reference]
abort_with("--target is required") unless options[:target]
abort_with("--output is required unless --apply is used") unless options[:apply] || options[:output]
abort_with("--output and --apply cannot be combined") if options[:apply] && options[:output]

reference = load_yaml(options[:reference])
target = load_yaml(options[:target])
reference_matches = named_items(reference, "proxies").select { |item| item.is_a?(Hash) && item["name"] == STATIC_PROXY }
abort_with("reference must contain exactly one #{STATIC_PROXY} proxy") unless reference_matches.length == 1

static_proxy = Marshal.load(Marshal.dump(reference_matches.first))
static_proxy["dialer-proxy"] = DIALER_GROUP
missing_auth = %w[type server port].reject { |key| static_proxy.key?(key) }
abort_with("static proxy is missing required fields: #{missing_auth.join(', ')}") unless missing_auth.empty?

proxies = named_items(target, "proxies").reject { |item| item.is_a?(Hash) && item["name"] == STATIC_PROXY }
proxies << static_proxy
target["proxies"] = proxies

groups = named_items(target, "proxy-groups")
abort_with("target does not contain dialer group #{DIALER_GROUP}") unless groups.any? { |g| g.is_a?(Hash) && g["name"] == DIALER_GROUP }
groups = groups.reject { |item| item.is_a?(Hash) && item["name"] == STATIC_GROUP }
groups << { "name" => STATIC_GROUP, "type" => "select", "proxies" => [STATIC_PROXY] }
target["proxy-groups"] = groups

rules = target["rules"] || []
abort_with("rules must be a list") unless rules.is_a?(Array)
rules = rules.reject { |rule| rule.to_s.match?(/\A\s*MATCH(?:-|,|\z)/i) }
rules << "MATCH,#{STATIC_GROUP}"
target["rules"] = rules

known_names = Set.new(proxies.map { |proxy| proxy["name"] if proxy.is_a?(Hash) }.compact)
known_names.merge(groups.map { |group| group["name"] if group.is_a?(Hash) }.compact)
builtins = Set.new(%w[DIRECT REJECT PASS COMPATIBLE])
groups.each do |group|
  next unless group.is_a?(Hash) && group["proxies"].is_a?(Array)
  missing = group["proxies"].reject { |member| known_names.include?(member) || builtins.include?(member) }
  abort_with("group #{group['name']} references missing members") unless missing.empty?
end
proxies.each do |proxy|
  next unless proxy.is_a?(Hash) && proxy["dialer-proxy"]
  abort_with("proxy #{proxy['name']} references a missing dialer") unless known_names.include?(proxy["dialer-proxy"])
end

output = options[:apply] ? options[:target] : options[:output]
if options[:apply]
  stamp = Time.now.strftime("%Y%m%d-%H%M%S")
  backup = "#{options[:target]}.before-static-ip-#{stamp}.bak"
  FileUtils.cp(options[:target], backup)
  puts "Backup created: #{backup}"
end

write_profile(output, target)
puts "Profile written: #{output}"
puts "Summary: static_proxy=present dialer_group=present static_group=present match_rules=1"
puts "Sensitive fields redacted: #{SENSITIVE_KEYS.join(',')}"
