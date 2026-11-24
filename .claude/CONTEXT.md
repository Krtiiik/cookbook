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
- **Owner page**: the one explainer that explains an idea in full; other pages give one sentence and link it. Maillard reaction and výpek: `hnednuti-masa`. Onion colour stages: `karamelizace-cibule`. Softening without colour: `zpoceni-zeleniny`. Liquid states (chvění, mírný var, prudký var): `mirny-var`. Slow cooking in a little liquid, and collagen turning to gelatin: `duseni`. Tough vs dry braised meat, the fork test and the rescue: `tuhe-dusene-maso`. How to add ground paprika: `sladka-paprika`. Burnt paprika and its bitterness: `zhorkla-paprika`. Braising time of a cut: that cut's own page (`hovezi-klizka`, `hovezi-plec`, `hovezi-licka`, `ohanka`); other pages compare in a few words and do not repeat the oven setting. Oven braising at 140–150 °C: `duseni`. Smoke points (kouřový bod) and which fat takes which heat: `olej`. Clarified butter: `maslo`. Rendering lard: `sadlo`. Safe core temperatures, using a thermometer, and checking fridge and freezer temperatures: `teplomer`. Cutting technique and knife care: `kucharsky-nuz`. Heating and using the cast-iron pot: `litinovy-hrnec`. Butter heat stages and oříškové máslo: `maslo`. Frying-oil reuse, oil fires and the strouhanka or vařečka test for frying heat: `olej` (`sadlo` links it). Reheating temperature: `teplomer`. Smoked-paprika kinds and dosing: `uzena-paprika`. Hot-paprika grades and dosing: `paliva-paprika`. Burnt onion and telling it from burnt paprika: `zhorkla-cibule`. Softening bitterness in a finished dish: `zhorkla-paprika`. The too-much-heat signal "zlatá za 10 minut" (for 500 g): `karamelizace-cibule`. When to salt each kind of food and fixing oversalting: `sul`; salting meat before browning (the 40-minute window): `hnednuti-masa`. Root vegetables in stock and sauces, and storing them: `mrkev`. What the celery allergen covers: `celer`. Garlic timing on fat and garlic in oil: `cesnek`. Protlak kinds, frying it, opened-paste storage: `rajcatovy-protlak`. Varný typ A/B/C, green and sprouted potatoes (solanin), storing raw potatoes, boiling potatoes and their fork test: `brambory`. Washing sand out of leek, white vs green part: `porek`. Onion / shallot / leek swaps by weight: `salotka`. Bone kinds, blanching, roasting bones for a dark stock, the gelatin test, raw-bone storage: `hovezi-kosti`. Whole vs ground spice and storing spices: `pepr`. Toasting whole seeds, dry or on fat: `kmin`. Delicate dried herbs added late, rubbing them in the palms, dried vs fresh: `majoranka`. Whole aromatics in early and out before serving (count them, sítko, plátýnko): `bobkovy-list`. Counts of nové koření per dish: `nove-koreni` (pepř counts stay on `pepr`, bay leaves on `bobkovy-list`). Jíška (světlá, zlatá, tmavá), zaprášení, zátřepka, how much flour per litre, lumps, the 15-minute cook-out, flour grades and raw flour: `mouka`. Heating milk, škraloup, curdling in sauces, raw, opened and frozen milk: `mleko`. Rice kinds, cooking rice and the safety of cooked rice and rice dishes: `ryze`. Fresh vs canned tomatoes, peeling, storing, unripe tomatoes: `rajcata` (the word "protlak" on labels stays on `rajcatovy-protlak`; glykoalkaloidy on `brambory`). Wild-garlic look-alikes, the smell test, picking rules, fox tapeworm: `medvedi-cesnek`. Washing soft fruit and boiling bought frozen berries: `jahody`. Cut-apple browning, ethylene and what to store apart: `jablka`. Ovocné knedlíky (dough, wrapping, boiling) and povidla: `svestky`. Bitter pumpkin (cucurbitacins), also for cuketa and okurka: `dyne`. Peeling and cooking white and green asparagus: `chrest`. Wild mushrooms (identification, the 20-minute cooking, poisoning, drying, the 24-hour rule for mushroom dishes): `hriby`. Fish freshness, live carp, Y bones, rybí polévka: `kapr`. Tap, bojler and well water, hardness, cold start vs hot top-up, boiling at altitude: `voda`. Kinds of sugar, karamel, sugar burns, jam with želírovací cukr: `cukr`. Honey and infants, the honey↔sugar swap: `med`. Egg sizes and code, boiling times, ztracené vejce, separating, sníh, raw and soft eggs and risk groups: `vejce`. Which cream goes into a hot sauce, tempering, whipping, zakysaná with flour: `smetana` (why milk curdles stays `mleko`). Pressing and draining tvaroh, tvaroh pomazánky: `tvaroh`. Vinegar strengths, 8 % to 5 %, nálev na salát 1:3, acid added last, never mixed with chlorine: `ocet`. Lemon juice and zest, treated peel: `citron`. Mustard kinds, sulphites in dijonská: `horcice`. Trojobal and shallow frying (the oil-heat test stays on `olej`): `trojobal`. Draining, straining, pasírování, plátýnko: `sitko`. Descaling: `voda`. Burn first aid: `cukr`.
- Site words: "zatáhnout" = the meat surface goes grey, no crust. "Opéct" = a brown crust. "Výpek" = the brown layer on the pan bottom, from meat or vegetables. "Mírný oheň" is a heat setting; "mírný var" is what the liquid does. "Stáhni oheň" lowers the heat; "stáhni hrnec z ohně" takes the pot off the burner; "na přímém žáru" means on a lit burner at any setting. "Tuk se leskne a lehce tetelí" = ready; "kouří" = too hot, stáhni oheň. "Přepuštěné máslo" (clear, solids still white), "ghí" (solids lightly browned) and "oříškové máslo" (browned butter used as it is) are three things. "Protlak" = the concentrate (at least 24 % sušiny); passata is "protlak nezahuštěný" on Czech labels but is never what a recipe means by protlak. "Dusit" only for braising; meat steaming in a pan "vaří se ve vlastní šťávě". "Vedlejší produkty" = USDA variety meats (hlava, ocas, vnitřnosti); "droby" means organs only. For braising, say "kus s málo kolagenem", not "libový": kližka is lean but full of collagen. "Blanšírovat" = kosti krátce povařit a první vodu slít. "Zátřepka" = mouka rozmíchaná ve studené tekutině a vlitá do horké; "zaprášení" = mouka nasypaná na zeleninu nebo maso na tuku. "Pasírovat" = protlačit omáčku nebo rajčata sítkem (not "prolisovat"); tvaroh se "prolisuje" sítkem nebo lisem, as Czech recipes say. "Nálev na salát" (ocet, voda, cukr, sůl) is not a pickling brine. "Ztracené vejce" has a runny yolk and belongs with the soft eggs.