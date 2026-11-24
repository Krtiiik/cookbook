# Conventions

<!--
Idioms and placement rules that a linter or formatter can't enforce.
Skip anything tooling already checks. Prefer a rule plus a one-line reason over a long explanation.
-->

## Content

- Site text is Czech. Slugs, keys, file names and code are English (`onion`, not `cibule`), so links stay stable when titles change.
- Address the reader informally (tykání: "nakrájej", "tvoje", "zkus"), never with vykání ("nakrájejte", "Vaše"). This applies to all Czech text: recipes, explainers and UI labels, buttons and messages.
- Slugs are unique across all sections and recipes, so `[[slug]]` never needs a section prefix.
- Link a method, equipment or troubleshooting page with `[[slug]]` or `[[slug|text]]` in the body. Do not add frontmatter lists for them.
- Every written page needs at least one incoming link.
- Write ingredient amounts in metric units from the unit list. Use `text:` (e.g. "podle chuti") only for amounts that must not scale.
- Never type allergens or diet on a recipe unless the derived value is wrong; then add the override and a note why in Poznámky.
- Food-safety numbers (temperatures, storage times) need a cited authority, named in the text ("podle USDA FSIS"). Never invent them.
- Cooked food into the fridge always gets the same rule: shallow containers, in the fridge within 2 hours, then a day count (USDA FSIS). A loose "vychladlé dej do lednice" invites hours on the counter.
- Heat words, only these: mírný, středně mírný, střední, středně vysoký, vysoký oheň; "moc silný oheň" only as a mistake. To lower the heat: "stáhni oheň". Give a heat word wherever a step changes the heat, so pages can agree.
- Raw-meat storage follows USDA FSIS by cut: fridge days, freezer months for quality ("bezpečné neomezeně"). Quality-only times (spices) need no source but must not read as safety claims.
- A recipe step that cooks until soft gives the fork test with the time, not the time alone.
- Troubleshooting pages use exactly these headings: Příznak, Možné příčiny, Jak to zachránit, Jak tomu předejít. A cause may end with "(→ …)" naming the symptom it gives.
- Ingredient pages have a body "Náhrady" section (bold bullets). Catalog `substitutes` lists only existing slugs; substitutes without a slug stay plain text there.
- `[[slug]]` without text renders the title in the nominative. Where the sentence needs another case, write `[[slug|text]]`.
- An explainer's catalog summary uses the body's terms and does not blur states the body separates (it is the link preview).
- Draft text from the corpus must be new writing. No sentence may be a near-copy of a source.
- Add a `changes` entry each time a tested recipe changes in substance.
- Czech past tense shows gender, and the owner's is not recorded. Write about cooking in the present or in neutral forms ("ještě nebyl uvařený", not "ještě jsem ho nevařil").
- Quote YAML values that contain a comma or a colon (`note: "rozpůlená, ve slupce"`); unquoted, YAML splits them into unknown keys.

## Where things go

- New explainer: add the catalog entry first (it becomes planned), then the body file and its banner.
- New group: add it to the group catalog with a kind before any recipe uses it.
- New unit: add it to the unit list with Czech forms and scaling rules.
- Recipe photos: run the import script; never commit an original.
- Corpus files: outside the repository or in a git-ignored folder.

- New category, cuisine or season value: add its Czech label to `data/labels.yaml`.
- Lists a template needs (related pages, backlinks, recent changes) are methods on `Site` in the build, not loops in Jinja: templates run with `StrictUndefined`, and Python is easier to test.

## Code

- The build collects problems into a list and raises once at the end; never stop at the first problem.
- Rounding of scaled amounts must match in `build.py` and `site.js` (half up, step from `units.yaml`).
- The look follows `docs/STYLE.md`; the classes and data attributes in `SPEC.md` are the contract between templates, CSS and JS.

## Banners

- 3:1 SVG, colours only through the banner CSS variables in `SPEC.md`, no `id` attributes.
- Animation must stop under `prefers-reduced-motion`.

## Testing

- pytest in `tests/test_build.py`. Unit tests build a small site in `tmp_path` (the real `data/` plus small catalogs); the last tests build the real site and check that every internal link resolves.
- A new check in the build gets a test that triggers its message.
