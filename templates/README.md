# Atlas entry templates

This folder has a template for each kind of Atlas entry. Each entry is a folder containing an `index.qmd` file (plus any images it uses), so each template is a folder too: copy it, rename it, and fill it in.

Not comfortable with GitHub and Quarto? You don't need to use these. You can [submit an issue](https://github.com/hsma-programme/decision_intelligence_atlas/issues/new/choose) instead, and we'll write the entry for you.

## Which template?

| I'm adding... | Template | Copy it into | Good examples to look at |
|---|---|---|---|
| A package, project or tool | [`packages_projects_tools/`](packages_projects_tools/index.qmd) | `packages_projects_tools/` | `vidigi`, `nhsrplotthedots`, `patientflow` |
| A book, course, training resource or community | [`books_training/`](books_training/index.qmd) | `books_training/` | `hsma_little_book_of_des` (book), `hsma_des_module` (course), `nhs_oa_community` (community) |
| A collection of YouTube recordings | [`recordings_collection/`](recordings_collection/index.qmd) | `books_training/` | `nhs_oa_webinars`, `nhs_oa_conference_recordings` |
| A technique | [`techniques/`](techniques/index.qmd) | `techniques/` | `des`, `spc` |
| A graph | [`graph_catalogue/`](graph_catalogue/index.qmd) | `graph_catalogue/` | `spc` |

The two CSV files in this folder list the permitted `categories` and `tool-language` values. They are used by every template that has those fields, and are checked automatically on every pull request.

## Creating an entry

1. **Copy the template folder** into the folder from the table above, and rename it after your entry, e.g. `templates/techniques/` → `techniques/queueing_theory/`. Use only lower-case letters, numbers, hyphens (`-`) or underscores (`_`) - no spaces. The folder name becomes the page's address, e.g. `atlas.hsma.co.uk/techniques/queueing_theory/`.

2. **Fill in the header** (the "front matter" between the two `---` lines at the top of `index.qmd`). Every field has a comment explaining it. Lines starting with `#` are comments - you can leave them in or delete them. In particular:
    * Set `date` to today's date and time, e.g. `date: "2026-01-31T10:00:00+00:00"`. It's used to order the homepage's "Most recently added or updated" list, and the checks fail until it's set.
    * For `categories` and `tool-language`, use values from the CSV files in this folder, spelled exactly as they are there. If no category fits, add a new one and mention it in your pull request - we'll decide whether to add it to the list.

3. **Write the page** below the header. The template suggests what to cover. Anything inside `<!-- ... -->` is a comment and won't appear on the page.

4. **Add images** to your entry's folder, and link to them with paths relative to that folder:
    * Good: `![](my_tool_example.png)`
    * Bad: `![](C:/my_username/decision_intelligence_atlas/packages_projects_tools/my_tool/my_tool_example.png)`
    * Bad: `![](my_tool/my_tool_example.png)`

5. **Check your entry.** From the root of the repository, run:

    ```
    python resources/scripts/check_yaml.py
    ```

    This checks the categories, languages, rating and date, and that books and training entries are in exactly one section. Then run `quarto preview` and look at your page, and at the section page it's listed on.

6. **Open a pull request.** A member of the Atlas team will review it, and may make small changes before it's published.

To edit an existing entry, find its folder from the page's address (e.g. `atlas.hsma.co.uk/packages_projects_tools/vidigi/` is `packages_projects_tools/vidigi/index.qmd`) and edit it in the same way. Update its `date` if you've made substantial changes.

## Where an entry appears

* **Packages, Projects & Tools** groups entries by **`tool-language`**: Python, R, Julia, Power BI, Excel, Tableau, desktop or web end-user applications, Meta, and Other (for anything else, e.g. C++, SQL or Vega). An entry with several languages appears in each of their sections, except Other: entries only appear in Other if they have none of the languages with their own section. `categories` are shown as tags, but don't affect where it appears.
* **Books, Training & Communities** groups entries by **`categories`**. Every entry needs `Courses and Training or Reference Materials`, plus exactly one of:

    | Category | Section | Also needs |
    |---|---|---|
    | `Books` | Books (healthcare-specific) | Add `General Open Analytics` if it isn't specific to healthcare, or `Paid Resources` if it has to be bought (see below) |
    | `Courses` | Training > Courses | `Synchronous` (taught live), `Asynchronous` (self-paced), or both |
    | `Interactive Learning Tools` | Training > Interactive learning tools | |
    | `Reference Sites` | Training > Reference sites | |
    | `Recorded Talks` | Training > Recorded webinars and conference talks | |
    | `Communities` | Communities | |

    `Paid Resources` books must also have the paid icon in `project-type`: `<i class="fa-solid fa-sterling-sign" title="Paid resource"></i>`.

