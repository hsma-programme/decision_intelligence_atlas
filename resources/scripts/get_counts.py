#!/usr/bin/env python3
"""
pre_render_counts_to_yaml.py

Writes counts of immediate subdirectories for mappings PLACEHOLDER=PATH into a YAML file
(default: data/generated_counts.yml). Does NOT edit .qmd files.

Usage (from project root):
  python scripts/get_counts.py \
    "__NUM_PROJECTS__=content/projects" \
    "__NUM_MODULES__=src/modules" \
    "__NUM_EXAMPLES__=examples"

Optional args:
  --out-file path    (default: resources/generated_counts.yml)
  --format [yaml|json]  (default: yaml)
  --verbose / --dry-run
"""

from pathlib import Path
import argparse, sys, json
from collections import OrderedDict

try:
    import yaml
except Exception:
    yaml = None


def count_dirs(path: Path):
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for p in path.iterdir() if p.is_dir() and not p.name.startswith("."))


def parse_mapping(s: str):
    if "=" not in s:
        raise ValueError("Mapping must be PLACEHOLDER=PATH")
    ph, p = s.split("=", 1)
    return ph.strip().strip('"').strip("'"), Path(p.strip().strip('"').strip("'"))


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument("mappings", nargs="+", help="PLACEHOLDER=PATH")
    p.add_argument(
        "--out-file",
        "-o",
        default="resources/generated_counts.yml",
        help="Output YAML/JSON file",
    )
    p.add_argument(
        "--format",
        choices=["yaml", "json"],
        default=None,
        help="Output format (default by file ext)",
    )
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", "-v", action="store_true")
    args = p.parse_args(argv)

    out = Path(args.out_file)
    out.parent.mkdir(parents=True, exist_ok=True)

    # decide format
    fmt = args.format or ("json" if out.suffix.lower() == ".json" else "yaml")

    results = OrderedDict()
    for mapping in args.mappings:
        placeholder, path = parse_mapping(mapping)
        cnt = count_dirs(path)
        # store under a clean key name: strip surrounding underscores for YAML keys
        key = placeholder.strip("_")
        results[key] = cnt
        if args.verbose or args.dry_run:
            print(f"[INFO] {placeholder} -> {path} = {cnt}")

    if args.dry_run:
        print("Dry run - not writing file. Values:", results)
        return 0

    if fmt == "json":
        out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    else:
        # prefer yaml safe_dump if available, otherwise simple fallback to JSON-ish YAML
        if yaml:
            out.write_text(
                yaml.safe_dump(dict(results), sort_keys=False), encoding="utf-8"
            )
        else:
            out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    if args.verbose:
        print(f"Wrote {out} ({fmt}) with contents:")
        print(out.read_text(encoding="utf-8"))

    print(f"Generated counts written to: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
