"""Synthetic platform evidence; never inspect or launch the host application."""
import importlib.util
import plistlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check_clash_verge_installation.py'
spec = importlib.util.spec_from_file_location('installation_probe', SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def binary(self, name='clash-verge', windows=False):
        p = self.root / name
        data = bytearray(128)
        if windows:
            data[:2] = b'MZ'
            data[60:64] = (64).to_bytes(4, 'little')
            data[64:68] = b'PE\0\0'
        else:
            data[:4] = b'\x7fELF'
        p.write_bytes(data)
        p.chmod(0o700)
        return p

    def run_probe(self, system='Linux', machine='x86_64', candidates=(), app_path=None):
        with patch.object(probe, 'candidate_paths', return_value=list(candidates)), patch.object(probe.shutil, 'which', return_value=None):
            return probe.probe(system=system, machine=machine, app_path=app_path)

    def test_installed_but_not_running_linux(self):
        r = self.run_probe(candidates=[self.binary()])
        self.assertEqual(r['status'], 'installed')
        self.assertEqual(r['launch_check'], 'not_performed')
        self.assertEqual(r['dependencies']['ruby'], 'not_found')

    def test_windows_space_path(self):
        p = self.binary('Clash Verge.exe', windows=True)
        self.assertEqual(self.run_probe('Windows', 'AMD64', [p])['status'], 'installed')

    def test_macos_bundle_and_version(self):
        app = self.root / 'Clash Verge.app'
        binary = app / 'Contents/MacOS/clash-verge'
        binary.parent.mkdir(parents=True)
        binary.write_bytes(b'\xcf\xfa\xed\xfe' + bytes(128))
        binary.chmod(0o700)
        (app / 'Contents/Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': 'io.github.clash-verge-rev.clash-verge-rev', 'CFBundleExecutable': 'clash-verge', 'CFBundleShortVersionString': 'test-version'}))
        r = self.run_probe('Darwin', 'arm64', [app])
        self.assertEqual(r['status'], 'installed')
        self.assertEqual(r['evidence'][0]['version'], 'test-version')
        self.assertFalse(r['evidence'][0]['identity_verified'])
        self.assertTrue(r['evidence'][0]['bundle_identifier_matched'])

    def test_residual_directory_not_installed(self):
        old = self.root / 'clash-verge'
        old.mkdir()
        self.assertEqual(self.run_probe(candidates=[old])['status'], 'not_found')

    def test_empty_or_unrelated_file_not_installed(self):
        p = self.root / 'clash-verge'
        p.write_text('not an application')
        p.chmod(0o700)
        self.assertEqual(self.run_probe(candidates=[p])['status'], 'not_found')

    def test_permission_denied_is_unknown(self):
        with patch.object(probe, 'inspect_candidate', side_effect=PermissionError):
            self.assertEqual(self.run_probe(candidates=[self.root / 'app'])['status'], 'unknown')

    def test_custom_path_and_no_launch(self):
        p = self.binary('custom app')
        with patch('subprocess.run', side_effect=AssertionError('must not execute')):
            self.assertEqual(self.run_probe(app_path=str(p))['status'], 'installed')

    def test_custom_missing_path_is_unknown(self):
        self.assertEqual(self.run_probe(app_path=str(self.root / 'missing'))['status'], 'unknown')

    def test_unknown_platform_and_architecture(self):
        self.assertEqual(self.run_probe('Plan9')['status'], 'unknown')
        self.assertEqual(self.run_probe(machine='mystery')['status'], 'unknown')

    def test_recheck_does_not_assume_install_succeeded(self):
        self.assertEqual(self.run_probe()['status'], 'not_found')
        self.assertEqual(self.run_probe()['status'], 'not_found')
        p = self.binary()
        self.assertEqual(self.run_probe(candidates=[p])['status'], 'installed')

    def test_discovery_errors_are_unknown(self):
        with patch.object(probe, 'candidate_paths', side_effect=OSError):
            self.assertEqual(probe.probe(system='Linux', machine='x86_64')['status'], 'unknown')

    def test_malformed_macos_plist_is_unknown(self):
        app = self.root / 'Clash Verge.app'
        (app / 'Contents').mkdir(parents=True)
        (app / 'Contents/Info.plist').write_bytes(b'<?xml version="1.0"?><plist><dict>')
        result = self.run_probe('Darwin', 'arm64', [app])
        self.assertEqual(result['status'], 'unknown')
        self.assertEqual(result['issues'][0]['reason'], 'inspection_unavailable')

    def test_macos_plist_cannot_escape_bundle(self):
        app = self.root / 'Clash Verge.app'
        (app / 'Contents').mkdir(parents=True)
        (app / 'Contents/Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier': 'io.github.clash-verge-rev.clash-verge-rev', 'CFBundleExecutable': '../../../outside'}))
        self.assertEqual(self.run_probe('Darwin', 'arm64', [app])['status'], 'unknown')


if __name__ == '__main__':
    unittest.main()
