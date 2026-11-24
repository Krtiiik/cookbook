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
- **Owner page**: the one explainer that explains an idea in full; other pages give one sentence and link it. Maillard reaction and výpek: `browning`. Onion colour stages: `caramelising`. Softening without colour: `sweating`. Liquid states (chvění, mírný var, prudký var): `simmering`. Slow cooking in a little liquid, and collagen turning to gelatin: `braising`. Tough vs dry braised meat, the fork test and the rescue: `tough-stew`. How to add ground paprika: `sweet-paprika`. Burnt paprika and its bitterness: `bitter-paprika`. Braising time of a cut: that cut's own page (`beef-shank`, `beef-chuck`, `beef-cheeks`, `oxtail`); other pages compare in a few words and do not repeat the oven setting. Oven braising at 140–150 °C: `braising`. Smoke points (kouřový bod) and which fat takes which heat: `oil`. Clarified butter: `butter`. Rendering lard: `lard`. Safe core temperatures, using a thermometer, and checking fridge and freezer temperatures: `thermometer`. Cutting technique and knife care: `chefs-knife`. Heating and using the cast-iron pot: `dutch-oven`. Butter heat stages and oříškové máslo: `butter`. Frying-oil reuse, oil fires and the strouhanka or vařečka test for frying heat: `oil` (`lard` links it). Reheating temperature: `thermometer`. Smoked-paprika kinds and dosing: `smoked-paprika`. Hot-paprika grades and dosing: `hot-paprika`. Burnt onion and telling it from burnt paprika: `burnt-onion`. Softening bitterness in a finished dish: `bitter-paprika`. The too-much-heat signal "zlatá za 10 minut" (for 500 g): `caramelising`. When to salt each kind of food and fixing oversalting: `salt`; salting meat before browning (the 40-minute window): `browning`. Root vegetables in stock and sauces, and storing them: `carrot`. What the celery allergen covers: `celeriac`. Garlic timing on fat and garlic in oil: `garlic`. Protlak kinds, frying it, opened-paste storage: `tomato-paste`. Varný typ A/B/C, green and sprouted potatoes (solanin), storing raw potatoes, boiling potatoes and their fork test: `potatoes`. Washing sand out of leek, white vs green part: `leek`. Onion / shallot / leek swaps by weight: `shallot`. Bone kinds, blanching, roasting bones for a dark stock, the gelatin test, raw-bone storage: `beef-bones`. Whole vs ground spice and storing spices: `peppercorns`. Toasting whole seeds, dry or on fat: `caraway`. Delicate dried herbs added late, rubbing them in the palms, dried vs fresh: `marjoram`. Whole aromatics in early and out before serving (count them, sítko, plátýnko): `bay-leaf`. Counts of nové koření per dish: `allspice` (pepř counts stay on `peppercorns`, bay leaves on `bay-leaf`). Jíška (světlá, zlatá, tmavá), zaprášení, zátřepka, how much flour per litre, lumps, the 15-minute cook-out, flour grades and raw flour: `flour`. Heating milk, škraloup, curdling in sauces, raw, opened and frozen milk: `milk`. Rice kinds, cooking rice and the safety of cooked rice and rice dishes: `rice`. Fresh vs canned tomatoes, peeling, storing, unripe tomatoes: `tomato` (the word "protlak" on labels stays on `tomato-paste`; glykoalkaloidy on `potatoes`). Wild-garlic look-alikes, the smell test, picking rules, fox tapeworm: `wild-garlic`. Washing soft fruit and boiling bought frozen berries: `strawberry`. Cut-apple browning, ethylene and what to store apart: `apple`. Ovocné knedlíky (dough, wrapping, boiling) and povidla: `plum`. Bitter pumpkin (cucurbitacins), also for cuketa and okurka: `pumpkin`. Peeling and cooking white and green asparagus: `asparagus`. Wild mushrooms (identification, the 20-minute cooking, poisoning, drying, the 24-hour rule for mushroom dishes): `porcini`. Fish freshness, live carp, Y bones, rybí polévka: `carp`. Tap, bojler and well water, hardness, cold start vs hot top-up, boiling at altitude: `water`. Kinds of sugar, karamel, sugar burns, jam with želírovací cukr: `sugar`. Honey and infants, the honey↔sugar swap: `honey`.
- Site words: "zatáhnout" = the meat surface goes grey, no crust. "Opéct" = a brown crust. "Výpek" = the brown layer on the pan bottom, from meat or vegetables. "Mírný oheň" is a heat setting; "mírný var" is what the liquid does. "Stáhni oheň" lowers the heat; "stáhni hrnec z ohně" takes the pot off the burner; "na přímém žáru" means on a lit burner at any setting. "Tuk se leskne a lehce tetelí" = ready; "kouří" = too hot, stáhni oheň. "Přepuštěné máslo" (clear, solids still white), "ghí" (solids lightly browned) and "oříškové máslo" (browned butter used as it is) are three things. "Protlak" = the concentrate (at least 24 % sušiny); passata is "protlak nezahuštěný" on Czech labels but is never what a recipe means by protlak. "Dusit" only for braising; meat steaming in a pan "vaří se ve vlastní šťávě". "Vedlejší produkty" = USDA variety meats (hlava, ocas, vnitřnosti); "droby" means organs only. For braising, say "kus s málo kolagenem", not "libový": kližka is lean but full of collagen. "Blanšírovat" = kosti krátce povařit a první vodu slít. "Zátřepka" = mouka rozmíchaná ve studené tekutině a vlitá do horké; "zaprášení" = mouka nasypaná na zeleninu nebo maso na tuku.