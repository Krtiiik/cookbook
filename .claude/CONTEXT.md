# Context

<!--
Glossary for Claude: the terms and top-level concepts this project uses with a specific meaning.
- Define a term only if it means something particular here; skip ordinary words.
- One or two sentences each. Say what it is, not where it lives in the code.
- Keep the whole file short enough to read every session.
-->

## Language

**Recipe**: the main content: one dish, with structured ingredients, steps and the owner's notes.
_Avoid_: dish page, post.

**Explainer**: a supporting page in one of four sections: method, ingredient, equipment, troubleshooting.
_Avoid_: concept, article, wiki page.

**Section**: one of the four explainer kinds (`metody`, `suroviny`, `vybaveni`, `reseni-problemu`).
_Avoid_: category (that is a field inside a section).

**Catalog**: the per-section list of explainers (slug, title, summary, data), plus the list of groups. It is also the roadmap.

**Written / planned**: an explainer is written when its body file exists, planned when it is only in the catalog.
_Avoid_: stub, draft (for explainers).

**Draft / tested**: a recipe's status. A draft is published but marked "netestováno"; a tested recipe was cooked and has a photo.
_Avoid_: unpublished, final.

**Group**: a named set of recipes, defined in the catalog, with a kind.
_Avoid_: tag, collection, category.

**Kind**: what a group sorts by: `course` (what the dish is) or `occasion` (when you make it).

**Basic**: a recipe in the group `zaklady` (stock, sauce, dough) that other recipes use as an ingredient.
_Avoid_: sub-recipe, component.

**Ingredient item**: one line of a recipe's ingredient list: amount, unit, ingredient or basic slug, note.

**Unit**: one entry of the fixed unit list, with Czech forms and scaling rules.

**Banner**: the hand-drawn SVG header of an explainer.

**Corpus**: the private recipe dataset used only as reference when drafting. Never published.

## Relationships

- A **recipe** has **ingredient items**; each names an ingredient explainer or a **basic**.
- A **recipe** links to method, equipment and troubleshooting **explainers** from its body; each explainer lists the recipes that link to it.
- A **recipe** is in one or more **groups**; each group has one **kind**.
- A recipe's allergens and diet are derived from its ingredients' catalog data.

## Ambiguities

- "Základy" is a **group** (kind `course`), not a section.
- "Draft" is only a recipe status. A missing explainer is **planned**.
- "Kategorie" in the catalog is a field inside a section (vegetables, moist-heat), not a group.
- **Owner page**: the one explainer that explains an idea in full; other pages give one sentence and link it. Maillard reaction and výpek: `browning`. Onion colour stages: `caramelising`. Softening without colour: `sweating`. Liquid states (chvění, mírný var, prudký var): `simmering`. Slow cooking in a little liquid, and collagen turning to gelatin: `braising`. Tough vs dry braised meat, the fork test and the rescue: `tough-stew`. How to add ground paprika: `sweet-paprika`. Burnt paprika and its bitterness: `bitter-paprika`. Braising time of a cut: that cut's own page (`beef-shank`, `beef-chuck`, `beef-cheeks`, `oxtail`); other pages compare in a few words and do not repeat the oven setting. Oven braising at 140–150 °C: `braising`. Smoke points (kouřový bod) and which fat takes which heat: `oil`. Clarified butter: `butter`. Rendering lard: `lard`. Safe core temperatures and using a thermometer: `thermometer`. Cutting technique and knife care: `chefs-knife`. Heating and using the cast-iron pot: `dutch-oven`. Butter heat stages and oříškové máslo: `butter`. Frying-oil reuse and oil fires: `oil`. Reheating temperature: `thermometer`. Smoked-paprika kinds and dosing: `smoked-paprika`. Hot-paprika grades and dosing: `hot-paprika`. Burnt onion and telling it from burnt paprika: `burnt-onion`. Softening bitterness in a finished dish: `bitter-paprika`. The too-much-heat signal "zlatá za 10 minut" (for 500 g): `caramelising`.
- Site words: "zatáhnout" = the meat surface goes grey, no crust. "Opéct" = a brown crust. "Výpek" = the brown layer on the pan bottom, from meat or vegetables. "Mírný oheň" is a heat setting; "mírný var" is what the liquid does. "Stáhni oheň" lowers the heat; "stáhni hrnec z ohně" takes the pot off the burner; "na přímém žáru" means on a lit burner at any setting. "Tuk se leskne a lehce tetelí" = ready; "kouří" = too hot, stáhni oheň. "Přepuštěné máslo" (clear, solids still white), "ghí" (solids lightly browned) and "oříškové máslo" (browned butter used as it is) are three things. "Vedlejší produkty" = USDA variety meats (hlava, ocas, vnitřnosti); "droby" means organs only. For braising, say "kus s málo kolagenem", not "libový": kližka is lean but full of collagen.
