import importlib.util
import json
import re
import shutil
import sys
import textwrap
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


build = _load("cookbook_build", "build.py")
import_photo = _load("cookbook_import_photo", "import_photo.py")

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400"></svg>'
RECIPE = """
---
title: Polévka
summary: Jednoduchá polévka.
status: {status}
servings: 4
time_active_min: 10
time_total_min: 40
difficulty: easy
cuisine: czech
groups: [{groups}]
ingredient_groups:
  - items:
{items}
changes:
  - {{ date: 2026-11-20, note: "První verze." }}
---
## Postup

1. Uvař [[stock|vývar]] a [[duseni]].
2. Osol.

## Poznámky

Poznámka.
"""


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip("\n"), encoding="utf-8")


def add_recipe(root, slug="polevka", status="draft", groups="polevky",
               items="      - { qty: 2, unit: lzice, item: cibule }\n      - { qty: 500, unit: ml, item: stock }"):
    write(root, f"content/recepty/{slug}.md", RECIPE.format(status=status, groups=groups, items=items))


@pytest.fixture
def site_root(tmp_path: Path) -> Path:
    shutil.copytree(ROOT / "data", tmp_path / "data")
    write(tmp_path, "catalog/metody.yaml", """
        - { slug: duseni, title: Dušení, summary: Pomalu., category: moist-heat }
        - { slug: hnednuti-masa, title: Hnědnutí, summary: Kůrka., category: dry-heat }
    """)
    write(tmp_path, "catalog/suroviny.yaml", """
        - { slug: cibule, title: Cibule, summary: Ostrá., category: vegetables, animal: none, season: all-year }
        - { slug: maslo, title: Máslo, summary: Tuk., category: fats, animal: dairy, season: all-year, allergens: [milk] }
        - { slug: bones, title: Kosti, summary: Na vývar., category: meat, animal: meat, season: [10, 11] }
        - { slug: celer, title: Celer, summary: Vůně., category: vegetables, animal: none, season: [9, 10], allergens: [celery] }
    """)
    write(tmp_path, "catalog/vybaveni.yaml", "[]\n")
    write(tmp_path, "catalog/reseni-problemu.yaml", "[]\n")
    write(tmp_path, "catalog/skupiny.yaml", """
        - { slug: zaklady, kind: course, title: Základy }
        - { slug: polevky, kind: course, title: Polévky }
    """)
    write(tmp_path, "banners/_planned.svg", SVG)
    write(tmp_path, "banners/duseni.svg", SVG)
    write(tmp_path, "content/metody/duseni.md", "Dusí se [[hnednuti-masa|po opečení]].\n")
    write(tmp_path, "content/recepty/stock.md", RECIPE.format(
        status="draft", groups="zaklady",
        items="      - { qty: 1, unit: kg, item: bones }\n      - { qty: 100, unit: g, item: celer }",
    ).replace("[[stock|vývar]] a ", ""))
    return tmp_path


def problems(root: Path) -> str:
    with pytest.raises(build.BuildError) as e:
        build.load_site(root)
    return "\n".join(e.value.problems)


# ---------------------------------------------------------------- loading and checks


def test_explainer_is_written_only_when_its_file_exists(site_root):
    site = build.load_site(site_root)
    assert site.pages["duseni"].written
    assert not site.pages["hnednuti-masa"].written
    assert [p.slug for p in site.sections[0].pages] == ["duseni", "hnednuti-masa"]


def test_the_build_lists_every_problem_at_once(site_root):
    add_recipe(site_root, items="      - { qty: 2, unit: cup, item: cibule }\n      - { qty: 1, unit: g, item: ghost }")
    write(site_root, "content/metody/duseni.md", "See [[nowhere]].\n")
    text = problems(site_root)
    assert "unknown unit cup" in text  # US units are for the converter only
    assert "links to unknown [[nowhere]]" in text


def test_unknown_ingredient_and_group_fail(site_root):
    add_recipe(site_root, groups="polevky, ghosts", items="      - { qty: 1, unit: g, item: ghost }")
    text = problems(site_root)
    assert "unknown group ghosts" in text
    assert "ingredient ghost is not in catalog/suroviny.yaml" in text


def test_a_tested_recipe_needs_a_photo(site_root):
    add_recipe(site_root, status="tested")
    assert "a tested recipe needs a photo photos/polevka.webp" in problems(site_root)


