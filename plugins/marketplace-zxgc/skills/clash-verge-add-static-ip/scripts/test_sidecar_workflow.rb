#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "json"
require "open3"
require "rbconfig"
require "tmpdir"
require "yaml"

BUILD = File.join(__dir__, "build_static_ip_sidecar.rb")
VERIFY = File.join(__dir__, "verify_sidecar_profile.rb")
FAKE_SECRETS = %w[192.0.2.44 sample-user sample-password].freeze

def assert(condition, message)
  raise "FAIL: #{message}" unless condition
end

def run(*command)
  Open3.capture3(*command)
end

def assert_redacted(stdout, stderr)
  FAKE_SECRETS.each do |secret|
    assert(!(stdout + stderr).include?(secret), "command output leaked a synthetic credential")
  end
end

node = `command -v node`.strip
abort "ERROR: node is required for the sidecar behavior regression" if node.empty?

Dir.mktmpdir("clash-sidecar-test") do |dir|
  reference = File.join(dir, "reference.yaml")
  sidecar = File.join(dir, "sidecar.js")
  input = File.join(dir, "input.json")
  composed_json = File.join(dir, "composed.json")
  composed_yaml = File.join(dir, "composed.yaml")
  harness = File.join(dir, "harness.js")

  File.write(reference, YAML.dump("proxies" => [{
    "name" => "cliproxy-static", "type" => "socks5", "server" => FAKE_SECRETS[0],
    "port" => 443, "username" => FAKE_SECRETS[1], "password" => FAKE_SECRETS[2], "udp" => true
  }]))
  base = {
    "proxies" => [
      { "name" => "SG-A", "type" => "ss", "server" => "198.51.100.1", "port" => 443 },
      { "name" => "HK-A", "type" => "ss", "server" => "198.51.100.2", "port" => 443 }
    ],
    "proxy-groups" => [{ "name" => "Proxy", "type" => "select", "proxies" => ["SG-A", "HK-A"] }],
    "rules" => ["MATCH,Proxy"]
  }
  File.write(input, JSON.generate(base))

  stdout, stderr, status = run(RbConfig.ruby, BUILD, "--reference", reference, "--output", sidecar, "--exclude-regex", "HK")
  assert(status.success?, "sidecar build should succeed")
  assert_redacted(stdout, stderr)
  assert((File.stat(sidecar).mode & 0o777) == 0o600, "sidecar should be owner-readable only")
  assert(!File.read(sidecar).include?("__CUSTOM_PROXY_JSON__"), "sidecar must not contain template placeholders")

  _stdout, _stderr, status = run(node, "--check", sidecar)
  assert(status.success?, "generated sidecar JavaScript syntax should pass")

  File.write(harness, <<~JS)
    const fs = require("fs");
    const { main } = require(process.argv[2]);
    const input = JSON.parse(fs.readFileSync(process.argv[3], "utf8"));
    const once = main(input, "fixture");
    const twice = main(JSON.parse(JSON.stringify(once)), "fixture");
    fs.writeFileSync(process.argv[4], JSON.stringify(twice));
  JS
  _stdout, stderr, status = run(node, harness, sidecar, input, composed_json)
  assert(status.success?, "sidecar should execute twice: #{stderr.lines.first}")
  composed = JSON.parse(File.read(composed_json))
  assert(composed["proxies"].count { |proxy| proxy["name"] == "cliproxy-static" } == 1, "static proxy should be idempotent")
  auto = composed["proxy-groups"].find { |group| group["name"] == "auto-best" }
  assert(auto["proxies"] == ["SG-A"], "Auto-Best should rebuild from current eligible nodes")
  assert(composed["proxy-groups"].count { |group| group["name"] == "auto-best" } == 1, "Auto-Best should be idempotent")
  File.write(composed_yaml, YAML.dump(composed))

  stdout, stderr, status = run(RbConfig.ruby, VERIFY, "--profile", composed_yaml)
  assert(status.success?, "composed profile verification should succeed")
  assert_redacted(stdout, stderr)

  stdout, stderr, status = run(RbConfig.ruby, BUILD, "--reference", reference, "--output", sidecar)
  assert(!status.success?, "builder should refuse to overwrite without --force")
  assert_redacted(stdout, stderr)

  changed = Marshal.load(Marshal.dump(base))
  changed["proxies"] = [{ "name" => "US-B", "type" => "ss", "server" => "203.0.113.3", "port" => 443 }]
  changed["proxy-groups"][0]["proxies"] = ["US-B"]
  File.write(input, JSON.generate(changed))
  _stdout, stderr, status = run(node, harness, sidecar, input, composed_json)
  assert(status.success?, "sidecar should accept refreshed subscription nodes: #{stderr.lines.first}")
  refreshed = JSON.parse(File.read(composed_json))
  refreshed_auto = refreshed["proxy-groups"].find { |group| group["name"] == "auto-best" }
  assert(refreshed_auto["proxies"] == ["US-B"], "Auto-Best should follow refreshed subscription nodes")
end

puts "PASS: sidecar generation, redaction, syntax, idempotence, refresh rebuild, overwrite guard, and composed-profile verification"
puts "Boundary: tests use synthetic data and do not modify or prove a live Clash Verge GUI binding, runtime selection, external IP, or restart persistence"
