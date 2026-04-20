"""Validate QMD category metadata against the permitted category list."""

from pathlib import Path
import sys
import yaml


CATEGORIES_CSV = Path(
    "templates/packages_projects_tools_permitted_categories.csv"
)
QMD_ROOT = Path("packages_projects_tools")


def load_categories(path):
    """
    Return the set of allowed categories.

    Parameters
    ----------
    path : pathlib.Path
        Path to the text file containing one category per line.

    Returns
    -------
    set of str
        Set of category names after stripping whitespace and skipping
        empty lines.
    """
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def extract_front_matter(text):
    """
    Extract YAML front matter from a QMD file.

    Parameters
    ----------
    text : str
        Full text content of the QMD file.

    Returns
    -------
    str or None
        The YAML front-matter block (without the delimiters) if present
        and well-formed, otherwise `None`.
    """
    if not text.startswith("---\n"):
        return None

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    return parts[1]


def main():
    """
    Validate category metadata in QMD files against the allowed list.

    Scans QMD files under `QMD_ROOT`, parses YAML front matter, and
    checks that each value in the `categories` field appears in
    `CATEGORIES_CSV`. Prints any validation problems and exits with a
    non-zero status if invalid YAML or disallowed categories are found.
    """
    allowed_categories = load_categories(CATEGORIES_CSV)
    problems = []

    for path in Path(QMD_ROOT).rglob("*.qmd"):
        # skip generated/output dirs if needed
        if any(part in {"_site", ".quarto", ".git"} for part in path.parts):
            continue

        text = path.read_text(encoding="utf-8")
        front_matter = extract_front_matter(text)
        if not front_matter:
            continue

        try:
            meta = yaml.safe_load(front_matter) or {}
        except Exception as e:
            problems.append(f"{path}: invalid YAML front matter ({e})")
            continue

        categories = meta.get("categories", [])
        if categories is None:
            categories = []
        if not isinstance(categories, list):
            problems.append(f"{path}: categories must be a list")
            continue

        bad = [c for c in categories if c not in allowed_categories]
        if bad:
            problems.append(f"{path}: invalid categories {bad} ")

    if problems:
        print("Category validation failed:\n")
        for p in problems:
            print(f"- {p}")
        print("")
        print(f"Allowed: {sorted(allowed_categories)})")
        sys.exit(1)

    print("All categories are valid.")


if __name__ == "__main__":
    main()
