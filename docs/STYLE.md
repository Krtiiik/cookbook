# Visual style: "Smaltovaný sešit"

The site's look. It mixes a kitchen notebook (hand-drawn type, tape, polaroids, dotted paper) with the colours of Czech enamel kitchenware (tomato, mint, mustard, cobalt). The reference prototypes are the `hy-*` artboards (row D) on the design canvas: https://claude.ai/artifact/CadNEin9R24pkFQju8KEnH. `SPEC.md` gives the hooks and data; this file gives the look.

## Principles

1. **Colour goes on elements, never behind text.** Do not use highlighter or marker backgrounds on words (the owner rejected this). Put colour on tape strips, offset shadows, dots, discs, bars, buttons and photo placeholders.
2. **Ink borders are bold.** All outlines are 2.5px in `--ink`. Dashed lines inside a box are 1.5px in `--line`.
3. **Hand-made, not messy.** Corners use slightly uneven radii, and tape and stickers are rotated a few degrees. Text is never rotated, except the stickers and the converter result.
4. **Status is quiet.** Drafts get a mustard "netestováno" sticker. Planned explainers get a dashed `--pencil` outline, faded tape, no shadow and muted text. They must stay easy to read and click.
5. **Dense.** Lists and grids show a lot per screen. Reading text keeps a 66–70ch measure.
6. **Czech UI text uses tykání** ("Hledej", "Zkus jiné slovo", "Přepni").

## Tokens

