from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from app.core.env_loader import load_env_file, load_project_env, resolve_auth_loading_policy


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

    def test_load_project_env_can_exclude_auth_prefixes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / '.env').write_text(
                'export ANTHROPIC_AUTH_TOKEN=secret\n'
                'export SPEC_RUNTIME_PROVIDER=claude_code\n',
                encoding='utf-8',
            )
            original_token = os.environ.get('ANTHROPIC_AUTH_TOKEN')
            original_provider = os.environ.get('SPEC_RUNTIME_PROVIDER')
            try:
                os.environ.pop('ANTHROPIC_AUTH_TOKEN', None)
                os.environ.pop('SPEC_RUNTIME_PROVIDER', None)
                _, loaded = load_project_env(root, override=True, exclude_prefixes=('ANTHROPIC_',))
                self.assertNotIn('ANTHROPIC_AUTH_TOKEN', loaded)
                self.assertNotIn('ANTHROPIC_AUTH_TOKEN', os.environ)
                self.assertEqual(loaded['SPEC_RUNTIME_PROVIDER'], 'claude_code')
            finally:
                if original_token is None:
                    os.environ.pop('ANTHROPIC_AUTH_TOKEN', None)
                else:
                    os.environ['ANTHROPIC_AUTH_TOKEN'] = original_token
                if original_provider is None:
                    os.environ.pop('SPEC_RUNTIME_PROVIDER', None)
                else:
                    os.environ['SPEC_RUNTIME_PROVIDER'] = original_provider

    def test_resolve_auth_loading_policy_defaults_claude_code_to_cli_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / '.env').write_text('export SPEC_RUNTIME_PROVIDER=claude_code\n', encoding='utf-8')
            provider, excluded_prefixes = resolve_auth_loading_policy(root, None, 'auto')
            self.assertEqual(provider, 'claude_code')
            self.assertEqual(excluded_prefixes, ('ANTHROPIC_',))

    def test_resolve_auth_loading_policy_allows_explicit_env_auth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / '.env').write_text('export SPEC_RUNTIME_PROVIDER=claude_code\n', encoding='utf-8')
            provider, excluded_prefixes = resolve_auth_loading_policy(root, None, 'env')
            self.assertEqual(provider, 'claude_code')
            self.assertEqual(excluded_prefixes, ())


if __name__ == '__main__':
    unittest.main()
