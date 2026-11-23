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
- Food-safety numbers (temperatures, storage times) need a cited authority. Never invent them.
- Draft text from the corpus must be new writing. No sentence may be a near-copy of a source.
- Add a `changes` entry each time a tested recipe changes in substance.

## Where things go

- New explainer: add the catalog entry first (it becomes planned), then the body file and its banner.
- New group: add it to the group catalog with a kind before any recipe uses it.
- New unit: add it to the unit list with Czech forms and scaling rules.
- Recipe photos: run the import script; never commit an original.
- Corpus files: outside the repository or in a git-ignored folder.

## Banners

- 3:1 SVG, colours only through the banner CSS variables in `SPEC.md`, no `id` attributes.
- Animation must stop under `prefers-reduced-motion`.

## Testing

<!-- To be set when the build exists: pytest, tests also build the real site. -->
