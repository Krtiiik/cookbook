# Project brief: Czech cooking reference and recipe site

This brief replaces the first draft. It records the structure, content model and stack. The visual design is in a separate work stream; `SPEC.md` is the contract between the two. Reasons for the design choices are in `.claude/ARCHITECTURE.md`, terms in `.claude/CONTEXT.md`.

## 1. Goal

A public website, built for the owner first:

1. **Recipes**: the main content. Recipes in the owner's own style, published as drafts and then tested.
2. **Explainers**: methods, ingredients, equipment and troubleshooting pages that support the recipes.

All parts link to each other. A recipe links to the explainers it uses. Each explainer lists the recipes that use it. The build generates the reverse links from the recipe data and body links; nobody keeps manual lists.

- Site content: **Czech** only, no i18n. The site addresses the reader informally (**tykání**, never vykání), in content and UI text alike.
- Code, slugs, file names, data keys and comments: **English**.
- Never commercial. Content licence: **CC BY-NC-SA 4.0**.

## 2. Site structure

| Part | URL | What |
|---|---|---|
| Recipes | `recepty/` | The main content. |
| Methods | `metody/` | Braising, confit, emulsions, fermentation... |
| Ingredients | `suroviny/` | Meat, vegetables, spices, flours... |
| Equipment | `vybaveni/` | Knives, pans, thermometer: purpose, choice, care, substitutes. |
| Troubleshooting | `reseni-problemu/` | "Proč se mi srazila omáčka?" Symptom, causes, fix, prevention. |
| Groups | `skupiny/<slug>/` | Recipe groups, generated. `zaklady/` is the page of the group `zaklady`. |
| Reference | `reference/` | Special page with tools: unit converter, seasonal calendar. |
| About | `o-webu/` | Special page: licence, credits, how the site is made. |

Removed from the first draft: the cooking log (`denik`), `kolekce` as a section (now groups), `zaklady` as a content type (now a group), `reference` as a content section (now one tools page).

## 3. Content model

Two kinds of content page:

- **Recipe**: a Markdown file with YAML frontmatter. One file per recipe.
- **Explainer**: a method, ingredient, equipment or troubleshooting page. Its title, summary and data live in a **catalog** file per section. Its body is a Markdown file **without frontmatter**. An explainer is **written** when its body file exists, otherwise **planned**. A planned explainer still has a page, takes links and shows a hover preview, so the catalog is also the roadmap.

### 3.1 Recipe

```yaml
---
title: "Hovězí guláš"
summary: "One or two sentences."
status: tested                # draft | tested; tested needs photos/<slug>.webp
servings: 4
time_active_min: 30
time_total_min: 180
difficulty: medium            # easy | medium | hard
cuisine: czech
season: [autumn, winter]
groups: [hlavni-jidla, zimni]
ingredient_groups:
  - name: Guláš
    items:
      - { qty: 1000, unit: g, item: beef-shank }
      - { qty: 500, unit: g, item: onion, note: nakrájená }
      - { qty: 2, unit: lzice, item: sweet-paprika }
      - { qty: 500, unit: ml, item: hovezi-vyvar } # a basic: links to its recipe
      - { text: podle chuti, item: salt }          # never scales
changes:                      # at least one entry; newest is the "updated" date
  - { date: 2026-11-20, note: "Víc cibule, kratší vaření." }
# optional overrides of derived data:
# allergens: [...]
# diet: [...]
---
```

- The slug is the file name. The photo is found by file name too (`photos/<slug>.webp`), so there is no `photo` field.
- Quote a `note` or `text` that contains a comma or a colon, or YAML splits it.
- `item` is an ingredient slug from `catalog/suroviny.yaml` or the slug of a recipe in group `zaklady` (a **basic**).
- `unit` is a recipe unit from `data/units.yaml`. `difficulty`, `cuisine` and `season` take values from `data/labels.yaml`.
- **Derived, not typed**: allergens (EU 14) and diet (vegetarian, vegan) come from the ingredient catalog. Use the optional fields only to override.
- **No** `course`, `methods`, `equipment`, `uses_basics`, `ingredients`, `tags`, `version` or `archived` fields. Groups replace course and tags. Body links replace the method and equipment lists. `ingredient_groups` replaces the ingredient list and `uses_basics`.

