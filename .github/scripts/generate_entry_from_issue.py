"""
Write an Atlas entry from a "New Package, Project or Tool Submission" issue.

Reads the issue form, as parsed by issue-ops/parser, from the ISSUE_JSON
environment variable, and writes `<section>/<folder>/index.qmd` in the same
format as the templates in `templates/`. Books, courses, training resources
and communities go in `books_training/`; everything else in
`packages_projects_tools/`.

The issue text is only ever read from the environment and written to the
file, never put into a shell command, so it can't run code in the workflow.

If GITHUB_OUTPUT is set, writes `folder` (the entry's folder name) and
`path` (the path of the new file) to it for later workflow steps.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys


# Categories that put an entry in books_training/ rather than
# packages_projects_tools/.
BOOKS_TRAINING_CATEGORIES = {
    "Courses and Training or Reference Materials",
    "Books",
    "Communities",
    "Courses",
    "Interactive Learning Tools",
    "Reference Sites",
    "Recorded Talks",
}

STATUS_SPANS = {
    "Gold": '<span style="color: #D18B12FF">Gold</span>',
    "Silver": '<span style="color: #888888FF">Silver</span>',
    "Bronze": '<span style="color: #893400FF">Bronze</span>',
}

# Issue form checkbox labels (matched on these words) and the icons they map to.
PROJECT_TYPE_ICONS = [
    ("NHS", '<i class="fa-solid fa-hospital"></i>'),
    ("academia", '<i class="fa-solid fa-user-graduate"></i>'),
]

# Icon required by check_yaml.py on entries in the Paid Resources category.
PAID_ICON = '<i class="fa-solid fa-sterling-sign" title="Paid resource"></i>'

# (issue form field id, link name, icon)
LINKS = [
    ("code", "Code", "fa-brands fa-github"),
    ("documentation", "Documentation", "fa-solid fa-book"),
    ("paper", "Paper", "fa-solid fa-file-contract"),
    ("pypi", "PyPi", "fa-solid fa-brands fa-python"),
    ("cran", "CRAN", "fa-solid fa-brands fa-r-project"),
    ("website", "Website", "fa-solid fa-globe"),
]

# Plain YAML scalars that are safe to write without quotes.
PLAIN_SCALAR = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 +&()/.,'-]*$")


def text(data, key):
    """
    Return a text field from the issue, or "" if it wasn't filled in.

    Parameters
    ----------
    data : dict
        Parsed issue form.
    key : str
        Field id.

    Returns
    -------
    str
        The stripped value, with non-breaking hyphens made plain.
    """
    value = data.get(key)
    if value is None:
        return ""
    if isinstance(value, list):
        value = "\n".join(str(v) for v in value)
    value = str(value).replace("‑", "-").strip()
    if value == "_No response_":
        return ""
    return value


def choices(data, key):
    """
    Return the selected options of a dropdown or checkboxes field.

    Parameters
    ----------
    data : dict
        Parsed issue form.
    key : str
        Field id.

    Returns
    -------
    list of str
        Selected options. Checkboxes may be parsed as a list or as a dict
        with a `selected` list, depending on the parser version.
    """
    value = data.get(key)
    if isinstance(value, dict):
        value = value.get("selected", [])
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [
        str(v).replace("‑", "-").strip()
        for v in value
        if str(v).strip() and str(v).strip() != "_No response_"
    ]


def split_list(value, separator):
    """
    Split a free-text list such as "SQL; Databricks" into its items.

    Parameters
    ----------
    value : str
        Free text.
    separator : str
        Separator between items.

    Returns
    -------
    list of str
        Non-empty, stripped items.
    """
    return [item.strip() for item in value.split(separator) if item.strip()]


def scalar(value):
    """
    Format a string as a YAML scalar, quoting it unless it is plainly safe.

    Parameters
    ----------
    value : str
        Value to format.

    Returns
    -------
    str
        The value, plain or double-quoted (JSON strings are valid YAML).
    """
    if PLAIN_SCALAR.match(value):
        return value
    return json.dumps(value, ensure_ascii=False)


def block(value, indent):
    """
    Format text as the indented body of a YAML `|` block scalar.

    Parameters
    ----------
    value : str
        Text, possibly over several lines.
    indent : int
        Number of spaces to indent each line by.

    Returns
    -------
    str
        The indented text, with blank lines left empty.
    """
    pad = " " * indent
    lines = (value or "TBC").splitlines()
    return "\n".join(pad + line if line.strip() else "" for line in lines)


def folder_name(name):
    """
    Turn an entry's name into a folder name.

    Parameters
    ----------
    name : str
        Name of the package, project or tool.

    Returns
    -------
    str
        Lower-case letters and numbers, separated by single underscores.
    """
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "new_entry"


def build_entry(data, now):
    """
    Build the folder, section and file contents for an entry.

    Parameters
    ----------
    data : dict
        Parsed issue form.
    now : datetime.datetime
        Time to use as the entry's date.

    Returns
    -------
    tuple of (str, str, str)
        Section folder, entry folder name and the contents of index.qmd.
    """
    name = text(data, "model_name")
    if not name:
        sys.exit("The issue has no package, project or tool name.")

    categories = choices(data, "category")
    languages = choices(data, "language") + split_list(
        text(data, "language_other"), ";"
    )
    section = (
        "books_training"
        if set(categories) & BOOKS_TRAINING_CATEGORIES
        else "packages_projects_tools"
    )

    status = choices(data, "status")
    status = STATUS_SPANS.get(status[0], status[0]) if status else "N/A"

    project_type = " ".join(
        icon
        for word, icon in PROJECT_TYPE_ICONS
        if any(word in label for label in choices(data, "project_type"))
    )
    if "Paid Resources" in categories:
        project_type = f"{project_type} {PAID_ICON}".strip()

    lines = ["---", f"title: {json.dumps(name, ensure_ascii=False)}"]

    lines.append("categories:")
    lines += [f"  - {scalar(c)}" for c in categories] or ["  - TBC"]

    lines.append("tool-language:")
    lines += [f"  - {scalar(lang)}" for lang in languages] or ["  - N/A"]

    # Single-quoted, as in the templates; '' is an escaped ' in YAML.
    lines.append("status: '" + status.replace("'", "''") + "'")
    # No image line: Quarto rejects an empty `image:`. Reviewers add one.

    authors = split_list(text(data, "author"), ",")
    if authors:
        lines.append("author:")
        lines += [f"  - name: {scalar(a)}" for a in authors]

    lines.append(f'date: "{now.strftime("%Y-%m-%dT%H:%M:%S+00:00")}"')

    lines.append("pub-info:")
    if project_type:
        lines.append(f"  project-type: {project_type}")
    lines.append("  rationale-for-status: |")
    lines.append(block(text(data, "status_reason"), 4))

    entry_author = text(data, "entry_author")
    if entry_author:
        lines.append("  entry-author:")
        lines.append(f"    - name: {scalar(entry_author)}")
        entry_author_url = text(data, "entry_author_url")
        if entry_author_url:
            lines.append(f"      url: {json.dumps(entry_author_url)}")

    lines.append("  abstract: |")
    lines.append(block(text(data, "summary"), 4))

    lines.append("  links:")
    for key, link_name, icon in LINKS:
        url = text(data, key)
        lines.append(f"  - name: {link_name}")
        lines.append(f"    url: {json.dumps(url) if url else ''}".rstrip())
        lines.append(f"    icon: {icon}")
    lines.append("---")
    lines.append("")

    lines.append(text(data, "details") or "TBC")

    other_urls = text(data, "other_urls")
    if other_urls:
        lines += ["", "## Additional links", "", other_urls]

    category_other = split_list(text(data, "category_other"), ";")
    if category_other:
        lines += [
            "",
            "<!-- REVIEWER: the submitter suggested these new categories. "
            "Add any that should be used to the categories above and to "
            "templates/packages_projects_tools_permitted_categories.csv, "
            "then delete this comment.",
            "",
        ]
        lines += [f"- {c}" for c in category_other]
        lines.append("-->")

    return section, folder_name(name), "\n".join(lines) + "\n"


def main():
    data = json.loads(os.environ["ISSUE_JSON"])
    section, folder, contents = build_entry(data, datetime.now(timezone.utc))

    path = Path(section, folder, "index.qmd")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    print(f"Wrote {path}")

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"folder={folder}\n")
            f.write(f"path={path.as_posix()}\n")


if __name__ == "__main__":
    main()