def test_slugs_are_unique_across_recipes_and_explainers(site_root):
    add_recipe(site_root, slug="cibule")
    assert "slug cibule is already used" in problems(site_root)


def test_explainer_file_must_be_in_its_catalog(site_root):
    write(site_root, "content/metody/stray.md", "Text.\n")
    assert "content/metody/stray.md: not in catalog/metody.yaml" in problems(site_root)


def test_written_explainer_needs_a_banner(site_root):
    (site_root / "banners" / "duseni.svg").unlink()
    assert "duseni: written explainer has no banner" in problems(site_root)


# ---------------------------------------------------------------- derived data


def test_allergens_and_diet_pass_through_a_basic(site_root):
    add_recipe(site_root)
    site = build.load_site(site_root)
    stock, soup = site.pages["stock"], site.pages["polevka"]
    assert stock.is_basic and stock.allergens == ["celery"] and stock.diet == []
    assert soup.allergens == ["celery"] and soup.diet == []
    assert site.pages["stock"].backlinks == ["polevka"]  # used as an ingredient
    assert site.pages["cibule"].backlinks == ["polevka"]


def test_diet_is_vegetarian_with_dairy_and_vegan_without(site_root):
    add_recipe(site_root, slug="maslova", items="      - { qty: 50, unit: g, item: maslo }")
    add_recipe(site_root, slug="cibulova", items="      - { qty: 50, unit: g, item: cibule }")
    site = build.load_site(site_root)
    assert site.pages["maslova"].diet == ["vegetarian"]
    assert site.pages["maslova"].allergens == ["milk"]
    assert site.pages["cibulova"].diet == ["vegetarian", "vegan"]


def test_a_basic_override_passes_on_to_its_users(site_root):
    text = (site_root / "content/recepty/stock.md").read_text(encoding="utf-8")
    write(site_root, "content/recepty/stock.md", text.replace("status: draft", "status: draft\nallergens: []"))
    add_recipe(site_root)
    assert build.load_site(site_root).pages["polevka"].allergens == []


def test_basics_in_a_loop_fail(site_root):
    add_recipe(site_root, slug="a", groups="zaklady", items="      - { qty: 1, unit: g, item: b }")
    add_recipe(site_root, slug="b", groups="zaklady", items="      - { qty: 1, unit: g, item: a }")
    assert "basics use each other in a loop" in problems(site_root)


# ---------------------------------------------------------------- amounts


@pytest.mark.parametrize("unit, qty, factor, text", [
    ("lzice", 1, 1, "1 lžíce"),
    ("lzice", 2, 1, "2 lžíce"),
    ("lzice", 5, 1, "5 lžic"),
    ("lzice", 3, 0.5, "1,5 lžíce"),
    ("strouzek", 3, 1.5, "5 stroužků"),  # half rounds up, as in the browser scaler
    ("strouzek", 1, 1, "1 stroužek"),
    ("g", 1000, 0.75, "750 g"),
    ("g", 33, 0.5, "17 g"),
    ("ml", 500, 0.25, "130 ml"),  # from 100 ml the step is 10 ml
    ("spetka", 1, 3, "1 špetka"),  # a pinch never scales
])
def test_amounts_scale_round_and_use_czech_forms(site_root, unit, qty, factor, text):
    units = build.load_site(site_root).units
    assert build.fmt_amount(units[unit], qty, factor) == text


def test_never_rounds_below_one_step(site_root):
    units = build.load_site(site_root).units
    assert build.fmt_amount(units["lzicka"], 1, 0.1) == "0,5 lžičky"


# ---------------------------------------------------------------- rendering


def test_body_rendering_adds_design_hooks(site_root):
    add_recipe(site_root)
    site = build.load_site(site_root)
    html = build.render_body(site, site.pages["polevka"], "../")
    assert '<h2 class="c-tomato">Postup</h2>\n<ol class="steps">' in html
    assert '<a class="site-link is-draft" data-slug="stock" href="../recepty/stock.html">vývar</a>' in html
    assert '<a class="site-link is-written" data-slug="duseni" href="../metody/duseni.html">dušení</a>' in html
    assert '<p class="handnote">Poznámka.</p>' in html


def test_steps_style_allows_an_intro_paragraph_before_the_list(site_root):
    add_recipe(site_root)
    path = site_root / "content/recepty/polevka.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("## Postup\n\n", "## Postup\n\nVývar uvař předem.\n\n"), encoding="utf-8")
    site = build.load_site(site_root)
    html = build.render_body(site, site.pages["polevka"], "../")
    assert '<p>Vývar uvař předem.</p>\n<ol class="steps">' in html


