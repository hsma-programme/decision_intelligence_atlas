# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Dates formatted as YYYY-MM-DD as per [ISO standard](https://www.iso.org/iso-8601-date-and-time-format.html).

## Unreleased

### Added

* New pages for: `ConcurrentSim`, Julia for Healthcare, Visualizing Health and Healthcare Data (the first paid book), NHS-OA webinar and talk (including NHS.pycom), workshop and conference recordings, National Analyst Network Huddle recordings, HSMA project showcase recordings, HSMA lecture and masterclass recordings, HACA (Health and Care Analytics Conference), Midlands Decision Support Network training recordings, the NHS-R Podcast, Insight 2020 and 2021 festival recordings, AphA webinar and conference recordings, Strategy Unit webinar recordings. Added HSMA 3 lectures and a standalone DES workshop to the HSMA lecture recordings, and training recordings to the New Hospital Programme Demand Model entry.

### Changed

* Projects now grouped by language rather than analysis type.
* "Books and Training" page renamed to "Books, Training and Communities" and split into Books (healthcare-specific / general open analytics), Training (courses / interactive tools / reference sites) and Communities sections, using new `Communities`, `Courses`, `Interactive Learning Tools`, `Reference Sites` and `General Open Analytics` categories. `check_yaml.py` now checks each entry appears in exactly one section.
* Added a 'Paid books' subsection to the Books, Training and Communities page, using a new `Paid Resources` category and a <i class="fa-solid fa-sterling-sign"></i> icon in `project-type`, plus an icon key on that page. `check_yaml.py` checks `Paid Resources` is only used with `Books` and that the icon is present.
* Added `Synchronous` and `Asynchronous` categories for courses, shown as tags on listing cards. `check_yaml.py` checks every `Courses` entry has at least one, and that they are only used with `Courses`.
* Added a 'Recorded webinars and conference talks' subsection to the Training section, using a new `Recorded Talks` category.
* Recording entries now include searchable tables of their talks, built from YouTube playlists using `fetch_youtube_playlists.py` and `build_youtube_talks.py`, and configured in `resources/recordings/collections.yml`.
* New Recordings Finder page, bringing together recordings from all of these collections in one table with search and multi-select filters, linked from the homepage.
* Recording tables now show each talk's duration, and the Recordings Finder has a duration slider in 5-minute steps.
* The Recordings Finder shows recordings from before the NHS-R and NHS.pycom communities merged to form NHS-OA under their original communities, using new `earlier_source` and per-playlist `source` options.

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
