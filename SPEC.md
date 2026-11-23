# Cooking site: structure spec for the design

This is the contract between the site's structure (build script, catalogs, content, data, banners, photos) and its design (templates and styles). The design can change any markup and styling, provided that it keeps the data, URLs and hooks below working. The content model and the reasons behind it are in `docs/BRIEF.md`.

Status: the build does not exist yet. This spec states what it will give to the templates. When the build and this spec disagree, fix the one that is wrong in the same change.

## Ownership

| Part | Owner | Files |
|---|---|---|
| Structure | build and content work | `scripts/`, `catalog/`, `data/`, `content/`, `banners/`, `photos/` |
| Design | design work | `templates/*.html`, `static/site.css`, new files in `static/` (fonts, icons) |
| Behaviour | shared | `static/*.js`: the design may restyle or extend it, but must keep the hooks in [Behaviour hooks](#behaviour-hooks) |

## What the site is

A Czech cooking site, built for the owner first and public.

- **Recipes** are the main content. Each recipe is a **draft** (published, marked "netestováno", placeholder image) or **tested** (has a photo).
- **Explainers** support the recipes. There are four **sections**: methods (`metody`), ingredients (`suroviny`), equipment (`vybaveni`) and troubleshooting (`reseni-problemu`). Each explainer is **written** or **planned**. A planned explainer has a title, a one-line summary and a shared placeholder banner. Links to it work. It should look clearly secondary but still be reachable.
- **Groups** sort recipes. Each group has a **kind**: `course` (Přílohy, Saláty, Základy...) or `occasion` (Vánoce, Rychlá večeře...).
- **Basics** are recipes in the group `zaklady` (stocks, sauces, doughs). Other recipes use them as ingredients.

Expect tens of recipes and a hundred or more explainers, most of them planned at first.

## Pages and URLs

All URLs are relative. Every template gets `root` and must put it before every internal link and asset. The site is served under a sub-path on GitHub Pages and from `dist/` locally, so a link that starts with `/` breaks.

| Page | URL | Template | Purpose |
|---|---|---|---|
| Home | `index.html` | `home.html` | Intro, newest recipes, groups, sections |
| Recipe list | `recepty/index.html` | `recipes.html` | All recipes, with search and filters |
| Recipe | `recepty/<slug>.html` | `recipe.html` | One recipe |
| Section | `<section>/index.html` | `section.html` | All explainers of one section, in catalog order, written first |
| Explainer | `<section>/<slug>.html` | `explainer.html` | One explainer, written or planned |
| Groups | `skupiny/index.html` | `groups.html` | All groups, sorted by kind |
| Group | `skupiny/<slug>.html` | `group.html` | Recipes in one group |
| Basics | `zaklady/index.html` | `group.html` | Same page as `skupiny/zaklady.html`, at a short URL |
| Reference | `reference/index.html` | `reference.html` | Unit converter and seasonal calendar |
| About | `o-webu/index.html` | `about.html` | Licence, credits, how the site is made |

### Recipe page

Photo (or placeholder with "netestováno" badge for a draft) → groups → title → summary → facts (servings, active and total time, difficulty, cuisine, season, diet, allergens) → **Suroviny** (rendered from data, with the serving scaler) → body (Postup, Proč to funguje, Varianty a náhrady, Skladování a ohřev, Poznámky) → **Použité metody a vybavení** (explainers linked from the body) → **Historie úprav** (changes, newest first). It must print well: photo small or hidden, no navigation, ingredients and steps on as few pages as possible.

### Explainer page

Banner (full width, the main visual of the page) → section label → title → summary → body → **Související** (explainers this page links to, plus catalog `related` and `substitutes`) → **Použito v receptech** (recipes that link here or use the ingredient). A planned explainer has no body, only a "zatím nenapsáno" note; it can already have recipe backlinks.

Ingredient pages also show catalog data: category, season (as a 12-month strip), substitutes, allergens.

### Reference page

- **Unit converter**: amount + from-unit → to-unit; optional ingredient for spoon/cup to grams.
- **Seasonal calendar**: a grid. Columns are months 1–12, rows are ingredients. A cell is coloured when the ingredient is in season. A category filter and a text filter hide rows. Row titles link to ingredient pages. It must stay usable at phone width (the grid scrolls inside itself, the first column stays visible).

### Card

Used in lists and grids:

- **Recipe card**: photo or placeholder, title, summary, total time, "netestováno" for drafts.
- **Explainer card**: banner (scaled down), section label, title, summary, "zatím nenapsáno" for planned.

## Template data

Templates are Jinja2 (`StrictUndefined`, autoescape on). Every template receives:

| Name | What |
|---|---|
| `site.recipes` | list of recipe pages, newest change first |
| `site.sections` | list of sections: `slug`, `title`, `url`, `pages` (explainers in catalog order), `written_count` |
| `site.groups` | list of groups: `slug`, `kind`, `title`, `summary`, `url`, `recipes` |
| `site.pages` | dict slug → page, every recipe and explainer |
| `site.units` | dict unit slug → unit |
| `site.allergens` | list of the EU 14: `slug`, `title` |
| `root` | relative prefix to the site root |
| `current` | this page's URL relative to the root |
| `title` | text for `<title>` |

A **page** has `kind` (`recipe`/`explainer`), `slug`, `title`, `summary`, `url`, `links` (slugs linked from the body), `backlinks` (slugs that link here).

A **recipe** page also has: `status` (`draft`/`tested`), `photo` (dict of sizes → URL, or none), `servings`, `time_active_min`, `time_total_min`, `difficulty`, `cuisine`, `season`, `groups` (slugs), `diet`, `allergens` (derived), `ingredient_groups` (each item: `qty`, `unit`, `item`, `note`, `text`, `display` (Czech text for the base servings)), `changes`, `jsonld` (string, output with `| safe` in a `<script type="application/ld+json">`).

An **explainer** page also has: `section`, `status` (`written`/`planned`), `banner_svg` (inline SVG, output with `| safe`), `category`, and the section's catalog fields (`season`, `substitutes`, `allergens`, `animal` for ingredients; `related` for methods).

Page templates also receive: `recipe.html` and `explainer.html` → `page` and `body` (rendered HTML, output with `| safe`); `section.html` → `section`; `group.html` → `group`.

## Body content

Markdown rendered to HTML: `h2`/`h3`, paragraphs, `ul`/`ol`, `table`, `strong`/`em`, and inline links. Style it under `.prose`. Recipe steps are an `ol` and should be easy to follow while cooking (large numbers, space between steps).

## Banners

- Every written explainer has its own hand-drawn SVG, inlined into the page. Planned explainers share `banners/_planned.svg`.
- Canvas: `viewBox="0 0 1200 400"` (3:1). Full width at that ratio on explainer pages; cards show the same SVG scaled down.
- Colours only through CSS custom properties that the design defines for light and dark themes: `--banner-bg`, `--banner-fg`, `--banner-accent`, `--banner-warm` (heat, browning), `--banner-cool` (cold, fresh). Each with a light fallback: `style="fill: var(--banner-bg, #f6f3ee)"`. The design may ask for other variables; the banners follow.
- Animation is allowed (CSS in the SVG). It must stop under `@media (prefers-reduced-motion: reduce)`.
- No `id` attributes in banners: many are inlined on one page.

## Photos

Recipe photos come in sizes made by the build (for example 400, 800, 1600 px wide, WebP). Use `srcset` from `page.photo`. Display ratio is the design's choice; the photographer will frame for a 3:2 centre crop.

## Behaviour hooks

Plain JavaScript in `static/`. Keep these classes and attributes, or update the scripts with the markup.

| Feature | Hook |
|---|---|
| Data | `static/index.js` (generated) sets `window.SITE_INDEX = {pages, groups, sections, units, banners}`. Each page entry has `slug, kind, title, summary, url, status, section?, groups?, season?, diet?, allergens?, difficulty?, time_total_min?, cuisine?, photo?, banner?`. Load it before the other scripts. |
| Root | `<html data-root="{{ root }}">` |
| Internal links | `a.site-link[data-slug]` with `is-written`/`is-planned`/`is-draft`/`is-tested`. Body links come from the build, so these class names are fixed. |
| Hover preview | one hidden `.link-preview` that the script fills with `.link-preview__media` (banner or photo) and `.link-preview__text` (`__section`, `__title`, `__summary`, `__status`) |
| Search | `.search` with `input.search__input` and `ol.search__results` > `li.search__result` > `a.search__link` > `.search__title` + `.search__meta`, or `li.search__empty` |
| Filters | `form.filters` on the recipe list; each control has `name` = a filter key (`group`, `season`, `diet`, `allergen`, `difficulty`, `time`, `cuisine`). Recipe cards in the list carry `data-slug`; the script hides the ones that do not match with `hidden`. |
| Scaler | `.scaler` with `input.scaler__servings[data-base]`; each ingredient amount is `.ing__amount[data-qty][data-unit]`, which the script rewrites with Czech unit forms |
| Converter | `.converter` with `input.converter__amount`, `select.converter__from`, `select.converter__to`, `select.converter__item`, `output.converter__result` |
| Calendar | `table.season` with `tr[data-slug][data-category]`, `td.is-in-season`; filter controls `input.season__search`, `select.season__category` |
| Status | `.is-written`/`.is-planned`/`.is-draft`/`.is-tested` on cards, links and the article |
| Page kind | `body.page-home|recipes|recipe|section|explainer|groups|group|reference|about` |
| Theme switch | `button.theme[data-theme-current=system|light|dark]`, as on the trading site; choice kept in `localStorage` |

## Constraints

- Public static site on GitHub Pages. Keep everything as local files in `static/`. External stylesheets only from Google Fonts; scripts only from cdnjs, jsdelivr or unpkg, pinned. Prefer none.
- Must work at phone width (16px side gutter, no horizontal page scroll) and in light and dark mode.
- Pages must be readable without JavaScript. Search, filters, previews, the scaler, the converter and the calendar filter need it.
- UI text is Czech and addresses the reader informally (tykání: "Hledej", "Přepočítej porce", "Zkus jiný filtr"), never with vykání ("Hledejte", "Vaše").