def test_recipe_jsonld_lists_steps_and_ingredients(site_root):
    add_recipe(site_root)
    site = build.load_site(site_root)
    data = json.loads(build.recipe_jsonld(site, site.pages["polevka"]))
    assert data["@type"] == "Recipe"
    assert [s["text"] for s in data["recipeInstructions"]] == ["Uvař vývar a duseni.", "Osol."]
    assert data["recipeIngredient"] == ["2 lžíce cibule", "500 ml polévka"]
    assert data["totalTime"] == "PT40M"


def test_tested_recipe_gets_resized_photos(site_root, tmp_path):
    add_recipe(site_root, status="tested")
    Image.new("RGB", (2000, 1333), "red").save(site_root / "photos.webp")
    (site_root / "photos").mkdir()
    shutil.move(site_root / "photos.webp", site_root / "photos" / "polevka.webp")
    site = build.load_site(site_root)
    out = tmp_path / "out"
    build.render_site(site, out, ROOT / "templates", ROOT / "static", tmp_path / "cache")
    for w in build.PHOTO_WIDTHS:
        with Image.open(out / "photos" / f"polevka-{w}.webp") as img:
            assert img.width == w
    html = (out / "recepty" / "polevka.html").read_text(encoding="utf-8")
    assert 'srcset="../photos/polevka-400.webp 400w' in html
    assert '"image"' in html


def test_import_photo_shrinks_and_drops_metadata(tmp_path):
    source = tmp_path / "phone.jpg"
    exif = Image.Exif()
    exif[0x010F] = "PhoneMaker"  # camera make, stands in for GPS and other metadata
    Image.new("RGB", (4000, 3000), "blue").save(source, exif=exif)
    target = import_photo.import_photo(source, "polevka", tmp_path / "photos")
    with Image.open(target) as img:
        assert max(img.size) == import_photo.LONG_SIDE
        assert not img.getexif()


# ---------------------------------------------------------------- the real site


@pytest.fixture(scope="module")
def real_site(tmp_path_factory):
    out = tmp_path_factory.mktemp("dist")
    site = build.load_site(ROOT)
    build.render_site(site, out, ROOT / "templates", ROOT / "static", tmp_path_factory.mktemp("cache"))
    return site, out


def test_real_site_builds(real_site):
    site, out = real_site
    assert (out / "index.html").exists()
    assert (out / "zaklady" / "index.html").exists()
    for page in site.pages.values():
        assert (out / page.url).exists()


def test_every_internal_link_and_asset_resolves(real_site):
    _, out = real_site
    missing = []
    for html in out.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        for ref in re.findall(r'(?:href|src)="([^"#?]+)', text):
            if ref.startswith(("http:", "https:", "mailto:")):
                continue
            if not (html.parent / ref).resolve().exists():
                missing.append(f"{html.relative_to(out)} -> {ref}")
    assert not missing, missing


def test_index_holds_previews_and_filters(real_site):
    _, out = real_site
    text = (out / "static" / "index.js").read_text(encoding="utf-8")
    data = json.loads(text.removeprefix("window.SITE_INDEX = ").rstrip().rstrip(";"))
    gulas = next(p for p in data["pages"] if p["slug"] == "hovezi-gulas")
    assert gulas["status"] == "draft" and "celery" in gulas["allergens"]
    duseni = next(p for p in data["pages"] if p["slug"] == "duseni")
    assert data["banners"][duseni["banner"]].startswith("<svg")
    assert data["units"]["lzice"]["forms"] == ["lžíce", "lžíce", "lžic", "lžíce"]


def test_filtered_out_cards_are_not_shown():
    # .card sets display: flex, which beats the hidden attribute unless a rule restores it.
    assert ".card[hidden] { display: none; }" in (ROOT / "static" / "site.css").read_text(encoding="utf-8")


def test_current_month_frame_closes_on_the_last_shown_row():
    # The filter hides rows, so :last-child is not the last row on screen; site.js marks it instead.
    css = (ROOT / "static" / "site.css").read_text(encoding="utf-8")
    js = (ROOT / "static" / "site.js").read_text(encoding="utf-8")
    assert ".season tr.is-last td.now::before" in css
    assert "classList.toggle('is-last'" in js


