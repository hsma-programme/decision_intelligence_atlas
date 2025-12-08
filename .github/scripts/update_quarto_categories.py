#!/usr/bin/env python3
"""
Update the `options:` list for the dropdown whose `id` == "category"
by performing a minimal textual replacement (pure regex approach).

Environment variables:
  CSV_PATH      - path to CSV of categories (default: templates/packages_projects_tools_permitted_categories.csv)
  TEMPLATE_PATH - path to the GitHub issue template file to update
                  (default: .github/ISSUE_TEMPLATE/issue_template.yml)

Exits with:
  0 - success (may print "No changes required.")
  2 - CSV not found
  3 - no categories found in CSV
  4 - template not found
  5 - could not find appropriate dropdown block
"""

import os
import re
import sys
from pathlib import Path
from typing import List

import pandas as pd

CSV_PATH = os.environ.get(
    "CSV_PATH", "templates/packages_projects_tools_permitted_categories.csv"
)
TEMPLATE_PATH = os.environ.get(
    "TEMPLATE_PATH", ".github/ISSUE_TEMPLATE/1-new_package_project_tool_submission.yml"
)


def read_categories(csv_path: str) -> List[str]:
    p = Path(csv_path)
    if not p.exists():
        print(f"CSV not found at {csv_path}", file=sys.stderr)
        sys.exit(2)
    df = pd.read_csv(p, header=None, dtype=str)
    vals = []
    for col in df.columns:
        vals += df[col].dropna().astype(str).tolist()
    vals = [v.strip() for v in vals if v and v.strip() != ""]
    # dedupe preserving order
    seen = set()
    out = []
    for v in vals:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def build_options_block(indent: str, categories: List[str]) -> str:
    # indent is the whitespace string used before 'options:'
    lines = [f"{indent}options:\n"]
    for c in categories:
        lines.append(f"{indent}  - {c}\n")
    return "".join(lines)


def find_dropdown_blocks(text: str):
    """
    Yield tuples (block_start_idx, block_end_idx, block_text) for each
    top-level list item that contains "type: dropdown".
    We detect a list-item block by searching from a line that contains
    "^\s*-\s*type:\s*dropdown" until the next top-level "- " at same or lesser indent,
    or EOF.
    """
    # find all positions of "- type: dropdown"
    pattern = re.compile(
        r"(^[ \t]*-\s*[^:\n]*\btype\s*:\s*dropdown\b.*?$)",
        flags=re.MULTILINE | re.IGNORECASE,
    )
    for m in pattern.finditer(text):
        start = m.start()

        # Find end: look for next "- <something>:" that starts a new list item at column with <= indent
        # We'll search from m.end() onward for the next line that begins with "^[ \t]*- " and treat that as the end boundary.
        next_m = re.search(r"^[ \t]*-\s+", text[m.end() :], flags=re.MULTILINE)
        if next_m:
            end = m.end() + next_m.start()
        else:
            end = len(text)

        block_text = text[start:end]
        yield start, end, block_text


def replace_options_in_block(
    full_text: str,
    block_start: int,
    block_end: int,
    block_text: str,
    categories: List[str],
) -> str:
    """
    Replace or insert the options: block inside block_text and return the modified full text.
    """
    # Look for options: line inside the block (capture the exact indent used)
    options_re = re.compile(r"(^[ \t]*options:\s*$)", flags=re.MULTILINE)
    m_opt = options_re.search(block_text)
    if m_opt:
        # options line was found. compute absolute positions.
        options_abs_start = block_start + m_opt.start()
        # From that position, include options line + subsequent lines that begin with whitespace + '-'
        rest = full_text[options_abs_start:].splitlines(keepends=True)
        end_offset = 0
        # include options line
        end_offset += len(rest[0])
        for ln in rest[1:]:
            # stop when line doesn't look like a list item (leading whitespace then '- ')
            if re.match(r"^[ \t]*-\s+", ln):
                end_offset += len(ln)
            else:
                break
        options_abs_end = options_abs_start + end_offset

        # determine indent of options line
        indent_match = re.match(r"^([ \t]*)options:", rest[0])
        indent = indent_match.group(1) if indent_match else ""
        new_block_text = build_options_block(indent, categories)

        new_full_text = (
            full_text[:options_abs_start] + new_block_text + full_text[options_abs_end:]
        )
        return new_full_text
    else:
        # No options: line inside the block. We'll insert options at the end of the block
        # preserving indentation level of the block's items. Determine a sensible indent:
        # find indentation of the first non-empty line in the block after the initial '-'
        lines = block_text.splitlines(keepends=True)
        indent = ""
        # try to find a line like "    attributes:" or "    id:" to copy its indent
        for ln in lines[1:]:
            m = re.match(r"^([ \t]+)\S", ln)
            if m:
                indent = m.group(1)
                break
        # fallback to two spaces
        if indent == "":
            indent = "  "
        new_options_block = build_options_block(indent, categories)
        # insert before block_end (absolute index)
        new_full_text = (
            full_text[:block_end] + new_options_block + full_text[block_end:]
        )
        return new_full_text


def main():
    categories = read_categories(CSV_PATH)
    if not categories:
        print("No categories found in CSV; aborting.", file=sys.stderr)
        sys.exit(3)

    tpl_path = Path(TEMPLATE_PATH)
    if not tpl_path.exists():
        print(f"Template file not found at {TEMPLATE_PATH}", file=sys.stderr)
        sys.exit(4)

    full_text = tpl_path.read_text(encoding="utf-8")

    # iterate candidate dropdown blocks and find the one that contains id: category (allow optional quotes)
    found = False
    new_text = full_text
    for start, end, block in find_dropdown_blocks(full_text):
        # Check for id: category inside the block; allow quotes and whitespace
        if re.search(
            r'^\s*id\s*:\s*(?:["\']\s*category\s*["\']|category)\s*$',
            block,
            flags=re.MULTILINE,
        ):
            # This is our block. Replace its options
            new_text_candidate = replace_options_in_block(
                new_text, start, end, block, categories
            )
            # Only apply first match (should only be one id: category)
            new_text = new_text_candidate
            found = True
            break

    if not found:
        print(
            "Could not find a `- type: dropdown` block containing `id: category`.",
            file=sys.stderr,
        )
        sys.exit(5)

    if new_text == full_text:
        print("No changes required; template already up-to-date.")
        return

    tpl_path.write_text(new_text, encoding="utf-8")
    print(
        f"Updated template {TEMPLATE_PATH} with {len(categories)} categories from {CSV_PATH}"
    )


if __name__ == "__main__":
    main()
