"""Extract each gamestate type from a TI save file into its own JSON file.

Nations and their control points are further split into per-entity files
under extracted/nations/:
  - nations/{id}_{displayName}.json
  - nations/{nationId}_{cpId}_{displayName}.json

Usage:
    python scripts/extract_save_types.py <save_file> [output_dir]

Output dir defaults to .tic/extracted/ relative to the save file's location.
"""
import json
import re
import sys
from pathlib import Path


def safe_filename(name: str) -> str:
    """Strip characters that are invalid in filenames."""
    return re.sub(r'[\\/*?:"<>|]', "_", name).strip()


def get_game_date(gamestates: dict) -> str:
    """Extract the in-game date as YYYY-MM-DD from TITimeState."""
    entries = gamestates.get("PavonisInteractive.TerraInvicta.TITimeState", [])
    if not entries:
        return "unknown-date"
    dt = entries[0]["Value"].get("currentDateTime", {})
    year = dt.get("year", 0)
    month = dt.get("month", 0)
    day = dt.get("day", 0)
    return f"{year:04d}-{month:02d}-{day:02d}"


def extract_nations(
    nation_entries: list,
    cp_entries: list,
    output_dir: Path,
) -> None:
    """Split nations and their control points into per-nation files."""
    nations_dir = output_dir / "nations"
    nations_dir.mkdir(parents=True, exist_ok=True)

    # Index control points by nation ID for quick lookup
    cps_by_nation: dict[int, list] = {}
    for entry in cp_entries:
        nation_ref = entry["Value"].get("nation")
        if nation_ref is None:
            continue
        nation_id = nation_ref["value"]
        cps_by_nation.setdefault(nation_id, []).append(entry)

    nation_count = 0
    cp_count = 0

    for entry in nation_entries:
        nation_id: int = entry["Key"]["value"]
        display_name: str = entry["Value"].get("displayName") or entry["Value"].get("templateName") or str(nation_id)
        safe_name = safe_filename(display_name)

        # Write nation file
        nation_file = nations_dir / f"{nation_id}_{safe_name}.json"
        with nation_file.open("w", encoding="utf-8") as f:
            json.dump(entry, f, indent=2)
        nation_count += 1

        # Write per-CP files for this nation
        for cp_entry in cps_by_nation.get(nation_id, []):
            cp_id: int = cp_entry["Key"]["value"]
            cp_display: str = cp_entry["Value"].get("displayName") or str(cp_id)
            safe_cp_name = safe_filename(cp_display)
            cp_file = nations_dir / f"{nation_id}_{cp_id}_{safe_cp_name}.json"
            with cp_file.open("w", encoding="utf-8") as f:
                json.dump(cp_entry, f, indent=2)
            cp_count += 1

    print(f"  nations: {nation_count} nation files, {cp_count} control point files -> {nations_dir}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_save_types.py <save_file> [output_dir]")
        sys.exit(1)

    save_path = Path(sys.argv[1])
    if not save_path.exists():
        print(f"File not found: {save_path}")
        sys.exit(1)

    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else save_path.parent / "extracted"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading {save_path} ...")

    with save_path.open(encoding="utf-8-sig") as f:
        data = json.load(f)

    gamestates = data.get("gamestates", {})
    print(f"Found {len(gamestates)} gamestate types")

    game_date = get_game_date(gamestates)
    dated_dir = output_dir / game_date
    dated_dir.mkdir(parents=True, exist_ok=True)
    print(f"Game date: {game_date} -> {dated_dir}\n")

    nation_entries = []
    cp_entries = []

    for full_type, entries in gamestates.items():
        short_name = full_type.split(".")[-1]

        if short_name == "TINationState":
            nation_entries = entries
        elif short_name == "TIControlPoint":
            cp_entries = entries

        out_path = dated_dir / f"{short_name}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        print(f"  {short_name}: {len(entries)} entries -> {out_path.name}")

    if nation_entries:
        extract_nations(nation_entries, cp_entries, dated_dir)
    else:
        print("  WARNING: no TINationState found — skipping nation extraction")

    print(f"\nDone. Files written to {output_dir}")


if __name__ == "__main__":
    main()
