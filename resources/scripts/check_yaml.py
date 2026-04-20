"""Validate QMD metadata against the permitted lists."""

from pathlib import Path
import sys
import yaml


CATEGORIES_CSV = Path(
    "templates/packages_projects_tools_permitted_categories.csv"
)
LANGUAGES_CSV = Path(
    "templates/packages_projects_tools_permitted_languages.csv"
)
QMD_ROOT = Path("packages_projects_tools")


def load_list(path):
    """
    Return the list of allowed options.

    Parameters
    ----------
    path : pathlib.Path
        Path to the CSV file containing one option per line.

    Returns
    -------
    set of str
        Set of options after stripping whitespace and empty lines.
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


def check_entries(field_name, allowed_path):
    """
    Validate a list-valued metadata field in QMD files.

    Parameters
    ----------
    field_name : str
        Name of the YAML field to validate.
    allowed_path : pathlib.Path
        Path to the file containing one allowed value per line.
    """
    allowed_values = load_list(allowed_path)
    problems = []

    for path in Path(QMD_ROOT).rglob("*.qmd"):
        text = path.read_text(encoding="utf-8")
        front_matter = extract_front_matter(text)
        if not front_matter:
            continue

        try:
            meta = yaml.safe_load(front_matter) or {}
        except Exception as e:
            problems.append(f"{path}: invalid YAML front matter ({e})")
            continue

        entries = meta.get(field_name, [])
        if entries is None:
            entries = []
        if not isinstance(entries, list):
            problems.append(f"{path}: {field_name} must be a list")
            continue

        bad = [entry for entry in entries if entry not in allowed_values]
        if bad:
            problems.append(f"{path}: invalid {field_name} {bad}")

    if problems:
        print(f"{field_name} validation failed:\n")
        for problem in problems:
            print(f"- {problem}")
        print("")
        print(f"Allowed {field_name}: {sorted(allowed_values)}")
        sys.exit(1)

    print(f"All {field_name} entries are valid.")


def main():
    check_entries("categories", CATEGORIES_CSV)
    check_entries("tool-language", LANGUAGES_CSV)


if __name__ == "__main__":
    main()