Body sections, in this order (the ingredient list is rendered from the frontmatter, not written in the body):

1. **Postup**: numbered steps. Link techniques and equipment with `[[slug]]`.
2. **Proč to funguje**: short explanation of the key step.
3. **Varianty a náhrady**.
4. **Skladování a ohřev**.
5. **Poznámky**: the owner's notes from cooking.

A **draft** is published with a "netestováno" badge and a placeholder image. A **tested** recipe must have a photo. The page shows `changes` as "Historie úprav".

### 3.2 Explainers

Catalog entries (one file per section in `catalog/`):

```yaml
# catalog/suroviny.yaml
- slug: onion
  title: Cibule
  summary: "One line."
  category: vegetables
  season: all-year             # or month numbers, e.g. [6, 7, 8]; drives the calendar
  substitutes: [shallot, leek]
  allergens: []                # EU 14 slugs
  animal: none                 # none | dairy | egg | honey | fish | meat (drives diet)
  density: 1.0                 # optional, g/ml, only for the unit converter

# catalog/metody.yaml
- slug: braising
  title: Dušení
  summary: "One line."
  category: moist-heat
  related: [stewing, confit]
```

Equipment and troubleshooting entries have `slug`, `title`, `summary`, and optional `category` and `related`. Every `category` value needs a Czech label in `data/labels.yaml`.

Body sections:

- **Method**: principle (what happens to the food), when to use it and when not, procedure, typical mistakes.
- **Ingredient**: description, types, how to choose, how to store, how to prepare, substitutes.
- **Equipment**: purpose, how to choose, care, substitutes.
- **Troubleshooting**: symptom, likely causes, fix, prevention.

The build adds "Použito v receptech" (backlinks) and related lists to each explainer.

### 3.3 Groups

`catalog/skupiny.yaml` lists every recipe group with a `kind`:

```yaml
- { slug: zaklady, kind: course, title: Základy, summary: "Vývary, omáčky, těsta." }
- { slug: priloha, kind: course, title: Přílohy }
- { slug: salat, kind: course, title: Saláty }
- { slug: vanoce, kind: occasion, title: Vánoce }
```

Kinds: `course` (what the dish is) and `occasion` (when you make it). The build rejects an unknown group and makes one page per group.

## 4. Linking

- In any body: `[[slug]]` or `[[slug|text]]`. Slugs are unique across all sections. The build fails on an unknown slug.
- A recipe's methods, equipment and troubleshooting links come from its body links. Its ingredients and basics come from `ingredient_groups`.
- Every written page must have at least one incoming link.
- Links to planned pages are allowed and show as secondary.

## 5. Data files

| File | Content |
|---|---|
| `catalog/suroviny.yaml`, `metody.yaml`, `vybaveni.yaml`, `reseni-problemu.yaml` | Explainer entries |
| `catalog/skupiny.yaml` | Recipe groups: `slug`, `kind`, `title`, optional `summary` and `color` (chip colour) |
| `data/units.yaml` | Units: slug, Czech forms (1 / 2–4 / 5+ / decimals), `scalable`, `round` steps, `ml` or `g` per unit for the converter; US units are converter-only (`in_recipes: false`) |
| `data/allergens.yaml` | The EU 14 allergens with Czech names |
| `data/labels.yaml` | Czech labels for difficulty, season, diet, cuisine and catalog categories; the build rejects a value missing here |
| `data/site.yaml` | Site name, tagline, public URL (for JSON-LD), licence |

Not in the first phase: USDA nutrition values, Wikidata ids, Open Food Facts.

