# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Dates formatted as YYYY-MM-DD as per [ISO standard](https://www.iso.org/iso-8601-date-and-time-format.html).

## Unreleased

### Added

* New sections:
  * **Techniques**, with pages on discrete event simulation (DES) and statistical process control (SPC).
  * **Graph Catalogue**, starting with SPC charts. Code examples can be switched between languages using new language selector buttons (credit @amyheather). The webR and Pyodide Quarto extensions are included for running R and Python in the browser.
  * **Books, Training and Communities**, with Books (healthcare-specific / general open analytics), Training (courses / interactive tools / reference sites / recorded talks) and Communities sections, plus a 'Paid books' subsection.
  * **Recordings Finder**, which brings together recordings from all of the recording collections in one table, with search, multi-select filters (including by event), and sliders for publish date and duration. It is linked from the homepage.
  * **About** and **Contributing** pages, with About replacing the old "About HSMA" page.
* New packages, projects and tools: `ConcurrentSim`, STARS Reusability Examples, Hybrid Simulation Modelling for Orthopaedics, Somerset wait list simulation, NHSE-NDRS Cancer Treatments, NHSE-NDRS Cancer Registrations, Streamlit, the NHSRplotthedots Power BI custom visual, the Making Data Count SPC Excel chart tool, DES RAP M/M/s and stroke models (as separate entries), ESA ED Crowding Model, ESA 'Avoidable' ED Attendances, Non-Elective Flow Simulation, Renal Capacity DES Model, Meeting the demand of 111 for primary care services, Ten Similar CCGs, ADHD CYP Pathway DES, APE (AMD Protocol Explorer), NHS Vega Library, and the Demand Forecasting Tool for Capacity Planning.
* New books and training: Julia for Healthcare, the Healthcare Decision Intelligence eBook, R for Data Science (2e), the Health RAP Playbook, Visualizing Health and Healthcare Data (the first paid book), the Somerset Introduction to Data Science Course, HDR UK Futures, the HSMA programme, HSMA-λ, every HSMA module, the HSMA Python, geographic, machine learning and Streamlit books, the HSMA Little Book of DES, HSMA machine learning notebooks and the HSMA DES Playground.
* New communities: AphA, NHS-OA, HACA (Health and Care Analytics Conference), SWAIH (South West Analytics and Infrastructure in Healthcare) and HaCORN (Health and Care Operational Research Network).
* New recording collections: NHS-OA webinars and talks (including NHS.pycom), workshops and conferences; National Analyst Network Huddles; HSMA project showcases; HSMA lectures and masterclasses (including HSMA 3 and a standalone DES workshop); HACA; Midlands Decision Support Network training; the NHS-R Podcast; Insight 2020 and 2021 festivals; AphA webinars and conferences; Strategy Unit webinars; and SWAIH Insight Talks. Training recordings were also added to the New Hospital Programme Demand Model entry.
* Recording entries include searchable tables of their talks, showing each talk's duration. These are built from YouTube playlists using `fetch_youtube_playlists.py` and `build_youtube_talks.py`, and configured in `resources/recordings/collections.yml`. A monthly GitHub Action refreshes them.
* Recordings of whole sessions or conference days are split into talks using the timestamps or talk lists in their descriptions, leaving out breaks and short welcomes and closing remarks. Collections can turn this off with `split_talks: false` (used for the HSMA lectures, whose timestamps mark sections of a lecture), or keep particular videos whole with `keep_whole_videos`. The README explains how to check how recordings were split.
* Homepage navigation cards, counts of written and planned entries (linking to the project board), a showcase of the newest entries, and an All Contributors table.
* Atlas logo in the navbar, and HSMA and NIHR logos with the NIHR disclaimer in the footer.
* Animated headers on the homepage and main section pages.
* "Page last modified" dates on entry pages, taken from each file's last change on `main`.
* Entry pages now show who wrote the Atlas entry (`entry-author`), an icon for the type of project, and the status and rating rationale in the title block.
* New issue templates for suggesting a package, project or tool, a technique, a graph or a book or training resource; reporting a content error; requesting removal of content; and editing an existing entry.
* Permitted categories and languages are kept in CSV files in `templates/`. `check_yaml.py` and a "Validate Quarto categories" Action check entries against them, and another Action keeps the submission template's categories in sync with the CSV.
* New categories, including `Communities`, `Courses`, `Interactive Learning Tools`, `Reference Sites`, `General Open Analytics`, `Recorded Talks`, `Paid Resources` (with a <i class="fa-solid fa-sterling-sign"></i> icon and an icon key) and `Synchronous` / `Asynchronous` tags for courses. `check_yaml.py` checks each books and training entry appears in exactly one section, and that these categories are used together correctly.
* Google Analytics, with a cookie consent banner.
* `bergam0t/value-box` and `bergam0t/splide-carousel` Quarto extensions.
* Conda environment (`environment.yaml`) for local development, also used by the GitHub Actions.