### Fonts

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Caveat:wght@400;600&family=Patrick+Hand&display=swap">
```

| Token | Family | Use |
|---|---|---|
| `--font-hand` | `'Patrick Hand', cursive` | Logo, headings, card titles, nav items, chips |
| `--font-note` | `'Caveat', cursive` (600) | Small handwritten labels: fact names, section labels, dates, stickers, step numbers, theme label, converter result |
| `--font-body` | `'Atkinson Hyperlegible', system-ui, sans-serif` | Body, lists, forms, meta |

All three fonts cover Czech diacritics (latin-ext). If the site must not load Google Fonts, self-host them in `static/fonts/` (all three use the OFL licence).

### Colours

```css
:root {
  /* light: Smalt cream */
  --paper:   #f5efe3;              /* page */
  --dot:     rgba(31,79,163,.24);  /* dotted paper */
  --card:    #fffaf0;              /* boxes, cards */
  --ink:     #1b2a4a;              /* text and all outlines */
  --ink2:    #34405c;              /* secondary text */
  --muted:   #55607a;              /* meta, planned text */
  --pencil:  #8a93ab;              /* dashed outlines of planned items (not for text) */
  --line:    #ddd3c0;              /* dashed separators */
  --accent:  #b8361c;              /* Caveat labels as TEXT colour (4.5:1 on cream) */
  --tomato:  #c8462a;  --on-tomato: #fff7ea;
  --mint:    #a3d4c0;
  --mustard: #e9b44c;
  --cobalt:  #1f4fa3;  --on-cobalt: #fff7ea;
  --fill-ink:#1b2a4a;              /* text on mint/mustard fills, both themes */
  --season:  #6fb597;  --empty: #efe7d6;   /* season grid */

  /* banners (SPEC.md) */
  --banner-bg:#fffaf0; --banner-fg:#1b2a4a; --banner-accent:#c8462a;
  --banner-warm:#e9b44c; --banner-cool:#1f4fa3;
}
:root[data-theme="dark"] {           /* also inside @media (prefers-color-scheme: dark) for "system" */
  /* dark: technical near-black */
  --paper:#0f1012; --dot:rgba(235,235,232,.13); --card:#17191c;
  --ink:#ebebe8; --ink2:#c9c9c5; --muted:#9c9c98; --pencil:#62666d; --line:#2e3135;
  --accent:#ff8a6a;
  --tomato:#e5603f; --on-tomato:#1a0d08;
  --mint:#5fae92; --mustard:#f0b84a;
  --cobalt:#7fa6ee; --on-cobalt:#0f1012;
  --fill-ink:#111214;
  --season:#4f9a7c; --empty:#202327;
  --banner-bg:#17191c; --banner-fg:#ebebe8; --banner-accent:#e5603f;
  --banner-warm:#f0b84a; --banner-cool:#7fa6ee;
}
```

In dark mode the enamel colours get lighter but keep their hues. Text on a coloured fill uses `--on-tomato`, `--on-cobalt` or `--fill-ink`. Never use `--tomato` as a text colour on paper. Use `--accent` for that.

**Section colour.** Each section has one enamel colour. Set it as `--c` on the section's elements:

| Section | `--c` |
|---|---|
| Metody (`metody`) | `--tomato` |
| Suroviny (`suroviny`) | `--mint` |
| Vybavení (`vybaveni`) | `--mustard` |
| Řešení problémů (`reseni-problemu`) | `--cobalt` |

Helper classes in the prototypes: `.c-tomato{--c:var(--tomato)}` and the same for mint, mustard and cobalt. Recipe cards cycle through the 4 colours in list order, so the grid is mixed but calm. Group chips get a colour by kind of meaning (the colour is decoration, not data).

### Dotted paper

```css
body {
  background-color: var(--paper);
  background-image: radial-gradient(var(--dot) 1.3px, transparent 1.8px);
  background-size: 22px 22px;
}
```

### Type scale (desktop / phone)

| Role | Font | Size |
|---|---|---|
| Home hero h1 | hand | 62px / 44px, line-height 1.02 |
| Page title (recipe, explainer, tool pages) | hand | 60–66px / 42–46px, line-height 1 |
| Section h2 (`.h2`, prose h2) | hand | 34px |
| Box h2 (ingredients, side boxes) | hand | 26–32px |
| Card title | hand | 22–23px |
| Nav item | hand | 22px |
| Logo | hand 34px |
| Labels, dates, fact names | note 600 | 17–21px |
| Body | body | 16px / 1.5; prose 17px / 1.6 |
| Lead (summary under title) | body | 18–19px, `--ink2` |
| Meta, small | body | 13–14px |

### Spacing, radii, borders, shadows

- Content width: `max-width: 1216px`, side padding 32px (16px on phone).
- Section gap: 48–52px. Grid gap: 26px rows, 22px columns.
- Border: `2.5px solid var(--ink)`. Inner separators: `1.5px dashed var(--line)`.
- Uneven radii: boxes `5px 8px 6px 9px` (or similar), pills `22px 18px 24px 20px`, step discs `50% 45% 52% 48%`.
- Offset shadow (no blur): `5px 5px 0 var(--c)`. Use 6–7px for large boxes (photo, banner, ingredients), and 3px for small controls (`3px 3px 0 var(--mustard)` on the theme button).
- Tape: an `::before` 70–96 × 20–24px, `background: var(--c)`, `opacity: .85`, `border-radius: 2px`, rotated −4° to 3°, top −10px. Faded to `.3–.35` on planned items.
- Circle dot marker: 10–16px circle, `background: var(--c)`, `border: 2–2.5px solid var(--ink)`. It goes before headings, chips, section labels and list items.

## Components

### Header and navigation

- **Top row:** logo, search, theme switch. No rule under it: the nav's ink rule closes the header.
  - **Logo:** a 44px tomato circle with a white icon of a chef's hat on a molehill (a nod to "Krtkova") (inline SVG, `aria-hidden`), then "Krtkova Kuchařka" (hand 34px).
  - **Search** `.search`: a pill input with a 2.5px ink border on `--card` and a magnifier icon inside on the left. The placeholder is "Hledej recept, surovinu, postup…". Results (`ol.search__results`) open below it as a card with a 5px mustard shadow.
  - **Theme switch** `button.theme[data-theme-current]`: a cobalt-filled pill (`--on-cobalt` text) with a 3px mustard shadow. It cycles system → light → dark. The icon is a half-filled circle, a sun or a moon. The label is "Auto", "Světlý" or "Tmavý" in Caveat. Its `aria-label` and `title` are "Motiv: podle systému. Přepni." (and the same for the other states).
- **Nav row: divider tabs** (`a.tab`) standing on a 2.5px ink rule, like the tabs of a notebook's dividers. Each tab is `--card` with a 2.5px ink border (no bottom), a 12–14px top radius and a 6px stripe of its section colour along the top (Recepty ink, Metody tomato, Suroviny mint, Vybavení mustard, Řešení problémů cobalt). Hand 22px.
  - **Secondary tabs** (`.tab--more`: Skupiny, Převodník, Sezónní kalendář, O webu) sit at the right: smaller (hand 18px), `--ink2`, with a `--pencil` stripe, because they are pages, not colour-coded sections.
  - **Current page** (`.tab.on`): rises to 58px, gets a 10px stripe and a `--paper` fill whose bottom covers the rule, so the tab joins the page below. The font and width stay the same, so no tab moves sideways when you change pages, and the nav keeps one height. This replaces the old underline bar. Still no highlight behind the word.
  - **Rejstřík** (narrow screens): `button.stack` is four divider tabs one behind the other, each 6px right and 4px higher, so the back one reaches the height of the current tab (front `--card` with a menu icon, then mustard, mint, cobalt). It opens `#rejstrik`, a list of index cards: the five sections full width with a 9px colour edge on the left, the current one pushed out with a 4px ink shadow and "tady jsi" in Caveat, then the secondary pages in two columns. When open, the front tab joins the page and shows a cross.

