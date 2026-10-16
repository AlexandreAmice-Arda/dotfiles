"""A failed source verification must leave the selected desktop stack usable."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE_ROOT = Path(__file__).resolve().parents[1]


class SwayStackTests(unittest.TestCase):
    def test_corrupted_download_does_not_activate_or_mark_stack_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            (root / 'packages').mkdir()
            shutil.copy2(SOURCE_ROOT / 'scripts/install-sway-stack', root / 'scripts')
            shutil.copy2(SOURCE_ROOT / 'packages/sway-stack-sources.tsv', root / 'packages')
            home = root / 'home'
            stack_root = home / '.local/lib/sway-stack'
            old_stack = stack_root / 'old'
            old_stack.mkdir(parents=True)
            (stack_root / 'current').symlink_to(old_stack)
            mock_bin = root / 'bin'
            mock_bin.mkdir()
            (mock_bin / 'dpkg-query').write_text('#!/bin/sh\nprintf "ii "\n')
            (mock_bin / 'dpkg-query').chmod(0o755)
            (mock_bin / 'curl').write_text(
                f'#!{sys.executable}\nimport sys\nfrom pathlib import Path\n'
                'Path(sys.argv[sys.argv.index("--output") + 1]).write_bytes(b"bad archive")\n')
            (mock_bin / 'curl').chmod(0o755)
            env = os.environ.copy()
            env.update(HOME=str(home), PATH=f'{mock_bin}:/usr/bin:/bin')
            result = subprocess.run(['/bin/sh', str(root / 'scripts/install-sway-stack')],
                                    env=env, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('wayland source checksum failed', result.stderr)
            self.assertEqual((stack_root / 'current').resolve(), old_stack)
            self.assertFalse((stack_root / '1.11/ready').exists())


if __name__ == '__main__':
    unittest.main()
