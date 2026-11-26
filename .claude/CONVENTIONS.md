# Conventions

<!--
Idioms and placement rules that a linter or formatter can't enforce.
Skip anything tooling already checks. Prefer a rule plus a one-line reason over a long explanation.
-->

## Content

- Site text is Czech. Page slugs are Czech without diacritics, words joined by hyphens (`cibule`, `hovezi-klizka`), because they are the public URLs and the owner wants them Czech. Make the slug from the title, shortened where the title is long (`tuhe-dusene-maso`), and do not change it when the title changes later, so links and URLs stay stable. Code keys, data values (allergens, categories, `animal`), file names outside `content/`, `banners/` and `photos/`, and code stay English.
- Address the reader informally (tykání: "nakrájej", "tvoje", "zkus"), never with vykání ("nakrájejte", "Vaše"). This applies to all Czech text: recipes, explainers and UI labels, buttons and messages.
- **Czech kitchen first.** Write every page from the Czech home kitchen, not as a translated general or American cookbook page. The owner found the early pages "very American, just translated".
  - Start from what a Czech cook does at home and say it plainly, also when a chef would do it differently: prolisovaný česnek, jíška, zahuštění moukou, bujón. Say what the habit changes and when it is fine; never sneer at it.
  - Examples and uses are Czech dishes first (česnečka, topinka s česnekem, bramboráky, svíčková, guláš, vepřo knedlo zelo, pomazánky, polévky ze sáčku jen jako srovnání), foreign dishes after them.
  - Tools, products and cuts by the names a Czech shop, butcher or market uses: lis na česnek, struhadlo, kastrol, pekáč, tlakový hrnec; hladká / polohrubá / hrubá mouka, smetana ke šlehání, zakysaná smetana, tvaroh, sádlo a škvarky; kližka, plec, krk, líčka. No brand names.
  - Use only ingredients a Czech supermarket, butcher or market sells. An ingredient that appears in American recipes but in no Czech one is probably not sold here (buttermilk in US grades, heavy cream as named, cake flour, kosher salt, canned pumpkin, specific US cuts): replace it with the Czech product a Czech recipe uses, or leave it out.
  - Czech seasoning habits where they belong: majoránka, kmín, nové koření, bobkový list, sladká paprika, česnek.
  - No US framing: no cups or °F (the converter handles them), no US-only products or names (kosher salt, half-and-half, "Dutch oven"), no US habit presented as the default (a whole roasted garlic head, brining a turkey). A foreign technique is fine when it is named as one and placed next to the Czech way.
  - Seasons, prices and availability as in Czech shops and markets.