### Links (`a.site-link`)

| Status | Look |
|---|---|
| written / tested | underline 2px `--tomato`, offset 3px |
| draft | the same, but `text-decoration-style: dashed` |
| planned | dotted underline in `--pencil`, text `--muted` |

### Cards (`.card`)

- `--card` background, 2.5px ink border, uneven radius, `5px 5px 0 var(--c)` shadow, a tape strip centred on the top edge in `--c`.
- **Recipe card:** the photo (3:2, 2px ink border), title, summary (14px `--ink2`) and meta pills (1.5px `--line` border, for example "⏱ 3 h", group).
  - **No photo yet (draft):** a dashed `--pencil` box with "zatím bez fotky" in Caveat, plus the sticker.
  - **Photo placeholder** (before real photos): mint fill with white enamel dots (`radial-gradient(rgba(255,255,255,.5) 22%, transparent 23%)`, 18–22px).
  - **"netestováno" sticker:** absolutely positioned top right, overlapping the edge (`right:-10px`). Mustard fill, `--fill-ink` text, Caveat 20px, 2px ink border, `2px 2px 0 var(--tomato)` shadow, rotated 4°.
- **Explainer card:** the banner scaled down (2px ink frame), a section label (dot + Caveat, `--accent`), title and summary. Ingredient cards show the small category pill instead of the label, because "suroviny" would repeat on every card of the section.
  - **Planned:** dashed `--pencil` border, transparent background, no shadow, faded tape, dashed banner frame, muted text, plus "zatím nenapsáno" in Caveat.

### Home

- **Hero:** h1 "Co dnes uvaříme?" and a row of 4 colour dots (tomato, mint, mustard, cobalt) as decoration. On the right is "Poslední úpravy", a card with a tomato tape strip and a mustard shadow, listing the latest `changes` (date in Caveat `--accent`, title link, note).
- **"Nejnovější recepty":** a grid of 4 columns (8 cards), with no count next to the heading.
- **"Jak a proč":** 4 section boxes, each in its section colour (tape, shadow, progress bar fill). Each box has the title, a bar "napsáno N z M" (10px, 2px ink border, paper background), and 4 explainer links. Planned links get "zatím nenapsáno" in Caveat.
- **"Skupiny":** 2 columns, "Druh jídla" (course) and "Příležitost" (occasion). Chips are 44px pills with a colour dot.

### Recipe page

Order as in SPEC.md. Desktop layout:

1. **Top:** 2 columns (1.2fr / 1fr).
   - **Left: polaroid** `figure`. Card padding 12px with 6px at the bottom, 2.5px ink border, `6px 6px 0 var(--mint)` shadow, rotated −1°. A tomato tape strip is on the left corner and a mustard one on the right. The caption is in Caveat ("uvařeno 20. 11. 2026").
   - **Draft:** the photo is replaced by the dashed "zatím bez fotky" box, and the "netestováno" sticker goes on the polaroid.
   - **Right:** group chips, title, summary, then the **facts** table.
   - **Facts:** a `dl` grid of 3 columns on a card with a mustard shadow and dashed cell separators. `dt` in Caveat `--accent`, `dd` in body bold.
   - Under the facts: the status line, a mint dot + "otestováno, N úpravy" (or a dashed dot + "netestováno").
2. **Body:** 2 columns (370px / 1fr).
   - **Left: Suroviny**, sticky (`top: 14px`). Card, cobalt shadow, mustard tape.
     - **Scaler** `.scaler`: label "porce" (Caveat), cobalt −/+ round buttons (44px, ink border), and the `input.scaler__servings` as a pill on paper.
     - **Ingredient groups:** each group name in Caveat `--muted`. Each row is a grid (92px right-aligned bold amount, then the name link and a `, note` in muted).
     - **Basic:** a basic (`zaklady`) gets a small mustard "základ" tag, rotated −2°.
   - **Right: prose.** Each h2 has a colour dot (Postup tomato, Proč to funguje mint, Varianty mustard, Skladování cobalt, Poznámky tomato).
     - **Steps** (`ol`): 50px tomato discs with the number in Caveat 32px, `--on-tomato`, a 2.5px ink border and a `3px 3px 0 var(--mustard)` shadow. Each step has 70px left padding and a dashed separator.
     - **Poznámky:** a note card in Caveat 24px with a mint shadow and a cobalt tape strip, rotated −0.6°.
