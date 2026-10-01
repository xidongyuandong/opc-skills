#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "optparse"
require "yaml"

def abort_with(message)
  warn "ERROR: #{message}"
  exit 1
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

options = {
  proxy_name: "cliproxy-static",
  auto_group_name: "auto-best",
  static_group_name: "🌐 静态IP出口",
  entry_group_name: "Proxy",
  health_check_url: "https://www.gstatic.com/generate_204",
  interval: 120,
  tolerance: 50,
  exclude_regex: "",
  force: false
}

OptionParser.new do |parser|
  parser.banner = "Usage: build_static_ip_sidecar.rb --reference FILE --output FILE [options]"
  parser.on("--reference FILE") { |value| options[:reference] = value }
  parser.on("--output FILE") { |value| options[:output] = value }
  parser.on("--proxy-name NAME") { |value| options[:proxy_name] = value }
  parser.on("--auto-group-name NAME") { |value| options[:auto_group_name] = value }
  parser.on("--static-group-name NAME") { |value| options[:static_group_name] = value }
  parser.on("--entry-group-name NAME") { |value| options[:entry_group_name] = value }
  parser.on("--health-check-url URL") { |value| options[:health_check_url] = value }
  parser.on("--interval SECONDS", Integer) { |value| options[:interval] = value }
  parser.on("--tolerance MILLISECONDS", Integer) { |value| options[:tolerance] = value }
  parser.on("--exclude-regex REGEX") { |value| options[:exclude_regex] = value }
  parser.on("--force") { options[:force] = true }
end.parse!

abort_with("--reference is required") unless options[:reference]
abort_with("--output is required") unless options[:output]
abort_with("interval must be positive") unless options[:interval].positive?
abort_with("tolerance must be non-negative") if options[:tolerance].negative?

reference = load_yaml(options[:reference])
proxies = reference["proxies"]
abort_with("reference proxies must be a list") unless proxies.is_a?(Array)
matches = proxies.select { |proxy| proxy.is_a?(Hash) && proxy["name"] == options[:proxy_name] }
abort_with("reference must contain exactly one #{options[:proxy_name]} proxy") unless matches.length == 1

custom_proxy = Marshal.load(Marshal.dump(matches.first))
required = %w[name type server port]
missing = required.reject { |key| custom_proxy.key?(key) }
abort_with("static proxy is missing required fields: #{missing.join(', ')}") unless missing.empty?
custom_proxy["dialer-proxy"] = options[:auto_group_name]

begin
  Regexp.new(options[:exclude_regex], Regexp::IGNORECASE) unless options[:exclude_regex].empty?
rescue RegexpError
  abort_with("--exclude-regex is invalid")
end

output = File.expand_path(options[:output])
abort_with("output already exists; use --force after review") if File.exist?(output) && !options[:force]
abort_with("output directory does not exist") unless Dir.exist?(File.dirname(output))

template_path = File.expand_path("../assets/static_ip_sidecar.js.tmpl", __dir__)
template = File.read(template_path)
sidecar_options = {
  "staticProxyName" => options[:proxy_name],
  "autoGroupName" => options[:auto_group_name],
  "staticGroupName" => options[:static_group_name],
  "entryGroupName" => options[:entry_group_name],
  "healthCheckUrl" => options[:health_check_url],
  "interval" => options[:interval],
  "tolerance" => options[:tolerance],
  "excludeRegex" => options[:exclude_regex]
}
content = template.sub("__CUSTOM_PROXY_JSON__", JSON.generate(custom_proxy))
content = content.sub("__OPTIONS_JSON__", JSON.generate(sidecar_options))
abort_with("template rendering left unresolved placeholders") if content.include?("__CUSTOM_PROXY_JSON__") || content.include?("__OPTIONS_JSON__")

File.write(output, content)
File.chmod(0o600, output)
puts "Sidecar written: #{output}"
puts "Summary: static_proxy=#{options[:proxy_name]} auto_group=#{options[:auto_group_name]} static_group=#{options[:static_group_name]}"
puts "Sensitive fields are stored only in the selected sidecar output and are not printed"
