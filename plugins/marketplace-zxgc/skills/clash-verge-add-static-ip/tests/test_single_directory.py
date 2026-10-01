"""Run the actual builders after copying this skill alone to a clean directory."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SingleDirectoryTests(unittest.TestCase):
    def test_core_regressions_in_isolation(self):
        self.assertIsNotNone(shutil.which('ruby'), 'Ruby is required for this regression')
        self.assertIsNotNone(shutil.which('node'), 'Node.js is required for this regression')
        self.assertFalse(any(p.is_symlink() for p in ROOT.rglob('*')), 'package must contain actual resources')
        with tempfile.TemporaryDirectory() as directory:
            isolated = Path(directory) / ROOT.name
            shutil.copytree(ROOT, isolated, ignore=shutil.ignore_patterns('__pycache__'))
            self.assertFalse((isolated.parent / 'clash-verge-static-ip').exists())
            for name in ['test_static_ip_workflow.rb', 'test_sidecar_workflow.rb']:
                run = subprocess.run(['ruby', str(isolated / 'scripts' / name)], cwd=directory, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == '__main__':
    unittest.main()
