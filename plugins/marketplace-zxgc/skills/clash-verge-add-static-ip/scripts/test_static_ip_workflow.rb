#!/usr/bin/env ruby
# frozen_string_literal: true

require "fileutils"
require "open3"
require "tmpdir"
require "yaml"

ROOT = File.expand_path("..", __dir__)
BUILD = File.join(__dir__, "build_static_ip_profile.rb")
VERIFY = File.join(__dir__, "verify_static_ip_profile.rb")
FAKE_SECRETS = %w[192.0.2.10 sample-user sample-password secret-token].freeze

def assert(condition, message)
  raise "FAIL: #{message}" unless condition
end

def run(*command)
  stdout, stderr, status = Open3.capture3(*command)
  [stdout, stderr, status]
end

def assert_redacted(stdout, stderr)
  combined = stdout + stderr
  FAKE_SECRETS.each do |secret|
    assert(!combined.include?(secret), "command output leaked a sensitive fixture value")
  end
end

Dir.mktmpdir("clash-static-ip-test") do |dir|
  reference = File.join(dir, "reference.yaml")
  target = File.join(dir, "target.yaml")
  candidate = File.join(dir, "candidate.yaml")
  invalid = File.join(dir, "invalid.yaml")
  invalid_output = File.join(dir, "invalid-output.yaml")
  missing_reference = File.join(dir, "missing-reference.yaml")

  File.write(reference, YAML.dump(
    "proxies" => [{
      "name" => "cliproxy-static",
      "type" => "socks5",
      "server" => FAKE_SECRETS[0],
      "port" => 1080,
      "username" => FAKE_SECRETS[1],
      "password" => FAKE_SECRETS[2],
      "token" => FAKE_SECRETS[3]
    }]
  ))
  File.write(target, YAML.dump(
    "proxies" => [{ "name" => "upstream-a", "type" => "socks5", "server" => "198.51.100.20", "port" => 1080 }],
    "proxy-groups" => [{ "name" => "🚀 Auto-Best", "type" => "select", "proxies" => ["upstream-a"] }],
    "rules" => ["DOMAIN-SUFFIX,example.com,DIRECT", "MATCH,DIRECT"]
  ))
  File.write(invalid, "dns:\n  nameserver: invalid: yaml\n")
  File.write(missing_reference, YAML.dump("proxies" => []))

  stdout, stderr, status = run(RbConfig.ruby, BUILD, "--reference", reference, "--target", target, "--output", candidate)
  assert(status.success?, "candidate build should succeed")
  assert(File.exist?(candidate), "candidate should be created")
  assert_redacted(stdout, stderr)

  stdout, stderr, status = run(RbConfig.ruby, VERIFY, "--profile", candidate)
  assert(status.success?, "candidate verification should succeed")
  assert(stdout.include?("PASS:"), "verifier should report PASS")
  assert_redacted(stdout, stderr)

  stdout, stderr, status = run(RbConfig.ruby, BUILD, "--reference", invalid, "--target", target, "--output", invalid_output)
  assert(!status.success?, "invalid YAML should fail")
  assert(!File.exist?(invalid_output), "invalid YAML must not create an output")
  assert(stderr.match?(/invalid YAML at line \d+/), "invalid YAML should report only its parser line")
  assert_redacted(stdout, stderr)

  stdout, stderr, status = run(RbConfig.ruby, BUILD, "--reference", missing_reference, "--target", target, "--output", invalid_output)
  assert(!status.success?, "missing static proxy should fail")
  assert(!File.exist?(invalid_output), "missing static proxy must not create an output")
  assert_redacted(stdout, stderr)

  applied = File.join(dir, "applied.yaml")
  FileUtils.cp(target, applied)
  stdout, stderr, status = run(RbConfig.ruby, BUILD, "--reference", reference, "--target", applied, "--apply")
  assert(status.success?, "apply should succeed")
  assert(Dir.glob("#{applied}.before-static-ip-*.bak").length == 1, "apply should create exactly one backup")
  assert_redacted(stdout, stderr)

  stdout, stderr, status = run(RbConfig.ruby, VERIFY, "--profile", applied)
  assert(status.success?, "applied profile should verify")
  assert_redacted(stdout, stderr)
end

puts "PASS: build, reject, backup, Ruby compatibility, and redaction regressions"
puts "Boundary: tests use synthetic YAML and do not modify or validate a live Clash Verge profile"
