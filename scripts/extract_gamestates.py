#!/usr/bin/env python3
"""Extractor for Terra Invicta save gamestates.

Reads the `gamestates` mapping from a save JSON and writes one file per
top-level key. For parsed dict/list values the script optionally explodes
their entries into a subdirectory, naming subfiles using a display name
when present and falling back to templateName when display is missing.
"""

import argparse
import contextlib
import json
import re
from pathlib import Path
from typing import Any


def sanitize_name(s: str) -> str:
    """Return a filesystem-safe name by replacing unsafe chars with underscore."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", s)


def sanitize_display_name(s: str | None, max_len: int = 64) -> str:
    """Normalize a display string for use in filenames."""
    if not s:
        return ""
    s2 = re.sub(r"\s+", "_", str(s).strip())
    s2 = re.sub(r"[^A-Za-z0-9._-]", "_", s2)
    return (s2[:max_len]) if len(s2) > max_len else s2


def _write_value_file(
    out_dir: Path, filename: str, value_text: str
) -> tuple[Path, Any | None]:
    """Write value_text under out_dir/filename. Return (Path, parsed_or_None)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    if out_path.exists():
        i = 1
        base = out_path.stem
        ext = out_path.suffix
        while True:
            candidate = f"{base}_{i}{ext}"
            candidate_path = out_dir / candidate
            if not candidate_path.exists():
                out_path = candidate_path
                filename = candidate
                break
            i += 1
    parsed = None
    try:
        parsed = json.loads(value_text)
        with out_path.open("w", encoding="utf-8") as outf:
            json.dump(parsed, outf, indent=2, ensure_ascii=False)
    except Exception:
        with out_path.open("w", encoding="utf-8") as outf:
            outf.write(value_text)
    return out_path, parsed


def _compute_subkey(elem: object, idx: int) -> str:
    """Compute a stable subkey for list elements from common fields."""
    if not isinstance(elem, dict):
        return f"item_{idx}"
    key_field = elem.get("Key")
    if isinstance(key_field, dict):
        val = key_field.get("value")
        if isinstance(val, dict) and "value" in val:
            val = val.get("value")
        if val is not None:
            return str(val)
    elif key_field is not None:
        return str(key_field)
    value_field = elem.get("Value")
    if isinstance(value_field, dict):
        id_field = value_field.get("ID")
        if isinstance(id_field, dict):
            v = id_field.get("value")
            if v is not None:
                return str(v)
        elif id_field is not None:
            return str(id_field)
    return f"item_{idx}"


def _write_subval_file(subdir: Path, sub_filename: str, subval: object) -> str:
    """Write a sub-value JSON file into subdir, handling name collisions."""
    subdir.mkdir(parents=True, exist_ok=True)
    sub_path = subdir / sub_filename
    if sub_path.exists():
        i = 1
        base = sub_path.stem
        ext = sub_path.suffix
        while True:
            candidate = f"{base}_{i}{ext}"
            candidate_path = subdir / candidate
            if not candidate_path.exists():
                sub_filename = candidate
                sub_path = candidate_path
                break
            i += 1
    try:
        with sub_path.open("w", encoding="utf-8") as sf:
            json.dump(subval, sf, indent=2, ensure_ascii=False)
    except Exception:
        with sub_path.open("w", encoding="utf-8") as sf:
            sf.write(json.dumps(subval, ensure_ascii=False))
    return sub_filename


def _explode_parsed(
    parsed: object, out_dir: Path, short_key: str, manifest: dict
) -> None:
    """Explode a parsed dict/list into per-item files under out_dir/short_key."""
    if parsed is None or not isinstance(parsed, (dict, list)):
        return
    subdir = out_dir / short_key
    subdir.mkdir(parents=True, exist_ok=True)

    if isinstance(parsed, dict):
        iterator = list(parsed.items())
    else:
        iterator = [
            (_compute_subkey(elem, idx), elem) for idx, elem in enumerate(parsed)
        ]

    for subkey, subval in iterator:
        display = None
        if isinstance(subval, dict):
            value_block = subval.get("Value")
            display = (
                value_block.get("displayName")
                if isinstance(value_block, dict)
                else None
            )
            if not display:
                display = subval.get("displayName") or subval.get("DisplayName")
            if not display and isinstance(value_block, dict):
                display = value_block.get("DisplayName")
            if not display and isinstance(value_block, dict):
                display = value_block.get("templateName") or value_block.get(
                    "TemplateName"
                )
            if not display:
                display = subval.get("templateName") or subval.get("TemplateName")

        display_part = sanitize_display_name(display)
        base = sanitize_name(str(subkey))
        sub_filename = (
            f"{base}__{display_part}.json" if display_part else base + ".json"
        )

        final_name = _write_subval_file(subdir, sub_filename, subval)
        rel = f"{short_key}/{final_name}"
        manifest[f"{short_key}.{subkey}"] = rel


def extract_gamestates(src_path: str, out_dir: str) -> tuple[str, dict]:
    """Extract `gamestates` from src_path and write files into out_dir.

    Returns (manifest_path, manifest_dict).
    """
    out_dir_path = Path(out_dir)
    out_dir_path.mkdir(parents=True, exist_ok=True)
    manifest: dict = {}
    prefix = "PavonisInteractive.TerraInvicta."

    with Path(src_path).open(encoding="utf-8", errors="replace") as f:
        data = json.load(f)

    gamestates = data.get("gamestates") or {}
    for key, value in gamestates.items():
        key_unquoted = key
        short_key = (
            key_unquoted[len(prefix) :]
            if key_unquoted.startswith(prefix)
            else key_unquoted
        )

        filename_base = sanitize_name(short_key)
        filename = filename_base + ".json"

        value_text = json.dumps(value, ensure_ascii=False)
        out_path_obj, parsed = _write_value_file(out_dir_path, filename, value_text)

        manifest[short_key] = out_path_obj.name

        with contextlib.suppress(Exception):
            _explode_parsed(parsed, out_dir_path, short_key, manifest)

    manifest_path_obj = out_dir_path / "manifest.json"
    with manifest_path_obj.open("w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)
    return str(manifest_path_obj), manifest


def main() -> None:
    """CLI entrypoint for the extractor."""
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="Path to the save JSON file")
    ap.add_argument(
        "outdir", nargs="?", help="Output directory (defaults to package .tic)"
    )
    args = ap.parse_args()

    script_dir = Path(__file__).resolve().parent
    package_dir = script_dir.parent
    default_outdir = package_dir / ".tic"

    outdir = (
        default_outdir
        if args.outdir is None
        else (
            Path(args.outdir)
            if Path(args.outdir).is_absolute()
            else package_dir / args.outdir
        )
    )
    outdir = str(Path(outdir).resolve())

    manifest_path, manifest = extract_gamestates(args.source, outdir)
    print("Wrote manifest to", manifest_path)
    print("Extracted", len(manifest), "entries")


if __name__ == "__main__":
    main()