* **Techniques** and **Graphs** list every entry in their folder, sorted by title.

Every entry also appears in the homepage's carousels.

## Choosing a rating

Packages, projects and tools, and books and training entries, have a `status` rating. The definitions below are also shown on the [Packages, Projects & Tools](https://atlas.hsma.co.uk/packages_projects_tools/) page. It isn't an exact science - it's just to give people a sense of how easy the work is to reuse - so give your reasons in `rationale-for-status`. If you rate it Bronze or Silver, say what's keeping it from a higher rating.

* **Gold**: either a well-parameterised script that is easily adapted for new use cases, with excellent documentation; a web-based or other tool with adjustable parameters; or a package. To be Gold, it should have extensive tests and clear documentation, and be a well-established project that is actively maintained.
* **Silver**: either a script that isn't optimised for reuse but is well documented and could be adapted; a web-based or other tool with adjustable parameters; or a package. Compared with Gold, it may have fewer automated tests, less documentation, or limited adoption or maintenance.
* **Bronze**: a script, tool or package with limited documentation, and/or that may need significant reworking to be reused. Also used for projects at an early stage of development, or that are no longer maintained.
* **N/A**: for entries a rating doesn't suit, such as communities, or collections of recordings from many presenters.

For books and courses, rate the quality and upkeep of the material in the same spirit.

Write the rating exactly as in the template, including the quote marks, e.g. `status: '<span style="color: #D18B12FF">Gold</span>'`.

## Reference

### Fields

| Field | Used in | Required? | Notes |
|---|---|---|---|
| `title` | All | Yes | |
| `categories` | Packages/tools, books/training, recordings | Yes | From `packages_projects_tools_permitted_categories.csv` |
| `tool-language` | Packages/tools, books/training, recordings | Yes | From `packages_projects_tools_permitted_languages.csv` |
| `status` | Packages/tools, books/training, recordings | Yes | See [Choosing a rating](#choosing-a-rating) |
| `image` | All | No | Shown on the listing card. Landscape images work best |
| `author` | All | Recommended | List of `name`, with optional `affiliation`, `orcid` and `url` |
| `date` | All | Yes | e.g. `"2026-01-31T10:00:00+00:00"` |
| `pub-info.project-type` | Packages/tools, books/training, recordings | No | Icons shown after the title - see below |
| `pub-info.rationale-for-status` | Packages/tools, books/training, recordings | Yes | Reasons for the rating |
| `pub-info.entry-author` | All | No | You, the author of the Atlas entry: `name` and optional `url` |
| `pub-info.abstract` | All | Yes | Summary for the listing card and title block, about 50-200 words |
| `pub-info.links` | All | No | Buttons: `name`, `url` and `icon`. Links with an empty `url` are hidden |
| `listing` | Any | No | Grids of related entries, or the talks table for recordings |
| `toc` | Any | No | `toc: false` hides the table of contents, which is shown by default except on graph pages |
| `aliases` | Any | No | Old addresses that should redirect here, if you move or rename an entry |

### Project-type icons

| Icon | Code | Meaning |
|---|---|---|
| <i class="fa-solid fa-hospital"></i> | `<i class="fa-solid fa-hospital"></i>` | Significant contributions from people in the NHS, public health or other healthcare or government organisations |
| <i class="fa-solid fa-user-graduate"></i> | `<i class="fa-solid fa-user-graduate"></i>` | Significant contributions from people in academia |
| <i class="fa-solid fa-sterling-sign"></i> | `<i class="fa-solid fa-sterling-sign" title="Paid resource"></i>` | Paid resource (books only) |

Use more than one by putting them on the same line, separated by a space. Leave `project-type` out for general-purpose tools that are neither.

### Link icons

Icons are [Font Awesome](https://fontawesome.com/search?ic=free) classes. The ones used across the Atlas are:

| Link | Icon |
|---|---|
| Code | `fa-brands fa-github` |
| Documentation, eBook, Module | `fa-solid fa-book` |
| Paper, Report | `fa-solid fa-file-contract` |
| PyPi | `fa-solid fa-brands fa-python` |
| CRAN | `fa-solid fa-brands fa-r-project` |
| Website, App, Web app, Article | `fa-solid fa-globe` |
| YouTube | `fa-brands fa-youtube` |
| LinkedIn | `fa-brands fa-linkedin` |
| Download | `fa-solid fa-download` |
| Poster | `fa-solid fa-file-image` |
| Email | `fa-solid fa-envelope` |

If there's more than one link of a kind, add detail to the name, e.g. `Code (Python)` and `Code (R)`.
