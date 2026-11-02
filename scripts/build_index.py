#!/usr/bin/env python3
"""Build and validate index.json from models/*.json.

Usage:
  python scripts/build_index.py          # Builds and updates index.json
  python scripts/build_index.py --check  # Validates cards and checks index.json is up-to-date (for CI)
"""

from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"
INDEX_FILE = ROOT / "index.json"

REQUIRED_FIELDS = ("id", "name", "family", "target_architecture", "engine")


def validate_card(path: Path, data: dict) -> list[str]:
    errors = []
    for field in REQUIRED_FIELDS:
        val = data.get(field)
        if not val or not str(val).strip():
            errors.append(f"Missing or empty required field: '{field}'")

    req = data.get("requirements") or {}
    min_vram = req.get("vram_min_gb")
    if min_vram is not None and not isinstance(min_vram, (int, float)):
        errors.append(f"Invalid requirements.vram_min_gb: {min_vram}")

    return errors


def build_catalog() -> dict:
    if not MODELS_DIR.is_dir():
        print(f"Error: {MODELS_DIR} not found", file=sys.stderr)
        sys.exit(1)

    cards = sorted(MODELS_DIR.glob("*.json"))
    if not cards:
        print(f"Error: No JSON cards found in {MODELS_DIR}", file=sys.stderr)
        sys.exit(1)

    entries = []
    has_errors = False

    for card_path in cards:
        try:
            with open(card_path, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except Exception as e:
            print(f"ERROR reading {card_path.name}: {e}", file=sys.stderr)
            has_errors = True
            continue

        errors = validate_card(card_path, data)
        if errors:
            print(f"ERROR in {card_path.name}:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            has_errors = True
            continue

        req = data.get("requirements") or {}
        entry = {
            "id": data["id"],
            "name": str(data.get("name") or data["id"]).strip(),
            "family": str(data.get("family") or "").strip(),
            "target_architecture": str(data.get("target_architecture") or "").strip(),
            "pipeline": str(data.get("pipeline") or "text_to_image").strip(),
            "engine": str(data.get("engine") or "quantfunc").strip(),
            "engine_version": str(data.get("engine_version") or data.get("engine") or "quantfunc").strip(),
            "description": str(data.get("description") or "").strip(),
            "vram_min_gb": req.get("vram_min_gb", 8),
            "vram_recommended_gb": req.get("vram_recommended_gb", 16),
            "tags": list(data.get("tags") or []),
            "license": str(data.get("license") or "").strip(),
            "verified": True,
            "card_file": card_path.name,
        }
        entries.append(entry)

    if has_errors:
        print("\nCard validation failed. Please fix the errors above.", file=sys.stderr)
        sys.exit(1)

    # Sort entries deterministically by architecture and id
    entries.sort(key=lambda x: (x["target_architecture"], x["engine"], x["id"]))

    catalog = {
        "schema_version": 1,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(entries),
        "models": entries,
    }
    return catalog


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and validate LazySD-Models index.json")
    parser.add_argument("--check", action="store_true", help="Check that index.json matches cards without overwriting")
    args = parser.parse_args()

    catalog = build_catalog()
    new_json_str = json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if not INDEX_FILE.is_file():
            print("Error: index.json does not exist. Run without --check first.", file=sys.stderr)
            return 1
        with open(INDEX_FILE, "r", encoding="utf-8") as fp:
            existing = json.load(fp)
        # Compare content ignoring timestamp
        catalog_clean = dict(catalog)
        existing_clean = dict(existing)
        catalog_clean.pop("generated_at", None)
        existing_clean.pop("generated_at", None)
        if catalog_clean != existing_clean:
            print("Error: index.json is out-of-date with models/*.json. Run python scripts/build_index.py to rebuild.", file=sys.stderr)
            return 1
        print(f"OK: All {catalog['count']} cards valid and index.json is up-to-date.")
        return 0

    with open(INDEX_FILE, "w", encoding="utf-8") as fp:
        fp.write(new_json_str)

    print(f"Successfully generated {INDEX_FILE.name} with {catalog['count']} verified models.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
