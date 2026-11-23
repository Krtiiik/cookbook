# Architecture

<!--
The big picture and the reasons behind it, for Claude.
Don't list files, classes or signatures: the source shows those.
Write what a newcomer couldn't work out by reading the code: how the parts fit together,
why a design was chosen over the obvious alternative, and the constraints that shaped it.
-->

## Overview

A static Czech cooking site: recipes are the main content, explainers (methods, ingredients, equipment, troubleshooting) support them. A custom Python build turns Markdown, YAML catalogs and data files into HTML plus one JSON index, and deploys to GitHub Pages. The full brief is `docs/BRIEF.md`; the structure/design contract is `SPEC.md`. Nothing is built yet.

## Components and flow

- **Content**: recipe files (frontmatter + body), explainer body files (no frontmatter), catalogs (explainer entries, groups), data (units, allergens), banners, photos.
- **Build**: loads everything, validates it, resolves `[[slug]]` links, derives allergens, diet and backlinks, renders templates, writes the index and resized photos. It is also the linter.
- **Client scripts**: read the generated index for search, filters and hover previews; the scaler, converter and seasonal calendar work on page data.
- **Authoring**: skills and agents (writer, illustrator, reviewer, fact-checker) plus a corpus-lookup script feed new content into the repository.

## Design notes

**Pattern taken from the trading site.** The owner's trading learning site (lessons + concepts) works well for them; this site reuses its shape (custom build, catalog as roadmap, `[[slug]]` links, banners, own index, agent pipeline), not its code.

**Custom Python build, not Astro or Hugo.** Same toolchain and habits as the trading site, and full control over validation and link resolution. Rejected: Astro (new Node toolchain), Hugo (no real schema validation).

**Build as linter.** The build collects every problem, then fails once, so one run shows all broken links, unknown units and missing photos.

**Catalog as roadmap; written = file exists.** Explainer titles and data live in the catalog, so a recipe can link `[[shallot]]` before its page exists, and planned pages still preview. No `draft` flag for explainers.

**Structured ingredients.** One data source feeds the ingredient list, the serving scaler, JSON-LD and the ingredient backlinks. Rejected: a parsed line syntax (needs a parser) and free text (no scaler).

**Body links instead of frontmatter lists.** Methods, equipment and troubleshooting links come from `[[slug]]` in the steps. A separate list would duplicate them and drift.

**Allergens and diet are derived.** Typed per recipe they are easy to forget; derived from the ingredient catalog they stay correct. An override exists for edge cases.

**Groups with kinds replace course, tags and collections.** One validated list covers what the dish is and when you make it; free tags would split on typos. Basics are a group, not a separate type, so they reuse the recipe template and the scaler.

**Drafts are published, marked.** The site is for the owner first, so untested recipes are useful online; the badge and placeholder image keep them apart from tested ones. Tested requires a photo.

**No cooking log, no version numbers.** A short `changes` list on the recipe is enough; git keeps the rest.

**Own JSON index, not Pagefind.** One file drives search, filters and previews, as on the trading site. Enough for a few hundred pages.

**Photos shrunk on import.** Phone originals would bloat the repo and Pages limits; originals stay outside the repository.

**Private corpus.** Recipe datasets are used only for comparing variants when drafting. They never enter the published site; a near-copy check runs on each draft.

**Never commercial, CC BY-NC-SA 4.0.** This allows non-commercial corpora as private reference.
