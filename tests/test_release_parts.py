"""Legacy release setup lists in a fork must use the fork's copied release-parts assets."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("release_parts", ROOT / "scripts" / "release_parts.py")
release_parts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release_parts)


class MirrorReleaseUrls(unittest.TestCase):
    def test_legacy_upstream_part_urls_are_repointed_to_the_fork(self):
        source = (
            b"tag v2.1.0\\n"
            b"part " + b"a" * 64 + b" 5349210 app 1 1 "
            b"https://github.com/NotRexed/Hookshot/releases/download/builder-parts/HookshotBuilder-app-5e62e1658e5f.zip\\n"
        )
        expected = source.replace(
            b"https://github.com/NotRexed/Hookshot/releases/download/",
            b"https://github.com/ZuanCrisp/Zelda-OOT-Port/releases/download/",
        )
        self.assertEqual(
            release_parts.mirror_release_urls(source, "ZuanCrisp/Zelda-OOT-Port"),
            expected,
        )

    def test_unrelated_urls_and_lists_without_a_mirror_are_unchanged(self):
        source = b"https://example.invalid/file.zip\\nhttps://github.com/NotRexed/Hookshot/releases/tag/v2.1.0\\n"
        self.assertEqual(release_parts.mirror_release_urls(source, ""), source)
        self.assertEqual(
            release_parts.mirror_release_urls(source, "ZuanCrisp/Zelda-OOT-Port"),
            source,
        )


if ( __name__ == "__main__"):
    unittest.main()
