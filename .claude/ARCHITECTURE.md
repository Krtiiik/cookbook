# Architecture

<!--
The big picture and the reasons behind it, for Claude.
Don't list files, classes or signatures: the source shows those.
Write what a newcomer couldn't work out by reading the code: how the parts fit together,
why a design was chosen over the obvious alternative, and the constraints that shaped it.
-->

## Overview

A static Czech cooking site: recipes are the main content, explainers (methods, ingredients, equipment, troubleshooting) support them. A custom Python build turns Markdown, YAML catalogs and data files into HTML plus one JSON index, and deploys to GitHub Pages. The full brief is `docs/BRIEF.md`, the structure/design contract is `SPEC.md`, and the look is `docs/STYLE.md` (ported from the hybrid "Smaltovaný sešit" prototypes on the design canvas). The private corpus (TheMealDB in SQLite) and the saved sources live in the git-ignored `corpus/` folder.

## Components and flow

- **Content**: recipe files (frontmatter + body), explainer body files (no frontmatter), catalogs (explainer entries, groups), data (units, allergens), banners, photos.
- **Build**: loads everything, validates it, resolves `[[slug]]` links, derives allergens, diet and backlinks, renders templates, writes the index and resized photos. It is also the linter.
- **Client scripts**: read the generated index for search, filters and hover previews; the scaler, converter and seasonal calendar work on page data.
- **Authoring**: skills dispatch agents. Two write (writer, illustrator); the others only read and report (reviewer, fact-checker, test-cook, auditor, planner, variant-researcher). The main session builds, looks at the page and commits.

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

**Photo found by file name.** A tested recipe needs `photos/<slug>.webp`; there is no `photo` field to keep in sync, the same way an explainer is written when its body file exists.

**Labels in one data file.** Difficulty, cuisine, season, diet and category values are English keys with Czech labels in `data/labels.yaml`. The build rejects unknown values, so a typo cannot create a new filter option.

**Photos shrunk on import, metadata dropped.** Phone originals would bloat the repo and the Pages limits, so originals stay outside the repository. The import script also removes EXIF, so phone GPS data is never published.

**Private corpus.** Recipe datasets are used only for comparing variants when drafting. They never enter the published site; a near-copy check runs on each draft.

**Never commercial, CC BY-NC-SA 4.0.** This allows non-commercial corpora as private reference.

**Checkers are read-only and separate from the writer.** A writer that checks its own page finds what it meant, not what it wrote. Each checker has one job (reading, facts, the kitchen), so findings do not overlap, and the writer may reject a finding with a reason; a repeated disagreement goes to the user.

**Only the writer runs on Opus.** Each page goes through several check rounds, so agent runs use most of the subscription. The page text is the product, so the writer is pinned to `opus`; the checkers, researcher, illustrator, auditor and planner follow written rules and are pinned to `sonnet`. The main session can then run on Sonnet too.

**Test-cook next to the reviewer.** A recipe can read well and still fail at the stove (an ingredient never used, a step out of order). The trading site had no equivalent; recipes need one.

**Catalog data is fact-checked.** Allergens and diet are derived from `catalog/suroviny.yaml`, so a wrong `allergens` or `animal` value is a safety problem, not a typo. The fact-checker checks catalog entries with the page that adds or uses them.

**Near-copy check compares only Czech with Czech.** A word-run check is exact and cheap within one language but meaningless across languages, and machine translation first would make it fuzzy. So the script compares drafts with the Czech pages the researcher saved, and the reviewer judges close translations of English sources. The check runs in the `write-recipe` skill, not in CI, because the sources are private.

**Corpus downloaded once, not queried live.** About 26 API calls fill a local SQLite file with full-text search; lookups are then offline and fast, and agents make no network calls for them.
