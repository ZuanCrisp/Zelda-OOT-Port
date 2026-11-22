"""The shared Windows/Linux build-version fallback for forks without reachable version tags."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_version", ROOT / "scripts" / "build_version.py")
build_version = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_version)


class BuildVersion(unittest.TestCase):
    def test_uses_git_describe_when_a_version_tag_is_reachable(self):
        class Result:
            returncode = 0
            stdout = "v2.2.0-rc.1-57-g82885814\n"
        with patch.object(build_version.subprocess, "run", return_value=Result()):
            self.assertEqual(build_version.describe(ROOT), "v2.2.0-rc.1-57-g82885814")

    def test_manifest_fallback_is_a_nightly_and_keeps_commit_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".release-please-manifest.json").write_text(
                json.dumps({".": "2.2.0-rc.1"}), encoding="utf-8"
            )
            class NoTag:
                returncode = 128
                stdout = ""
            class Sha:
                stdout = "abcdef012345\n"
            with patch.object(build_version.subprocess, "run", side_effect=[NoTag(), Sha()]):
                self.assertEqual(build_version.describe(root), "v2.2.0-rc.1-0-gabcdef012345")

    def test_rejects_invalid_manifest_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".release-please-manifest.json").write_text(
                json.dumps({".": "unknown"}), encoding="utf-8"
            )
            class NoTag:
                returncode = 128
                stdout = ""
            with patch.object(build_version.subprocess, "run", return_value=NoTag()):
                with self.assertRaises(ValueError):
                    build_version.describe(root)


if __name__ == "__main__":
    unittest.main()
