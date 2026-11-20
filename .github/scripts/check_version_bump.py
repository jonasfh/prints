#!/usr/bin/env python3
"""Verify that modified designs bump their SemVer version in deploy.yml."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

import yaml

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


def parse_semver(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.match(version.strip())
    if not match:
        raise ValueError(f"Invalid SemVer version: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def git_show_file(rev: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Base git revision/SHA.")
    parser.add_argument("manifests", nargs="+", type=Path, help="Changed deploy.yml paths.")
    args = parser.parse_args(argv)

    failed = False
    for manifest_path in args.manifests:
        head_data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        head_ver = str(head_data["version"])

        base_text = git_show_file(args.base, manifest_path.as_posix())
        if base_text is None:
            print(f"OK (new): {manifest_path} @ {head_ver}")
            continue

        base_data = yaml.safe_load(base_text)
        base_ver = str(base_data["version"])

        if parse_semver(head_ver) <= parse_semver(base_ver):
            print(
                f"ERROR: {manifest_path} was modified, but version ({head_ver}) "
                f"was not bumped above base version ({base_ver}).",
                file=sys.stderr,
            )
            failed = True
        else:
            print(f"OK: {manifest_path} bumped {base_ver} -> {head_ver}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
