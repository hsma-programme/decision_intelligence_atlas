# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). Dates formatted as YYYY-MM-DD as per [ISO standard](https://www.iso.org/iso-8601-date-and-time-format.html).

## v0.2.0 - Unreleased

This release adds some new tools, and makes changes to styling and site setup.

### Added

* New pages for DES RAP Book, NHS RAP Community of Practice and `opencodecounts`.
* Light theme option now available, including a lighter version of the custom grid card.
* Add `CITATION.cff` and `CHANGELOG.md`.

### Changed

* README contribution instructions now clearer and more practical, and mentions `quarto render` command.
* Add title and summary to `index.qmd` and updated contributions paragraph to point to README.
* NHS-R PlotTheDots PDFs no longer stored in `resources/`; now live alongside the relevant tool's `.qmd` - since they're only used on that page, it makes sense to store them there (just like images).
* Author YAML in tool pages now refers to the person or team who made the package/tool, not the Atlas page writer. This is because current set-up creates confusion, as implies the page writer is the package/tool author.
* All CSS/SCSS styling files have moved to `resources/`.
* Abstract titles and colors reworked for legibility - shorter title, no opacity and larger font size.

### Fixed

* Corrected the GIF filename for the bupaR page.
* Prevented the pm4py web app from overflowing off the right edge of the page.
* Add `docs/` and `site_libs/` to `.gitignore`.
* Banner PNG added and switched to being loaded globally via `_quarto.yml` (removed broken per-page banner references).
* Switched rating callouts from `.callout-info` (not a real style) to `.callout-note` so callouts render properly.
* Removed white hyperlinks from themes, so you are able to see location in table of contents.

### Removed

* Removed the committed `docs/` folder from the repo. As the site builds via GitHub Actions, committing generated files just clutters PRs and risks the published site falling out of sync - keeping it uncommitted makes for a cleaner workflow.
* Removed favicon and logo from `_quarto.yml` as files are not present.
* Dropped `linkedin` and `website` from author YAML - these fields aren’t supported in the current page layouts and would require custom HTML.

## v0.1.0 - 2025-11-13

Initial release of the website (work in progress).

### Added

* Basic website structure and navigation.
* Seven packages/projects/tools: `vidigi`, `bupaR`, `pm4py`, `nowcasts`, `patientflow`, `nhsr-plotthedots`, `nhspy-plotthedots`.
* Placeholders for additional packages, and for the techniques and graph catalogue pages.
* Theme based on the HSMA branding.
* Automated deployment via GitHub Pages using GitHub Actions.
* Issue template for submitting new packages, projects, or tools, with a corresponding GitHub Action to generate Quarto pages from submitted issue forms.