3. **"Použité metody a vybavení":** explainer cards, 4 columns.
4. **"Historie úprav":** a list. Each row has a dot (tomato for the newest, mint for older ones), the date in Caveat `--accent` (120px) and the note.

**Print:** hide the search, theme switch, nav, footer, scaler buttons and link preview. Make the polaroid at most 200px wide, with no rotation and no shadow. Keep the ingredients and steps. Use a white background.

### Link preview (`.link-preview`)

A card 340px wide: 2.5px ink border, mustard shadow, uneven radius. A grid with the banner (120px wide, 2px ink frame) on the left. The text is on the right: `__section` in Caveat `--accent`, `__title` in hand 21px, `__summary` 14px `--ink2`, `__status` 12px `--muted` ("napsáno", "zatím nenapsáno", "netestováno"). The prototypes place it under the hovered step. In the real site, one shared element is positioned by the script near the link.

### Explainer page

- **Banner:** full content width, 3:1. Frame: 2.5px ink border, `7px 7px 0 var(--tomato)` shadow (use the section's colour), uneven radius, and 2 tape strips (mustard on the left, mint on the right).
  - **Planned:** a dashed `--pencil` frame, no shadow, tape at 30% opacity.
- **Head:** the section label (dot + Caveat 24px, `--accent`, links to the section), the title (hand 66px) and the lead. On the right is a status pill: mint dot + "napsáno", or dashed + "zatím nenapsáno".
- **Body:** 2 columns (1fr / 350px).
  - **Prose:** h2 with a colour dot. An `ol` uses 36px cobalt discs. A table sits in a card with a mustard shadow: `th` in Caveat `--accent`, rows with dashed separators. Wrap tables in an `overflow-x: auto` box.
  - **Planned:** the body is replaced by a dashed box with "zatím nenapsáno" (Caveat 32px) and one line: "Tahle stránka je v plánu. Odkazy na ni už fungují a vpravo vidíš recepty, které ji používají."
  - **Side:** "Související" (mint box) and "Použito v receptech" (mustard box). Each is a card with tape and a shadow in the box colour.
    - **Related items:** each has a dot in the item's section colour, a link and the section name under it. Planned items get a dashed empty dot and "zatím nenapsáno".
    - **Backlinks:** each has a 72px 3:2 thumbnail (mint dots, or dashed if there is no photo) and a link. Drafts get the mustard "netestováno" tag. Under it: time · group.
- **Category pill** (ingredient categories): a paper pill with a 2px ink border, a 2px offset shadow in the category colour, and a 24px colour disc with a hand-drawn icon, then the label in hand 18px. The colour is per family: mint for plants (zelenina, ovoce, bylinky, houby), tomato for animals (maso, ryby, vejce), mustard for grain and fat (mouka a obiloviny, ořechy a semínka, tuky), cobalt for the rest (mléčné výrobky, koření, spíž). The text stays on paper; colour is only on the disc and the shadow. The small version (hand 15px, 18px disc) is for cards and calendar rows. A new category needs its colour and icon in the template macro.
- **Ingredient explainers** also show the catalog data (category, a 12-month season strip in the season-grid style, substitutes, allergens) in a box between the head and the body. This is not in the prototype yet. Use the box style above with a mint colour.

### Banner drawing style

Banners follow SPEC.md (viewBox 1200×400, colours only through `--banner-*`, no `id`).
- **Drawing:** ink outlines (`--banner-fg`, stroke 5–6) with flat enamel fills (`--banner-accent` body, `--banner-cool` lid, `--banner-warm` flame). Add white enamel dots on the pot and Caveat annotations with thin curved leader lines.
- **Animation:** only gentle steam (opacity and translateY, 3.4s, staggered). It keeps running under `prefers-reduced-motion: reduce`.
- **`_planned.svg`:** a dashed rounded frame at 35% opacity, a few faded dots and a faded pencil outline.

### Converter and calendar pages

- **Layout:** each tool has its own page: the page title, a short lead, then one box. The converter is a tomato box, at most 460px wide; the calendar is a mint box at full width. Each box is a card with tape and a shadow.
- **Fields:** a Caveat label above, then an input or select with a 2.5px ink border, a paper background and an uneven radius of about 12px. Minimum height 44px.
- **Converter result** (`output.converter__result`): a mustard sticker with `--fill-ink` text in Caveat 36px, a 2.5px ink border and a `4px 4px 0 var(--tomato)` shadow, rotated −1°. Messages: "Zadej číslo", "Zvol °C", "Zvol g nebo ml". The hint is "Surovinu potřebuješ jen pro převod objemu na hmotnost."
- **Season grid** (`table.season`):
  - **Table:** `border-collapse: separate; border-spacing: 3px` inside a scroll box (2px ink border, `--card`).
  - **Cells:** 32px tall, uneven radius, `--empty` background. In season (`td.is-in-season`): `--season` fill with an inset 2px ink outline. The current month column gets a 2.5px tomato outline, and its header is in `--accent`.
  - **Headers:** month headers are 3-letter Czech abbreviations in Caveat (led, úno, bře, dub, kvě, čvn, čvc, srp, zář, říj, lis, pro), with `abbr title` holding the full month name.
  - **Row title** `th[scope=row]`: sticky on the left with a `--card` background, a dashed right border, the link and the small category pill under it.
  - **Filters:** `input.season__search` ("Hledej surovinu", placeholder "např. dýně") and `select.season__category` ("všechny", zelenina, ovoce, bylinky, houby, ryby). A legend sits above the table, with a count "N z M surovin".
  - **No results:** "Nic nenalezeno. Zkus jiné slovo." in Caveat.

### Recipe list filters (`form.filters`)

This page is not in the prototype. Use the converter field style: Caveat labels and bordered pill controls, in a card with a cobalt shadow. Put the controls in a wrapping row on desktop. On a phone, collapse the form into a `<details>` with the summary "Filtry". The text for no results is "Nic neodpovídá. Zkus jiný filtr." The whole card opens and shuts with an accordion fold: the summary row stays flat, the part below folds in four strips that tilt back and forth like folded paper, and the bottom edge rides along (about 0.5s). A click during the fold turns it back. The arrow turns with the fold. When shut or open and still, it is one complete card; the bottom edge folds up and lands under the summary.

### Footer

A 2.5px ink rule on top, 14px muted text: "© Krtkova Kuchařka · obsah pod licencí CC BY-NC-SA 4.0", then links to Převodník, Sezónní kalendář and O webu.

## Phone width (≤ 600px)

The prototypes use container queries only so the phone artboards work. The site should use the same breakpoints as media queries: 980px and 600px.

**At 980px and below:**
- Hero, recipe top, recipe body and explainer body become 1 column.
- The ingredients box stops being sticky.
- Grids of 4 become 2 columns.

**At 600px and below:**
- **Side padding:** 16px.
- **Header:** wraps. The search drops to its own full-width row (`order: 3`).
- **Nav:** at 1200px and below the secondary tabs move into the Rejstřík; at 820px and below only the current tab and the Rejstřík button stay. Without the script all tabs stay and wrap.
- **Grids:** 1 column.
- **Titles:** 42–46px. The hero h1 is 44px.
- **Facts:** 2 columns.
- **Steps:** 44px discs and 60px left padding.
- **Link preview:** full width under the step.
- **Historie úprav:** the date sits above the note.
- **Season grid:** it scrolls inside its box, the row titles stay visible (min-width 104px), and there is no horizontal page scroll.
- **Touch targets:** at least 44px (buttons, chips, inputs).

## Not obvious from the markup

- **Theme switch:** the prototypes store the choice in `localStorage` under the key `kk-theme`, with the values `system`, `light` and `dark`. A missing value means `system`. Apply the theme before first paint (a small inline script in `<head>`) so the page does not flash. The system theme also follows live changes of `prefers-color-scheme`.
- **Amounts:** the prototype scaler rounds g to 10 (≥100 g) or 1, ml to 10 (≥100 ml) or 5, and spoons to 0.5. It shows a decimal comma and uses Czech plural forms (1 / 2–4 and decimals / 5+): lžíce/lžíce/lžic, lžička/lžičky/lžiček, stroužek/stroužky/stroužků. The real rules come from `data/units.yaml`. "podle chuti" never scales.
- **Search:** fold Czech diacritics for search (NFD, strip combining marks, lower case). The calendar filter already does this.
- **Colour meaning:** section colours are only for orientation. Status is always shown by the outline style and a word, never by colour alone.
- **Content:** sample content in the prototypes (counts, densities, the guláš recipe) is placeholder data, not facts for the site.