## 6. Features

- Cross-links and backlinks generated at build time.
- **Hover previews** on every internal link (title, summary, banner or photo, status).
- **Search and filters** from one generated JSON index: full-text search (Czech diacritics folded) and recipe list filters by group, season, diet, allergen, difficulty, time, cuisine.
- **Serving scaler** on recipe pages, using `units.yaml` rules for rounding and Czech plural forms.
- **schema.org/Recipe JSON-LD** on every recipe page.
- **Print view** for recipes.
- **Reference page**:
  - Unit converter: US units and °F to metric, spoons to grams by ingredient density.
  - Seasonal calendar: a grid with months as columns and ingredients as rows; cells coloured when the ingredient is in season; filterable by category. Generated from catalog `season`.
  - Later: doneness temperatures and storage times, each with a cited food-safety source.

## 7. Images

- **Explainers**: every written explainer needs a hand-drawn SVG banner `banners/<slug>.svg`, 3:1, colours only through CSS variables. Animation is allowed and must stop under `prefers-reduced-motion`. Planned pages share one placeholder banner.
- **Recipes**: own photos only. Required for `tested`. An import script shrinks the original (about 2000 px long side, WebP) before commit; the build makes smaller sizes. Originals stay outside the repository.

## 8. Authoring workflow

Adapted from the trading site's pipeline:

- Skills `write-recipe` and `write-explainer` run the agents, build, check the page in the browser and commit.
- Agents: **writer**, **illustrator** (banners), **reviewer** (read-only, conventions and links), **fact-checker** (read-only, food-safety numbers and technical claims).
- Recipe drafts:
  1. The corpus-lookup script returns 5–10 variants of the dish from the private corpus.
  2. The writer compares them (ratios, temperatures, times) and writes a new recipe in the owner's style, metric units, `status: draft`.
  3. A near-copy check compares the draft text with the variants. No sentence may be a near-copy.
  4. The owner cooks it, edits it, adds a photo and a `changes` entry, and sets `status: tested`.

**Corpus**: TheMealDB first, loaded into SQLite. It is private reference material, never published. It lives outside the repository or in a git-ignored folder.

## 9. Guardrails

- **Copyright**: take ideas, write new text. Ingredient lists are usually not protected; method text, photos and stories are. Do not reproduce large parts of one collection (EU database right).
- **Accuracy**: drafts are marked "netestováno"; only tested recipes are the core of the site.
- **Food safety**: temperatures and storage times must cite a food-safety authority. Never invent numbers.
- **Allergens**: the EU 14: cereals containing gluten, crustaceans, eggs, fish, peanuts, soybeans, milk, nuts, celery, mustard, sesame, sulphur dioxide and sulphites, lupin, molluscs.

## 10. Stack

- **Generator**: custom Python script, same approach as the trading site. Python with uv; `jinja2`, `markdown`, `pyyaml`, `Pillow`.
- **Build as linter**: the build checks all data (unknown keys, units, groups, slugs, missing banners or photos) and lists every problem before it fails.
- **Tests**: pytest; the tests also build the real site.
- **Hosting**: GitHub Pages, deployed by a GitHub Actions workflow on push to `main` (tests and build first).
- **Client JS**: plain JavaScript, no framework: search, filters, previews, scaler, converter, calendar, theme switch.

## 11. Status and next steps

Done: the build with validation, links and derived data; recipe, explainer, list, group, reference and about pages in the "Smaltovaný sešit" style (`docs/STYLE.md`); search, previews, filters, scaler, converter and season calendar; photo import; tests; the Pages workflow. Sample content: 3 draft recipes and 3 written explainers.

Next:

1. Corpus lookup script (TheMealDB into SQLite) and the near-copy check.
2. Authoring skills and agents (`write-recipe`, `write-explainer`; writer, illustrator, reviewer, fact-checker).
3. Doneness temperatures and storage times on the reference page, with cited sources.