- Slugs are unique across all sections and recipes, so `[[slug]]` never needs a section prefix.
- Link a method, equipment or troubleshooting page with `[[slug]]` or `[[slug|text]]` in the body. Do not add frontmatter lists for them.
- Every written page needs at least one incoming link.
- Write ingredient amounts in metric units from the unit list. Use `text:` (e.g. "podle chuti") only for amounts that must not scale.
- Never type allergens or diet on a recipe unless the derived value is wrong; then add the override and a note why in Poznámky.
- Food-safety numbers (temperatures, storage times) need a cited authority, named in the text. Czech and EU authorities come first, other European ones next, USDA FSIS only where none of them gives a number; `docs/FOOD-SAFETY.md` lists the numbers and the name to cite for each topic. Never invent them. When two authorities differ, recommend the stricter number and never call the looser one "přísnější".
- Cooked food into the fridge always gets the same rule: shallow containers, in the fridge within 2 hours, then a day count (2 days, "podle bezpecnostpotravin.cz"). A loose "vychladlé dej do lednice" invites hours on the counter. Reheating ends with a target: "až se celé prohřeje a začne mírně vařit (ve středu aspoň 75 °C, nebo 70 °C po 2 minuty, viz [[thermometer|teploměr]])". Food that does not boil (brambory, kaše) drops "a začne mírně vařit" and keeps the core target.
- Exception: rice and any dish of cooked rice (rizoto, mléčná rýže, nákyp, plněné papriky) goes into the fridge within 1 hour, is eaten within 24 hours and is reheated once, "podle britského úřadu FSA" (`ryze` owns it); Bacillus cereus toxin survives reheating. The first reheat target on a page names its authority ("podle SZÚ a BfR").
- Exception: cooked wild-mushroom dishes (smaženice, houbová polévka, omáčka, kuba) are eaten within 24 hours and reheated once, "podle BZfE" (`hriby` owns it); wild mushrooms cook at least 20 minutes.
- Bought frozen berries for food that is not cooked or baked are boiled at least 2 minutes (`jahody` owns it). Other pages say "kupované mražené" and link it.
- Water that goes into food is cold from the tap or hot from the kettle, never warm from the tap (`voda` owns it); do not write "teplá voda" for food.
- Any dish with honey that could go to a child says "med nedávej dětem do 1 roku" and links `med`.
- A dish with a raw or soft egg (majonéza, holandská, ztracené vejce, tiramisu) names the risk groups or links `vejce`. A dish with wine or other alcohol is not for children or pregnant women; wine simmers at least 15 minutes. The same note goes on a filling, cream or sauce with rum, extract or other alcohol that is not simmered after it goes in.
- No alobal for salty or acidic food ("podle BfR"). Acid goes into a milk or cream sauce by lžička, tasting each time.
- A reheated cream dish follows `smetana`: smetana ke šlehání or a flour-thickened sauce may simmer gently; smetana na vaření without flour is only heated to the core target.
- Burn first aid is one text on `cukr`; other pages give a one-line summary and link it.
- A recipe that uses vinný, jablečný or balzamikový ocet, dijonská hořčice or sušené ovoce overrides allergens with `sulphites` (the catalog default is the sulphite-free kind).
- Spice timing: whole spices and bay leaf go in early; ground pepper at the end; ground paprika and ground kmín that build a sauce go in early on the fat (the paprika method on `sladka-paprika`); delicate dried herbs (majoránka) 10–15 minutes before the end, hardy ones (tymián, rozmarýn) earlier.
- A "viz X" or link must land on text that covers the point; check the target before linking. One authority name per rule across pages (the 2-hour cooling cites KHS or SZÚ as `docs/FOOD-SAFETY.md` topic 1 says, the same on every page). Spoon amounts use only lžíce and lžička.
- Wild-plant and forest-fruit food (medvědí česnek, lesní jahody, brusinky) is eaten cooked or heated to about 60 °C; raw only from the garden or the shop (fox tapeworm, `jahody` owns it for fruit).
- Heat words, only these: mírný, středně mírný, střední, středně vysoký, vysoký oheň; "moc silný oheň" only as a mistake. To lower the heat: "stáhni oheň". Give a heat word wherever a step changes the heat, so pages can agree.
- Raw meat: cook it within 2 days ("podle bezpecnostpotravin.cz"); at −18 °C it is safe almost without limit, and the freezer months are quality only. Head, tail and organ cuts (líčka, oháňka, jazyk, játra) are variety meats: 1–2 days in the fridge, 3–4 months frozen; that grouping and those numbers stay "podle USDA FSIS", since no Czech or EU source gives them. Numbers per topic in `docs/FOOD-SAFETY.md`.
- A basic that will cook further gets `note: nesolený` on the recipe's ingredient line. A variant or substitute that adds an allergen names it in brackets ("(obsahuje lepek)").
- A "bez mléka", "bez lepku" or similar substitute never contains that allergen; a substitute with butter, cheese or cream names "(obsahuje mléko)".
- Flour that has not simmered yet (zaprášení, zátřepka, a stored jíška) must still simmer in the dish: any text that thickens with flour says "po zahuštění aspoň 15 minut mírně vařit" or links `mouka`. The 15 minutes is for taste, not safety.
- One owner per procedure: a page that uses another page's procedure (jíška, zaprášení, peeling, toasting) gives what is special to it and a link, not the owner's steps and times again. Repeated steps drift.
- Opened packages in the fridge usually have a safety time (check `docs/FOOD-SAFETY.md`, then the label) before you label a time "odhad kvality".
- Quality-only times (spices, fats) need no source but say so ("odhad kvality, ne bezpečnostní lhůta"). Smoke-point numbers appear only on `olej`; other pages name the fat in words and link it.
- A recipe step that cooks until soft gives the fork test with the time, not the time alone.
- Troubleshooting pages use exactly these headings: Příznak, Možné příčiny, Jak to zachránit, Jak tomu předejít. A cause may end with "(→ …)" naming the symptom it gives.
- Equipment pages use exactly these headings: K čemu je, Jak vybrat, Při práci, Péče, Náhrady (bold bullets). "Při práci" stays neutral, so it fits a pánev as well as a nůž.
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
- Animation and transitions ignore `prefers-reduced-motion`, on the site and in banners. The owner turns that setting on only to quiet Windows animations, not for a health need. Do not add `prefers-reduced-motion` rules.
- The look follows `docs/STYLE.md`; the classes and data attributes in `SPEC.md` are the contract between templates, CSS and JS.

## Banners

- 3:1 SVG, colours only through the banner CSS variables in `SPEC.md`, no `id` attributes.

## Testing

- pytest in `tests/test_build.py`. Unit tests build a small site in `tmp_path` (the real `data/` plus small catalogs); the last tests build the real site and check that every internal link resolves.
- A new check in the build gets a test that triggers its message.
