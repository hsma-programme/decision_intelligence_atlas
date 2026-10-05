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
QMD_ROOTS = [Path("packages_projects_tools"), Path("books_training")]

# Categories that place a books_training entry in a section of
# books_training/index.qmd. Keep in sync with that page's listings.
BOOKS_TRAINING_SECTIONS = {"Books", "Communities"}
TRAINING_SUBSECTIONS = {
    "Courses",
    "Interactive Learning Tools",
    "Reference Sites",
}

# Icon that must appear in `pub-info.project-type` for `Paid Resources`.
PAID_ICON = "fa-sterling-sign"


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

    paths = [path for root in QMD_ROOTS for path in root.rglob("*.qmd")]

    for path in paths:
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
        elif isinstance(entries, str):
            entries = [entries]
        elif not isinstance(entries, list):
            problems.append(
                f"{path}: {field_name} must be a string or a list"
            )
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


def check_books_training_sections():
    """
    Check each books_training entry appears in exactly one section.

    An entry must be tagged with exactly one of `Books`, `Communities` or a
    training subsection (`Courses`, `Interactive Learning Tools`,
    `Reference Sites`). Otherwise it would be missing from, or duplicated
    on, the Books, Training and Communities page. `Paid Resources` entries
    must also be `Books` and show the paid icon.
    """
    problems = []

    for path in Path("books_training").glob("*/index.qmd"):
        text = path.read_text(encoding="utf-8")
        front_matter = extract_front_matter(text)
        if not front_matter:
            continue

        meta = yaml.safe_load(front_matter) or {}
        categories = meta.get("categories") or []
        if isinstance(categories, str):
            categories = [categories]

        tags = set(categories) & (BOOKS_TRAINING_SECTIONS | TRAINING_SUBSECTIONS)
        if len(tags) != 1:
            problems.append(
                f"{path}: must have exactly one of "
                f"{sorted(BOOKS_TRAINING_SECTIONS | TRAINING_SUBSECTIONS)} "
                f"in categories (found {sorted(tags)})"
            )
        if "General Open Analytics" in categories and "Books" not in categories:
            problems.append(
                f"{path}: 'General Open Analytics' can only be used with 'Books'"
            )
        if "Paid Resources" in categories:
            if "Books" not in categories:
                problems.append(
                    f"{path}: 'Paid Resources' can only be used with 'Books'"
                )
            project_type = (meta.get("pub-info") or {}).get("project-type") or ""
            if PAID_ICON not in project_type:
                problems.append(
                    f"{path}: 'Paid Resources' entries must include the "
                    f"{PAID_ICON} icon in pub-info.project-type"
                )

    if problems:
        print("books_training section validation failed:\n")
        for problem in problems:
            print(f"- {problem}")
        sys.exit(1)

    print("All books_training entries are in exactly one section.")


def main():
    check_entries("categories", CATEGORIES_CSV)
    check_entries("tool-language", LANGUAGES_CSV)
    check_books_training_sections()


if __name__ == "__main__":
    main()
