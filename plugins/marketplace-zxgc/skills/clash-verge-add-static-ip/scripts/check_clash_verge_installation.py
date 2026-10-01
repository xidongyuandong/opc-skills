#!/usr/bin/env python3
"""Bounded read-only installation evidence. Never launch binaries or install software."""
import argparse
import json
import os
from pathlib import Path
import platform
import plistlib
import shutil
import stat
from xml.parsers.expat import ExpatError

SYSTEMS = {'Darwin', 'Windows', 'Linux'}
ARCHITECTURES = {'x86_64': 'x64', 'amd64': 'x64', 'arm64': 'arm64', 'aarch64': 'arm64'}
MACH_MAGICS = {b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca', b'\xca\xfe\xba\xbf'}


def candidate_paths(system):
    """Common install locations and PATH only; user supplies other locations explicitly."""
    home = Path.home()
    if system == 'Darwin':
        return [parent / name for parent in (Path('/Applications'), home / 'Applications')
                for name in ('Clash Verge.app', 'Clash Verge Rev.app')]
    paths = []
    if system == 'Windows':
        for variable in ('ProgramFiles', 'ProgramFiles(x86)', 'LOCALAPPDATA'):
            value = os.environ.get(variable)
            if value:
                for folder in ('Clash Verge', 'Clash Verge Rev', 'Programs/Clash Verge', 'Programs/Clash Verge Rev'):
                    paths.append(Path(value) / folder / 'clash-verge.exe')
        commands = ('clash-verge.exe',)
    else:
        paths = [Path('/usr/bin/clash-verge'), Path('/usr/local/bin/clash-verge'), Path('/opt/clash-verge/clash-verge')]
        commands = ('clash-verge',)
    for name in commands:
        found = shutil.which(name)
        if found:
            paths.append(Path(found))
    return paths


def native_binary(path, system):
    """Recognize a regular native binary, not a config directory or shell alias."""
    info = path.stat()  # Permission and other I/O failures must reach the caller.
    if not stat.S_ISREG(info.st_mode):
        return False
    if system != 'Windows' and not os.access(str(path), os.X_OK):
        raise PermissionError('application file is not executable')
    with path.open('rb') as stream:
        header = stream.read(64)
        if system == 'Windows':
            if len(header) != 64 or header[:2] != b'MZ':
                return False
            offset = int.from_bytes(header[60:64], 'little')
            if offset < 64 or offset > info.st_size - 4:
                return False
            stream.seek(offset)
            return stream.read(4) == b'PE\0\0'
        if system == 'Darwin':
            return len(header) >= 32 and header[:4] in MACH_MAGICS
        return len(header) >= 32 and header[:4] == b'\x7fELF'


def inspect_candidate(path, system):
    path = Path(path).expanduser()
    version = None
    if system == 'Darwin':
        if path.suffix.lower() != '.app' or not stat.S_ISDIR(path.stat().st_mode):
            return None
        with (path / 'Contents/Info.plist').open('rb') as stream:
            metadata = plistlib.load(stream)
        if not isinstance(metadata, dict):
            raise ValueError('invalid bundle metadata')
        if metadata.get('CFBundleIdentifier') not in (
                'io.github.clash-verge-rev.clash-verge-rev', 'io.github.clash-verge-rev',
                'io.github.clash-verge'):
            return None
        name = metadata.get('CFBundleExecutable')
        if not isinstance(name, str) or not name or name in {'.', '..'} or '/' in name or '\\' in name:
            raise ValueError('invalid bundle executable')
        executable = path / 'Contents/MacOS' / name
        version = metadata.get('CFBundleShortVersionString')
        if not isinstance(version, str):
            version = None
    else:
        executable = path
    if not native_binary(executable, system):
        return None
    return {'path': str(path), 'executable': str(executable), 'version': version,
            'basis': 'bundle_metadata_and_native_binary' if system == 'Darwin' else 'candidate_native_binary',
            'bundle_identifier_matched': system == 'Darwin', 'identity_verified': False, 'signature_verified': False}


def probe(system=None, machine=None, app_path=None):
    system = system or platform.system()
    machine = machine or platform.machine()
    result = {'status': 'unknown', 'platform': system, 'architecture': ARCHITECTURES.get(machine.lower()),
              'architecture_raw': machine, 'evidence': [], 'issues': [],
              'launch_check': 'not_performed', 'scope': 'common_locations_and_PATH',
              'dependencies': {}, 'next_action': 'ask_for_installation_details'}
    for name in ('ruby', 'node'):
        try:
            result['dependencies'][name] = 'found' if shutil.which(name) else 'not_found'
        except OSError:
            result['dependencies'][name] = 'unknown'
    if system not in SYSTEMS or result['architecture'] is None:
        result['issues'].append({'reason': 'unsupported_platform_or_architecture'})
        return result
    try:
        candidates = candidate_paths(system)
    except OSError:
        candidates = []
        result['issues'].append({'reason': 'discovery_unavailable'})
    if app_path:
        custom = Path(app_path).expanduser()
        if not custom.is_absolute():
            result['issues'].append({'reason': 'app_path_must_be_absolute'})
            return result
        candidates = [custom]  # An explicit path must not fall back to another installation.
        result['scope'] = 'user_supplied_path'
    for path in dict.fromkeys(map(Path, candidates)):
        try:
            evidence = inspect_candidate(path, system)
            if evidence:
                result['evidence'].append(evidence)
            elif app_path:
                result['issues'].append({'path': str(path), 'reason': 'unverified_app_path'})
        except FileNotFoundError:
            if app_path:
                result['issues'].append({'path': str(path), 'reason': 'app_path_not_found'})
        except (OSError, ValueError, plistlib.InvalidFileException, ExpatError):
            result['issues'].append({'path': str(path), 'reason': 'inspection_unavailable'})
    if result['evidence']:
        result['status'] = 'installed'
        result['next_action'] = 'verify_identity_and_open_app_then_collect_profile'
    elif not result['issues']:
        result['status'] = 'not_found'
        result['next_action'] = 'ask_custom_location_or_offer_official_installation'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--app-path', help='Absolute path to an application bundle (macOS) or executable (Windows/Linux)')
    args = parser.parse_args()
    print(json.dumps(probe(app_path=args.app_path), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