def test_ingredient_section_has_category_and_season_filters(real_site):
    site, out = real_site
    text = (out / "static" / "index.js").read_text(encoding="utf-8")
    data = json.loads(text.removeprefix("window.SITE_INDEX = ").rstrip().rstrip(";"))
    by_slug = {p["slug"]: p for p in data["pages"]}
    assert by_slug["dyne"]["category"] == "vegetables" and by_slug["dyne"]["season"] == [9, 10, 11]
    assert by_slug["sul"]["season"] == "all-year"
    assert "season" not in by_slug["duseni"]

    html = (out / "suroviny" / "index.html").read_text(encoding="utf-8")
    assert 'class="filters"' in html and 'class="grid4 filter-list"' in html
    assert 'name="category"' in html and 'name="month"' in html
    assert '<option value="vegetables">zelenina</option>' in html
    assert '<option value="moist-heat">' not in html  # only categories this section uses
    assert '<option value="all-year">celý rok</option>' in html
    assert '<option value="11">listopad</option>' in html
    assert site.categories(next(s for s in site.sections if s.slug == "suroviny"))[0] == "vegetables"
    assert 'class="filters"' not in (out / "metody" / "index.html").read_text(encoding="utf-8")


def test_filter_boxes_share_the_fold_wrapper(real_site):
    # The fold in site.js runs only when details.filters-wrap sits in .filters-box, which
    # also holds the bottom margin.
    _, out = real_site
    for rel in ("recepty/index.html", "suroviny/index.html"):
        html = (out / rel).read_text(encoding="utf-8")
        assert re.search(r'<div class="filters-box">\s*<details class="filters-wrap"', html), rel


def test_converter_and_calendar_have_own_pages(real_site):
    _, out = real_site
    converter = (out / "prevodnik" / "index.html").read_text(encoding="utf-8")
    calendar = (out / "sezonni-kalendar" / "index.html").read_text(encoding="utf-8")
    assert 'class="converter__result"' in converter and "table class=\"season\"" not in converter
    assert 'table class="season"' in calendar and "converter__result" not in calendar
    assert not (out / "reference").exists()


def test_home_has_no_meta_description(real_site):
    _, out = real_site
    assert 'name="description"' not in (out / "index.html").read_text(encoding="utf-8")


def test_ingredient_categories_show_as_pills(real_site):
    site, out = real_site
    cesnek = (out / "suroviny" / "cesnek.html").read_text(encoding="utf-8")
    # On the ingredient page the pill links to the section list, filtered to the category.
    assert re.search(r'<a class="pill c-mint" href="index.html\?category=vegetables"[^>]*>'
                     r'<i class="pill__icon"><svg[^>]*>.*?</svg></i>zelenina</a>', cesnek)

    calendar = (out / "sezonni-kalendar" / "index.html").read_text(encoding="utf-8")
    assert '<span class="pill pill--small c-mint">' in calendar

    # Ingredient cards show the category instead of the section label, which repeats on every card.
    section = (out / "suroviny" / "index.html").read_text(encoding="utf-8")
    assert '<span class="lbl">suroviny</span>' not in section
    pills = re.findall(r'<span class="pill pill--small c-(\w+)">(.*?)</span>', section)
    assert len(pills) == len(next(s for s in site.sections if s.slug == "suroviny").pages)
    # Every category has its own icon and one of the four enamel colours.
    assert all(colour in build.COLORS and "<svg" in inner for colour, inner in pills)
    assert {"maso", "koření"} <= {re.sub(r"<.*>", "", inner) for _, inner in pills}


def test_seasons_show_as_pills(real_site):
    _, out = real_site
    # A recipe's seasons link to the recipe list filtered to that season, in the season's colour.
    gulas = (out / "recepty" / "hovezi-gulas.html").read_text(encoding="utf-8")
    assert re.search(r'<a class="pill c-tomato" href="index.html\?season=autumn"[^>]*>'
                     r'<i class="pill__icon"><svg[^>]*>.*?</svg></i>podzim</a>', gulas)
    assert re.search(r'<a class="pill c-cobalt" href="index.html\?season=winter"[^>]*>.*?zima</a>', gulas)

    # An all-year ingredient links to the all-year filter of the ingredient list.
    klizka = (out / "suroviny" / "hovezi-klizka.html").read_text(encoding="utf-8")
    assert re.search(r'<a class="pill c-year" href="index.html\?month=all-year"[^>]*>'
                     r'<i class="pill__icon"><svg[^>]*>.*?</svg></i>celý rok</a>', klizka)
