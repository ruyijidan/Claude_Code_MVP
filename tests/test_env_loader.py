from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from app.core.env_loader import load_env_file, load_project_env


class EnvLoaderTests(unittest.TestCase):
    def test_load_env_file_supports_export_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            env_path = Path(tmp_dir) / '.env'
            env_path.write_text(
                'export ANTHROPIC_BASE_URL="https://example.test"\n'
                'export ANTHROPIC_MODEL=glm-5\n',
                encoding='utf-8',
            )
            loaded = load_env_file(env_path, override=True)
            self.assertEqual(loaded['ANTHROPIC_BASE_URL'], 'https://example.test')
            self.assertEqual(os.environ['ANTHROPIC_MODEL'], 'glm-5')

    def test_load_project_env_walks_up_parent_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            nested = root / 'a' / 'b'
            nested.mkdir(parents=True)
            (root / '.env').write_text('export ANTHROPIC_MODEL=glm-5\n', encoding='utf-8')
            env_path, loaded = load_project_env(nested, override=True)
            self.assertEqual(env_path, root / '.env')
            self.assertEqual(loaded['ANTHROPIC_MODEL'], 'glm-5')


if __name__ == '__main__':
    unittest.main()
