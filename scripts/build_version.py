"""Describe a checkout's version for Windows and Linux development builds.

Use a reachable semantic-version tag when there is one. Forks whose snapshot history
does not carry the source tags use release-please's manifest version and an explicit
nightly suffix, so both platform artifacts and the updater agree on the same track.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_RE = re.compile(r"\d+\.\d+\.\d+(?:-rc\.\d+)?\Z")


def describe(root=ROOT):
    root = Path(root)
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "describe", "--tags", "--long", "--match", "v[0-9]*"],
            capture_output=True, text=True, timeout=20, check=False,
        )
    except (OSError, subprocess.SubprocessError):
        result = None
    if result and result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    with (root / ".release-please-manifest.json").open(encoding="utf-8") as f:
        manifest = json.load(f)
    version = manifest.get(".")
    if not isinstance(version, str) or not VERSION_RE.fullmatch(version):
        raise ValueError("manifest has no valid root semantic version")

    sha = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--short=8", "HEAD"],
        capture_output=True, text=True, timeout=20, check=True,
    ).stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{8,}", sha):
        raise ValueError("git returned an invalid short commit hash")
    return f"v{version}-0-g{sha}"


if __name__ == "__main__":
    print(describe())