### Changed

* Theme changed from HSMA red to teal, with the light theme now the default. The green was darkened for contrast, and the dark theme retinted to match the teal header.
* Packages, projects and tools are now grouped by language and sorted by title, all on one page. Languages are set with a new `tool-language` field instead of `pub-info.language` and language categories.
* Books and training moved out of packages, projects and tools into their own section.
* Entries now live in their own folders as `index.qmd`.
* Pages generated from the submission form now include the entry author and language, use sanitised folder and branch names, and handle quotes in the submitted text.
* SPC guidance moved from the plot-the-dots entries to the SPC technique page, and the plot-the-dots entries now list the other SPC tools.
* Improved the abstracts of several existing entries.
* Updated the NIHR logo.

### Fixed

* Broken relative links between pages, and broken homepage navigation links.
* Homepage layout on small screens.
* Title block headers overlapping authors, and their position on the packages, projects and tools page.
* Menu collapsing at the wrong screen width.
* Abstract box colour now fits the theme.
* Several fixes to the publish and PR check workflows.

### Removed

* Placeholder folders for planned packages and techniques. Planned entries are now tracked on the GitHub project board.
* Status and rationale section at the end of entry pages, as these are now in the title block.
* `resources/generated_counts.yml` is no longer tracked, as it is regenerated on every render.
* Empty `requirements.txt`.

## v0.2.0 (2025-11-19)

This release adds some new tools, and makes changes to styling and site setup.

### Added

* New pages for: DES RAP Book, NHS RAP Community of Practice, `opencodecounts`, a community pharmacy workforce model, the New Hospital Programme Demand Model, `NHSRwaitinglist`, the ICB Place Based Allocation Tool, `nhs_time_of_travel`,  `AmbModelOpen`, `sim-tools`, `ciw`, `BPTK`.
* Light theme option now available, including a lighter version of the custom grid card.
* Add `CITATION.cff` and `CHANGELOG.md`.
* Add "Other" category to packages, projects and tools.

### Changed

* README contribution instructions now clearer and more practical, and mentions `quarto render` command.
* README contribution instructions now also includes separate section for editing existing entries
* Add title and summary to `index.qmd` and updated contributions paragraph to point to README.
* NHS-R PlotTheDots PDFs no longer stored in `resources/`; now live alongside the relevant tool's `.qmd` - since they're only used on that page, it makes sense to store them there (just like images).
* Author YAML in tool pages now refers to the person or team who made the package/tool, not the Atlas page writer. This is because current set-up creates confusion, as implies the page writer is the package/tool author.
* All CSS/SCSS styling files have moved to `resources/`.
* Abstract titles and colors reworked for legibility - shorter title, no opacity and larger font size.
* Moved code/documentation/website buttons to below abstract for better visibility (easy to not notice them when they are above the title).
* Changed the format of "project status" section at end of each page to include status alongside rationale.
* Make project title on grid cards a hyperlink.

### Fixed

* Corrected the GIF filename for the bupaR page.
* Prevented the pm4py web app from overflowing off the right edge of the page.
* Add `docs/` and `site_libs/` to `.gitignore`.
* Banner PNG added and switched to being loaded globally via `_quarto.yml` (removed broken per-page banner references).
* Removed white hyperlinks from themes, so you are able to see location in table of contents.
* Corrected category and add image for NHSRtt page.
* Fixed description and rating rationale not appearing in generated .qmd if generated from issue template
* Fixed broken fork link from homepage and replaced with link to general contribution instructions

### Removed

* Removed the committed `docs/` folder from the repo. As the site builds via GitHub Actions, committing generated files just clutters PRs and risks the published site falling out of sync - keeping it uncommitted makes for a cleaner workflow.
* Removed favicon and logo from `_quarto.yml` as files are not present.
* Dropped `linkedin` and `website` from author YAML - these fields aren’t supported in the current page layouts and would require custom HTML.

## v0.1.0 (2025-11-13)

Initial release of the website (work in progress).

### Added

* Basic website structure and navigation.
* Seven packages/projects/tools: `vidigi`, `bupaR`, `pm4py`, `nowcasts`, `patientflow`, `nhsr-plotthedots`, `nhspy-plotthedots`.
* Placeholders for additional packages, and for the techniques and graph catalogue pages.
* Theme based on the HSMA branding.
* Automated deployment via GitHub Pages using GitHub Actions.
* Issue template for submitting new packages, projects, or tools, with a corresponding GitHub Action to generate Quarto pages from submitted issue forms.
