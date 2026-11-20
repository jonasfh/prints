#!/usr/bin/env python3
"""Build parameterized 3D exports from SolidCraft designs using deploy.yml manifests."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import jsonschema
import yaml

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas" / "deploy.schema.json"


def build_command_script(
    piece: dict[str, Any],
    formats: list[str],
    output_dir: Path,
    design_name: str,
    version: str,
) -> tuple[list[dict[str, Any]], list[Path]]:
    """Build the solidcraft-cli command list and expected output paths for one piece."""
    commands: list[dict[str, Any]] = []
    for param_name, param_expr in (piece.get("params") or {}).items():
        commands.append(
            {
                "command": "parameters.change",
                "params": {"name": str(param_name), "expression": str(param_expr)},
            }
        )

    body = piece.get("body")
    label = piece.get("label")
    name_parts = [design_name, str(version)]
    if body:
        name_parts.append(str(body))
    if label:
        name_parts.append(str(label))
    stem = "-".join(name_parts)

    exported_files: list[Path] = []
    for fmt in formats:
        ext = fmt.lstrip(".")
        out_path = (output_dir / f"{stem}.{ext}").resolve()
        export_params: dict[str, Any] = {"path": str(out_path), "format": ext}
        if body:
            export_params["bodies"] = [str(body)]
        commands.append({"command": "file.export", "params": export_params})
        exported_files.append(out_path)

    return commands, exported_files


def format_release_notes(
    name: str, version: str, rows: list[dict[str, Any]]
) -> str:
    """Render a Markdown summary table for GitHub Release notes."""
    lines = [
        f"## {name} v{version}",
        "",
        "| File | Body | Parameters |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        params_str = (
            ", ".join(f"`{k}={v}`" for k, v in row["params"].items())
            if row["params"]
            else "default"
        )
        body = row.get("body") or "all"
        lines.append(f"| `{row['file']}` | `{body}` | {params_str} |")
    lines.append("")
    return "\n".join(lines)


def build_manifest(manifest_path: Path, out_root: Path) -> dict[str, Any]:
    """Process a single deploy.yml manifest and run solidcraft-cli for each piece."""
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.validate(instance=manifest, schema=schema)
    name = str(manifest["name"])
    version = str(manifest["version"])
    source_path = (manifest_path.parent / manifest["source"]).resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Source design not found: {source_path}")

    default_formats = [str(f) for f in (manifest.get("formats") or ["stl"])]
    design_out_dir = (out_root / f"{name}-{version}").resolve()
    design_out_dir.mkdir(parents=True, exist_ok=True)

    all_files: list[Path] = []
    note_rows: list[dict[str, Any]] = []

    for piece in manifest.get("pieces") or []:
        piece_formats = [str(f) for f in (piece.get("formats") or default_formats)]
        commands, exported = build_command_script(
            piece=piece,
            formats=piece_formats,
            output_dir=design_out_dir,
            design_name=name,
            version=version,
        )
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", encoding="utf-8", delete=False
        ) as tmp:
            json.dump({"commands": commands}, tmp, indent=2)
            tmp_path = Path(tmp.name)

        try:
            subprocess.run(
                [
                    "solidcraft-cli",
                    "run",
                    str(tmp_path),
                    "--in",
                    str(source_path),
                    "--quiet",
                ],
                check=True,
            )
        finally:
            tmp_path.unlink(missing_ok=True)

        for out_file in exported:
            if not out_file.is_file():
                raise FileNotFoundError(f"Expected export not created: {out_file}")
            all_files.append(out_file)
            note_rows.append(
                {
                    "file": out_file.name,
                    "body": piece.get("body"),
                    "params": piece.get("params") or {},
                }
            )

    notes_path = design_out_dir / "release-notes.md"
    notes_path.write_text(
        format_release_notes(name, version, note_rows), encoding="utf-8"
    )

    return {
        "name": name,
        "version": version,
        "tag": f"{name}-v{version}",
        "dir": str(design_out_dir),
        "notes_file": str(notes_path),
        "files": [str(f) for f in all_files],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifests",
        nargs="+",
        type=Path,
        help="Paths to deploy.yml manifest files.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("dist"),
        help="Root output directory for exported meshes (default: dist).",
    )
    args = parser.parse_args(argv)

    builds = [build_manifest(m.resolve(), args.out_dir.resolve()) for m in args.manifests]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    summary_path = args.out_dir / "builds.json"
    summary_path.write_text(json.dumps(builds, indent=2), encoding="utf-8")

    for build in builds:
        print(f"Built {build['tag']}: {len(build['files'])} file(s) -> {build['dir']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
