"""Build the cooking site from Markdown and YAML sources into static HTML pages.

Usage: uv run python scripts/build.py [--out DIR]

Sources (all under the repository root):
  data/site.yaml                       site name, public URL
  data/units.yaml                      units: Czech forms, scaling, conversion factors
  data/allergens.yaml                  the EU 14 allergens
  data/labels.yaml                     Czech labels for difficulty, season, diet, cuisine, categories
  catalog/<section>.yaml               explainer entries of one section (title, summary, data)
  catalog/skupiny.yaml                 recipe groups with their kind
  content/recepty/<slug>.md            a recipe: YAML frontmatter, then the body
  content/<section>/<slug>.md          body of a written explainer (no frontmatter)
  banners/<slug>.svg                   banner of a written explainer; banners/_planned.svg for planned ones
  photos/<slug>.webp                   photo of a recipe (made by scripts/import_photo.py)
  templates/, static/                  page templates (Jinja2) and assets copied to dist/static/

Links in bodies are written [[slug]] or [[slug|text]] and must name a recipe or an explainer.
The build checks everything and lists every problem before it fails.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

HERE = Path(__file__).resolve().parents[1]  # repository root
LINK = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLANNED_BANNER = "_planned"
PHOTO_WIDTHS = (400, 800, 1600)
BASIC_GROUP = "zaklady"

# Explainer sections in navigation order. "color" is the section's enamel colour (docs/STYLE.md).
SECTIONS = {
    "metody": {"title": "Metody", "label": "metody", "color": "tomato",
               "required": {"category"}, "optional": {"related"}},
    "suroviny": {"title": "Suroviny", "label": "suroviny", "color": "mint",
                 "required": {"category", "animal", "season"},
                 "optional": {"substitutes", "allergens", "density", "related"}},
    "vybaveni": {"title": "Vybavení", "label": "vybavení", "color": "mustard",
                 "required": set(), "optional": {"category", "related"}},
    "reseni-problemu": {"title": "Řešení problémů", "label": "řešení problémů", "color": "cobalt",
                        "required": set(), "optional": {"category", "related"}},
}
COLORS = ("tomato", "mint", "mustard", "cobalt")
GROUP_KINDS = {"course": "Druh jídla", "occasion": "Příležitost"}
ANIMAL = ("none", "dairy", "egg", "honey", "fish", "meat")
RECIPE_REQUIRED = {"title", "summary", "status", "servings", "time_active_min", "time_total_min",
                   "difficulty", "cuisine", "groups", "ingredient_groups", "changes"}
RECIPE_OPTIONAL = {"season", "allergens", "diet"}
STATUSES = ("draft", "tested")
DIETS = ("vegetarian", "vegan")
MONTHS = ["leden", "únor", "březen", "duben", "květen", "červen", "červenec", "srpen", "září",
          "říjen", "listopad", "prosinec"]
MONTHS_SHORT = ["led", "úno", "bře", "dub", "kvě", "čvn", "čvc", "srp", "zář", "říj", "lis", "pro"]
H2_COLORS = {"Postup": "tomato", "Proč to funguje": "mint", "Varianty a náhrady": "mustard",
             "Skladování a ohřev": "cobalt", "Poznámky": "tomato"}


class BuildError(Exception):
    """The sources are inconsistent; carries every problem found, not just the first."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("\n".join(problems))


# ---------------------------------------------------------------- model


@dataclass
class Unit:
    slug: str
    forms: list[str]  # one, few (2-4), many (5+), fraction
    scalable: bool = True
    round: list[tuple[float, float]] = field(default_factory=lambda: [(0, 1)])  # (from amount, step)
    ml: float | None = None  # millilitres in one unit, for the converter
    g: float | None = None  # grams in one unit, for the converter
    in_recipes: bool = True  # False for units only the converter offers (US units)
    title: str = ""

    def form(self, value: float) -> str:
        whole = abs(value - round(value)) < 1e-9
        if not whole:
            return self.forms[3]
        if round(value) == 1:
            return self.forms[0]
        if 2 <= round(value) <= 4:
            return self.forms[1]
        return self.forms[2]

    def step(self, value: float) -> float:
        step = self.round[0][1]
        for start, s in self.round:
            if value >= start:
                step = s
        return step

    def as_dict(self) -> dict:
        return {"forms": self.forms, "scalable": self.scalable, "round": self.round}


@dataclass
class Item:
    item: str  # ingredient or basic slug
    qty: float | None = None
    unit: str | None = None
    note: str = ""
    text: str = ""  # an amount that never scales, e.g. "podle chuti"
    display: str = ""  # amount for the base servings, Czech


@dataclass
class IngredientGroup:
    name: str
    items: list[Item]


@dataclass
class Page:
    kind: str  # "recipe" or "explainer"
    slug: str
    title: str
    summary: str
    url: str
    body_md: str = ""
    links: list[str] = field(default_factory=list)  # slugs linked from the body, in order, unique
    backlinks: list[str] = field(default_factory=list)  # slugs of pages linking here
    # explainers
    section: str = ""
    written: bool = True
    banner_svg: str = ""
    data: dict = field(default_factory=dict)  # catalog fields beyond slug/title/summary
    # recipes
    recipe_status: str = ""
    servings: int = 0
    time_active_min: int = 0
    time_total_min: int = 0
    difficulty: str = ""
    cuisine: str = ""
    season: list[str] = field(default_factory=list)
    groups: list[str] = field(default_factory=list)
    ingredient_groups: list[IngredientGroup] = field(default_factory=list)
    changes: list[dict] = field(default_factory=list)  # newest first
    allergens: list[str] = field(default_factory=list)
    diet: list[str] = field(default_factory=list)
    allergens_override: list[str] | None = None
    diet_override: list[str] | None = None
    photo_source: Path | None = None
    photo: dict | None = None  # width -> URL, filled when rendering
    jsonld: str = ""

    @property
    def status(self) -> str:
        if self.kind == "recipe":
            return self.recipe_status
        return "written" if self.written else "planned"

    @property
    def is_basic(self) -> bool:
        return BASIC_GROUP in self.groups

    @property
    def updated(self) -> dt.date | None:
        return self.changes[0]["date"] if self.changes else None

    @property
    def category(self) -> str:
        return self.data.get("category", "")

    @property
    def color(self) -> str:
        return SECTIONS[self.section]["color"] if self.section else "tomato"

    @property
    def ingredients(self) -> list[str]:
        return [i.item for g in self.ingredient_groups for i in g.items]


@dataclass
class Section:
    slug: str
    title: str
    label: str
    color: str
    url: str
    pages: list[Page] = field(default_factory=list)

    @property
    def written_count(self) -> int:
        return sum(p.written for p in self.pages)


@dataclass
class Group:
    slug: str
    kind: str
    title: str
    summary: str
    color: str
    url: str
    recipes: list[Page] = field(default_factory=list)


@dataclass
class Site:
    meta: dict
    labels: dict
    units: dict[str, Unit]
    allergens: list[dict]
    sections: list[Section]
    groups: list[Group]
    recipes: list[Page]  # newest change first
    pages: dict[str, Page]  # every recipe and explainer by slug

    def group(self, slug: str) -> Group:
        return next(g for g in self.groups if g.slug == slug)

    def related(self, page: Page) -> list[Page]:
        """Explainers this page links to or names in its catalog entry, then explainers linking here."""
        slugs = [*page.links, *(page.data.get("related") or []), *(page.data.get("substitutes") or []),
                 *page.backlinks]
        return [self.pages[s] for s in _ordered_unique(slugs)
                if s != page.slug and self.pages[s].kind == "explainer"]

    def linked_explainers(self, page: Page) -> list[Page]:
        return [self.pages[s] for s in page.links if self.pages[s].kind == "explainer"]

    def used_in(self, page: Page) -> list[Page]:
        """Recipes that use this page as an ingredient or link to it."""
        return [self.pages[s] for s in page.backlinks if self.pages[s].kind == "recipe"]

    def recent_changes(self, n: int) -> list[tuple[dt.date, Page, str]]:
        rows = [(c["date"], p, c["note"]) for p in self.recipes for c in p.changes]
        return sorted(rows, key=lambda r: (r[0], r[1].slug), reverse=True)[:n]

    def categories(self, section: Section) -> list[str]:
        """Category keys the section's pages use, in labels.yaml order, for its filter."""
        used = {p.category for p in section.pages}
        return [c for c in self.labels.get("categories", {}) if c in used]

    def label(self, kind: str, value: str) -> str:
        return self.labels.get(kind, {}).get(value, value)


# ---------------------------------------------------------------- formatting


def fmt_number(value: float) -> str:
    """Czech number: decimal comma, no trailing zeros, at most 2 decimals."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text.replace(".", ",")


def scale_amount(unit: Unit, qty: float, factor: float) -> float:
    if factor == 1 or not unit.scalable:
        return qty
    raw = qty * factor
    step = unit.step(raw)
    return max(step, math.floor(raw / step + 0.5) * step)  # half up, like Math.round in site.js


def fmt_amount(unit: Unit, qty: float, factor: float = 1) -> str:
    value = scale_amount(unit, qty, factor)
    form = unit.form(value)
    return f"{fmt_number(value)} {form}".strip()


def fmt_minutes(minutes: int) -> str:
    h, m = divmod(int(minutes), 60)
    if h and m:
        return f"{h} h {m} min"
    return f"{h} h" if h else f"{m} min"


def fmt_date(value: dt.date) -> str:
    return f"{value.day}. {value.month}. {value.year}"


def cz_plural(n: int, one: str, few: str, many: str) -> str:
    word = one if n == 1 else few if 2 <= n <= 4 else many
    return f"{n} {word}"


def default_link_text(title: str) -> str:
    """A title as it reads mid-sentence: 'Hovězí vývar' -> 'hovězí vývar'; acronyms stay."""
    first = title.split()[0]
    if len(first) > 1 and first[1].isupper():
        return title
    return title[:1].lower() + title[1:]


def season_range(months) -> str:
    """An ingredient's months as Czech text, read round the new year: [10, 11, 12, 1] -> 'říjen – leden'."""
    inside = set(months)
    if len(inside) == 12:
        return "celý rok"
    # Start each run at a month whose previous month is outside, walking forward from there.
    runs = []
    for m in range(1, 13):
        if m in inside and (m - 2) % 12 + 1 not in inside:
            end = m
            while end % 12 + 1 in inside:
                end = end % 12 + 1
            runs.append(MONTHS[m - 1] if end == m else f"{MONTHS[m - 1]} – {MONTHS[end - 1]}")
    return ", ".join(runs)


WHEEL_R, WHEEL_R_NOW, WHEEL_HUB, WHEEL_TEXT, WHEEL_TEXT_NOW = 75, 84, 38, 57, 61


def season_wheel(months) -> dict:
    """Geometry of the year wheel on ingredient pages: 12 ring segments, leden centred at the bottom,
    clockwise, so each season fills one quarter (summer at the top). Each segment also has a longer
    shape for when it is the current month, which the script marks. Empty segments come first:
    a later segment's paper outline would otherwise cover an in-season segment's ink edge."""
    cx = cy = WHEEL_R_NOW + 3
    inside = set(months)

    def point(radius, angle):
        return f"{cx + radius * math.cos(angle):.1f} {cy + radius * math.sin(angle):.1f}"

    def ring(outer, a0, a1):
        return (f"M{point(outer, a0)}A{outer} {outer} 0 0 1 {point(outer, a1)}"
                f"L{point(WHEEL_HUB, a1)}A{WHEEL_HUB} {WHEEL_HUB} 0 0 0 {point(WHEEL_HUB, a0)}Z")

    segments = []
    for m in range(1, 13):
        # SVG angles run clockwise from east; leden spans 75°–105°, centred on south (90°).
        a0, a1 = math.radians(75 + (m - 1) * 30), math.radians(75 + m * 30)
        mid = (a0 + a1) / 2
        tx, ty = cx + WHEEL_TEXT * math.cos(mid), cy + WHEEL_TEXT * math.sin(mid)
        segments.append({
            "month": m, "in_season": m in inside, "label": MONTHS_SHORT[m - 1], "title": MONTHS[m - 1],
            "d": ring(WHEEL_R, a0, a1), "d_now": ring(WHEEL_R_NOW, a0, a1), "tx": round(tx, 1), "ty": round(ty, 1),
            # the label moves outward with the longer current-month segment
            "dx": round((WHEEL_TEXT_NOW - WHEEL_TEXT) * math.cos(mid), 1),
            "dy": round((WHEEL_TEXT_NOW - WHEEL_TEXT) * math.sin(mid), 1),
        })
    segments.sort(key=lambda s: s["in_season"])
    return {"segments": segments, "centre": (cx, cy), "size": 2 * cx, "hub": WHEEL_HUB - 6,
            "count": len(inside), "range": season_range(months), "months": sorted(inside)}


def fold(text: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", text) if not unicodedata.combining(c)).lower()


# ---------------------------------------------------------------- loading


def _yaml(path: Path, problems: list[str], default=None):
    if not path.exists():
        problems.append(f"missing {path.name}")
        return default
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        problems.append(f"{path.name}: {e}")
        return default


def _read_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("a recipe must start with --- frontmatter")
    parts = re.split(r"^---[ \t]*$", text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        raise ValueError("frontmatter is not closed with ---")
    meta = yaml.safe_load(parts[1]) or {}
    return meta, parts[2].lstrip("\n")


def _ordered_unique(items):
    return list(dict.fromkeys(items))


def _load_units(root: Path, problems: list[str]) -> dict[str, Unit]:
    units: dict[str, Unit] = {}
    for u in _yaml(root / "data" / "units.yaml", problems, []) or []:
        slug = u.get("slug", "?")
        unknown = set(u) - {"slug", "title", "forms", "scalable", "round", "ml", "g", "in_recipes"}
        if unknown:
            problems.append(f"units.yaml {slug}: unknown keys {sorted(unknown)}")
        forms = u.get("forms", slug)
        if isinstance(forms, str):
            forms = [forms] * 4
        if len(forms) == 3:
            forms = [*forms, forms[1]]
        if len(forms) != 4:
            problems.append(f"units.yaml {slug}: forms must be one string or 3-4 forms")
            continue
        rounding = [(float(a), float(b)) for a, b in (u.get("round") or [[0, 1]])]
        units[slug] = Unit(slug, forms, u.get("scalable", True), rounding, u.get("ml"), u.get("g"),
                           u.get("in_recipes", True), u.get("title", forms[2]))
    return units


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def load_site(root: Path) -> Site:
    """Read every source under root, check that they agree, and link them together."""
    problems: list[str] = []
    meta = _yaml(root / "data" / "site.yaml", problems, {}) or {}
    labels = _yaml(root / "data" / "labels.yaml", problems, {}) or {}
    units = _load_units(root, problems)
    allergens = _yaml(root / "data" / "allergens.yaml", problems, []) or []
    allergen_slugs = {a["slug"] for a in allergens}

    banners = root / "banners"
    planned_path = banners / f"{PLANNED_BANNER}.svg"
    planned_svg = planned_path.read_text(encoding="utf-8") if planned_path.exists() else ""
    if not planned_svg:
        problems.append(f"missing shared planned banner banners/{PLANNED_BANNER}.svg")

    pages: dict[str, Page] = {}

    def claim(slug: str, where: str) -> bool:
        if not SLUG.match(str(slug)) or slug == "index":
            problems.append(f"{where}: slug {slug!r} must be lowercase words joined by hyphens")
            return False
        if slug in pages:
            problems.append(f"{where}: slug {slug} is already used by {pages[slug].url}")
            return False
        return True

    # explainers
    sections: list[Section] = []
    for s_slug, s in SECTIONS.items():
        section = Section(s_slug, s["title"], s["label"], s["color"], f"{s_slug}/index.html")
        sections.append(section)
        allowed = {"slug", "title", "summary"} | s["required"] | s["optional"]
        for entry in _yaml(root / "catalog" / f"{s_slug}.yaml", problems, []) or []:
            slug = entry.get("slug", "?")
            where = f"catalog/{s_slug}.yaml {slug}"
            missing = ({"slug", "title", "summary"} | s["required"]) - entry.keys()
            unknown = entry.keys() - allowed
            if missing or unknown:
                problems.append(f"{where}: missing {sorted(missing)} unknown {sorted(unknown)} keys "
                                "(quote a title or summary that contains a colon)")
                continue
            if not claim(slug, where):
                continue
            source = root / "content" / s_slug / f"{slug}.md"
            written = source.exists()
            data = {k: v for k, v in entry.items() if k not in {"slug", "title", "summary"}}
            for key in s["optional"] & {"related", "substitutes", "allergens"}:
                data[key] = data.get(key) or []
            page = Page("explainer", slug, entry["title"], entry["summary"], f"{s_slug}/{slug}.html",
                        body_md=source.read_text(encoding="utf-8") if written else "",
                        section=s_slug, written=written, data=data)
            if written:
                banner = banners / f"{slug}.svg"
                if banner.exists():
                    page.banner_svg = banner.read_text(encoding="utf-8")
                else:
                    problems.append(f"{slug}: written explainer has no banner banners/{slug}.svg")
            page.banner_svg = page.banner_svg or planned_svg
            if "category" in data and data["category"] not in labels.get("categories", {}):
                problems.append(f"{where}: unknown category {data['category']} (add it to labels.yaml)")
            if s_slug == "suroviny":
                _check_ingredient(page, where, allergen_slugs, problems)
            pages[slug] = page
            section.pages.append(page)
        content_dir = root / "content" / s_slug
        for source in sorted(content_dir.glob("*.md")) if content_dir.exists() else []:
            page = pages.get(source.stem)
            if page is None or page.section != s_slug:
                problems.append(f"content/{s_slug}/{source.name}: not in catalog/{s_slug}.yaml")

    # groups
    groups: list[Group] = []
    for g in _yaml(root / "catalog" / "skupiny.yaml", problems, []) or []:
        slug = g.get("slug", "?")
        unknown = set(g) - {"slug", "kind", "title", "summary", "color"}
        if unknown or g.get("kind") not in GROUP_KINDS or "title" not in g:
            problems.append(f"catalog/skupiny.yaml {slug}: needs title and kind {list(GROUP_KINDS)}, "
                            f"unknown keys {sorted(unknown)}")
            continue
        color = g.get("color", COLORS[len(groups) % len(COLORS)])
        if color not in COLORS:
            problems.append(f"catalog/skupiny.yaml {slug}: color must be one of {list(COLORS)}")
        url = f"{BASIC_GROUP}/index.html" if slug == BASIC_GROUP else f"skupiny/{slug}.html"
        groups.append(Group(slug, g["kind"], g["title"], g.get("summary", ""), color, url))
    group_slugs = {g.slug for g in groups}
    if BASIC_GROUP not in group_slugs:
        problems.append(f"catalog/skupiny.yaml: the group {BASIC_GROUP} must exist")

    # recipes
    recipes: list[Page] = []
    recipes_dir = root / "content" / "recepty"
    for source in sorted(recipes_dir.glob("*.md")) if recipes_dir.exists() else []:
        slug = source.stem
        where = source.relative_to(root).as_posix()
        if not claim(slug, where):
            continue
        try:
            fm, body = _read_frontmatter(source.read_text(encoding="utf-8"))
        except (ValueError, yaml.YAMLError) as e:
            problems.append(f"{where}: {e}")
            continue
        page = _load_recipe(slug, where, fm, body, root, units, labels, group_slugs,
                            allergen_slugs, problems)
        if page:
            pages[slug] = page
            recipes.append(page)

    # cross-references
    for page in pages.values():
        page.links = _ordered_unique(m.group(1).strip() for m in LINK.finditer(page.body_md))
        for slug in page.links:
            if slug not in pages:
                problems.append(f"{page.slug}: links to unknown [[{slug}]]")
        for key in ("related", "substitutes"):
            for slug in page.data.get(key, []) or []:
                target = pages.get(slug)
                if target is None or target.kind != "explainer":
                    problems.append(f"{page.slug}: {key} names unknown explainer {slug}")
                elif key == "substitutes" and target.section != "suroviny":
                    problems.append(f"{page.slug}: substitute {slug} is not an ingredient")
        for item in page.ingredients:
            target = pages.get(item)
            if target is None:
                problems.append(f"{page.slug}: ingredient {item} is not in catalog/suroviny.yaml "
                                "and is not a recipe")
            elif not ((target.kind == "explainer" and target.section == "suroviny")
                      or (target.kind == "recipe" and target.is_basic)):
                problems.append(f"{page.slug}: ingredient {item} must be an ingredient or a basic "
                                f"(a recipe in group {BASIC_GROUP})")
            elif item == page.slug:
                problems.append(f"{page.slug}: uses itself as an ingredient")
    # recipes first in backlinks, so "Použito v receptech" lists them before explainers
    for page in sorted(pages.values(), key=lambda p: p.kind != "recipe"):
        for slug in _ordered_unique([*page.ingredients, *page.links]):
            if slug in pages and slug != page.slug:
                pages[slug].backlinks.append(page.slug)

    if not problems:
        _derive_all(recipes, pages, problems)

    if problems:
        raise BuildError(problems)

    recipes.sort(key=lambda p: (p.updated, p.slug), reverse=True)
    for group in groups:
        group.recipes = [p for p in recipes if group.slug in p.groups]
    for section in sections:  # written first, then planned, each in catalog order
        section.pages = [p for p in section.pages if p.written] + [p for p in section.pages if not p.written]
    return Site(meta, labels, units, allergens, sections, groups, recipes, pages)


def _check_ingredient(page: Page, where: str, allergen_slugs: set, problems: list[str]) -> None:
    d = page.data
    if d["animal"] not in ANIMAL:
        problems.append(f"{where}: animal must be one of {list(ANIMAL)}")
    season = d["season"]
    if season != "all-year" and not (
        isinstance(season, list) and season and all(type(m) is int and 1 <= m <= 12 for m in season)
    ):
        problems.append(f"{where}: season must be all-year or a list of month numbers 1-12")
    for a in d.get("allergens", []) or []:
        if a not in allergen_slugs:
            problems.append(f"{where}: unknown allergen {a}")
    if "density" in d and not _number(d["density"]):
        problems.append(f"{where}: density must be a positive number (grams per millilitre)")


def _load_recipe(slug, where, fm, body, root, units, labels, group_slugs, allergen_slugs, problems):
    missing = RECIPE_REQUIRED - fm.keys()
    unknown = fm.keys() - RECIPE_REQUIRED - RECIPE_OPTIONAL
    if missing or unknown:
        problems.append(f"{where}: missing {sorted(missing)} unknown {sorted(unknown)} frontmatter keys")
        return None
    if fm["status"] not in STATUSES:
        problems.append(f"{where}: status must be one of {list(STATUSES)}")
    for key in ("servings", "time_active_min", "time_total_min"):
        if type(fm[key]) is not int or fm[key] < 1:
            problems.append(f"{where}: {key} must be a whole number from 1")
    for key, value in (("difficulty", fm["difficulty"]), ("cuisine", fm["cuisine"])):
        if value not in labels.get(key, {}):
            problems.append(f"{where}: unknown {key} {value} (add it to labels.yaml)")
    season = fm.get("season") or []
    for s in season:
        if s not in labels.get("season", {}):
            problems.append(f"{where}: unknown season {s}")
    groups = fm["groups"] or []
    if not groups:
        problems.append(f"{where}: a recipe needs at least one group")
    for g in groups:
        if g not in group_slugs:
            problems.append(f"{where}: unknown group {g} (add it to catalog/skupiny.yaml)")
    for key, valid in (("allergens", allergen_slugs), ("diet", set(DIETS))):
        for v in fm.get(key) or []:
            if v not in valid:
                problems.append(f"{where}: unknown {key} value {v}")

    changes = []
    for c in fm["changes"] or []:
        if not isinstance(c, dict) or set(c) != {"date", "note"} or not isinstance(c["date"], dt.date):
            problems.append(f"{where}: each change needs a date like 2026-11-20 and a note")
            continue
        changes.append(c)
    if not changes:
        problems.append(f"{where}: changes needs at least one entry (the first version)")
    changes.sort(key=lambda c: c["date"], reverse=True)

    ingredient_groups = []
    for g in fm["ingredient_groups"] or []:
        if not isinstance(g, dict) or set(g) - {"name", "items"} or not g.get("items"):
            problems.append(f"{where}: each ingredient group needs items (and an optional name)")
            continue
        items = []
        for raw in g["items"]:
            item = _load_item(raw, where, units, problems)
            if item:
                items.append(item)
        ingredient_groups.append(IngredientGroup(g.get("name", ""), items))
    if not ingredient_groups:
        problems.append(f"{where}: ingredient_groups is empty")

    photo = None
    for ext in ("webp", "jpg", "jpeg", "png"):
        candidate = root / "photos" / f"{slug}.{ext}"
        if candidate.exists():
            photo = candidate
            break
    if fm["status"] == "tested" and photo is None:
        problems.append(f"{where}: a tested recipe needs a photo photos/{slug}.webp "
                        "(run scripts/import_photo.py)")
    # A recipe with problems still joins the site, so its links and ingredients are checked too;
    # the build fails at the end anyway.
    return Page(
        "recipe", slug, fm["title"], fm["summary"], f"recepty/{slug}.html", body_md=body,
        recipe_status=fm["status"], servings=fm["servings"], time_active_min=fm["time_active_min"],
        time_total_min=fm["time_total_min"], difficulty=fm["difficulty"], cuisine=fm["cuisine"],
        season=season, groups=groups, ingredient_groups=ingredient_groups, changes=changes,
        allergens_override=fm.get("allergens"), diet_override=fm.get("diet"), photo_source=photo,
    )


def _load_item(raw, where, units, problems) -> Item | None:
    if not isinstance(raw, dict) or "item" not in raw:
        problems.append(f"{where}: ingredient {raw!r} needs an item slug")
        return None
    unknown = set(raw) - {"qty", "unit", "item", "note", "text"}
    if unknown:
        problems.append(f"{where}: ingredient {raw['item']}: unknown keys {sorted(unknown)}")
        return None
    note = str(raw.get("note", ""))
    if "text" in raw:
        if "qty" in raw or "unit" in raw:
            problems.append(f"{where}: ingredient {raw['item']}: use either text or qty and unit")
            return None
        return Item(raw["item"], note=note, text=str(raw["text"]), display=str(raw["text"]))
    qty, unit_slug = raw.get("qty"), raw.get("unit")
    if not _number(qty):
        problems.append(f"{where}: ingredient {raw['item']}: qty must be a positive number")
        return None
    unit = units.get(unit_slug)
    if unit is None or not unit.in_recipes:
        problems.append(f"{where}: ingredient {raw['item']}: unknown unit {unit_slug} "
                        "(use a recipe unit from data/units.yaml)")
        return None
    return Item(raw["item"], qty, unit_slug, note, display=fmt_amount(unit, qty))


def _derive_all(recipes: list[Page], pages: dict[str, Page], problems: list[str]) -> None:
    """Allergens and diet of every recipe from its ingredients; a basic is derived before its users,
    and a basic's override passes on to the recipes that use it."""
    done: set[str] = set()

    def visit(page: Page, stack: list[str]) -> None:
        if page.slug in done:
            return
        if page.slug in stack:
            problems.append(f"{page.slug}: basics use each other in a loop: {' -> '.join([*stack, page.slug])}")
            return
        allergens: set[str] = set()
        vegetarian = vegan = True
        for slug in page.ingredients:
            target = pages[slug]
            if target.kind == "recipe":
                visit(target, [*stack, page.slug])
                allergens.update(target.allergens)
                vegetarian &= "vegetarian" in target.diet
                vegan &= "vegan" in target.diet
            else:
                allergens.update(target.data.get("allergens") or [])
                animal = target.data["animal"]
                vegetarian &= animal not in {"fish", "meat"}
                vegan &= animal == "none"
        derived = [d for d, ok in (("vegetarian", vegetarian), ("vegan", vegan)) if ok]
        page.allergens = sorted(allergens) if page.allergens_override is None else list(page.allergens_override)
        page.diet = derived if page.diet_override is None else list(page.diet_override)
        done.add(page.slug)

    for page in recipes:
        visit(page, [])


# ---------------------------------------------------------------- rendering


def _link_html(site: Site, root_prefix: str):
    def replace(m: re.Match) -> str:
        slug = m.group(1).strip()
        page = site.pages[slug]
        text = (m.group(2) or default_link_text(page.title)).strip()
        return (f'<a class="site-link is-{page.status}" data-slug="{slug}" '
                f'href="{root_prefix}{page.url}">{text}</a>')

    return replace


def render_body(site: Site, page: Page, root_prefix: str) -> str:
    """Markdown to HTML, with [[links]] resolved and the hooks the design styles."""
    html = markdown.markdown(LINK.sub(_link_html(site, root_prefix), page.body_md),
                             extensions=["tables", "sane_lists"])
    colors = iter(COLORS * 10)

    def h2(m: re.Match) -> str:
        text = m.group(1)
        return f'<h2 class="c-{H2_COLORS.get(text, next(colors))}">{text}</h2>'

    html = re.sub(r"<h2>(.*?)</h2>", h2, html)
    html = html.replace("<table>", '<div class="tablebox"><table>').replace("</table>", "</table></div>")
    if page.kind == "recipe":
        html = re.sub(r'(<h2 class="c-\w+">Postup</h2>(?:(?!<h2|<ol>).)*)<ol>', r'\1<ol class="steps">',
                      html, flags=re.S)
        html = re.sub(r'(<h2 class="c-\w+">Poznámky</h2>)(.*?)(?=<h2|\Z)',
                      lambda m: m.group(1) + m.group(2).replace("<p>", '<p class="handnote">'),
                      html, flags=re.S)
    return html


def recipe_steps(page: Page) -> list[str]:
    """Plain text of the numbered steps under '## Postup', for JSON-LD."""
    m = re.search(r"^## Postup\s*$(.*?)(?=^## |\Z)", page.body_md, flags=re.M | re.S)
    if not m:
        return []
    text = LINK.sub(lambda l: l.group(2) or l.group(1), m.group(1))
    steps = re.split(r"^\d+\.\s+", text, flags=re.M)[1:]
    return [re.sub(r"[*_`]", "", " ".join(s.split())) for s in steps]


def recipe_jsonld(site: Site, page: Page) -> str:
    base = site.meta.get("url", "").rstrip("/") + "/"
    ingredients = []
    for g in page.ingredient_groups:
        for i in g.items:
            name = default_link_text(site.pages[i.item].title)
            ingredients.append(" ".join(x for x in (i.display, name) if x) + (f", {i.note}" if i.note else ""))
    data = {
        "@context": "https://schema.org",
        "@type": "Recipe",
        "name": page.title,
        "description": page.summary,
        "url": base + page.url,
        "inLanguage": "cs",
        "recipeYield": f"{page.servings} porce" if 2 <= page.servings <= 4 else f"{page.servings} porcí",
        "prepTime": f"PT{page.time_active_min}M",
        "totalTime": f"PT{page.time_total_min}M",
        "recipeCuisine": site.label("cuisine", page.cuisine),
        "recipeCategory": [g.title for g in site.groups if g.slug in page.groups and g.kind == "course"],
        "recipeIngredient": ingredients,
        "recipeInstructions": [{"@type": "HowToStep", "text": s} for s in recipe_steps(page)],
        "datePublished": page.changes[-1]["date"].isoformat(),
        "dateModified": page.updated.isoformat(),
    }
    if page.photo:
        data["image"] = [base + page.photo[w] for w in sorted(page.photo)]
    diets = {"vegetarian": "https://schema.org/VegetarianDiet", "vegan": "https://schema.org/VeganDiet"}
    if page.diet:
        data["suitableForDiet"] = [diets[d] for d in page.diet]
    # "</" cannot appear inside a <script> element
    return json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/")


def make_photos(site: Site, out: Path, cache: Path) -> None:
    """Resize each recipe photo to PHOTO_WIDTHS as WebP, reusing results cached by source mtime."""
    from PIL import Image

    cache.mkdir(parents=True, exist_ok=True)
    (out / "photos").mkdir(parents=True, exist_ok=True)
    for page in site.recipes:
        if page.photo_source is None:
            continue
        stamp = int(page.photo_source.stat().st_mtime)
        page.photo = {}
        with Image.open(page.photo_source) as img:
            img = img.convert("RGB")
            for w in PHOTO_WIDTHS:
                name = f"{page.slug}-{w}.webp"
                cached = cache / f"{page.slug}-{w}-{stamp}.webp"
                if not cached.exists():
                    for old in cache.glob(f"{page.slug}-{w}-*.webp"):
                        old.unlink()
                    copy = img.copy()
                    if copy.width > w:
                        copy = copy.resize((w, round(copy.height * w / copy.width)), Image.LANCZOS)
                    copy.save(cached, "WEBP", quality=80)
                shutil.copyfile(cached, out / "photos" / name)
                page.photo[w] = f"photos/{name}"


def _compact_svg(svg: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<!--.*?-->", "", svg, flags=re.S)).strip()


def site_index(site: Site, category_pills: dict) -> dict:
    """The data behind search, filters and hover previews, with URLs relative to the site root.
    category_pills maps a category to its (colour, icon) from the template macros, so search draws
    the same disc as the pages."""
    banners: dict[str, int] = {}

    def entry(p: Page) -> dict:
        d = {"slug": p.slug, "kind": p.kind, "title": p.title, "summary": p.summary,
             "url": p.url, "status": p.status, "fold": fold(p.title + " " + p.summary)}
        if p.kind == "explainer":
            d["section"] = SECTIONS[p.section]["label"]
            d["banner"] = banners.setdefault(_compact_svg(p.banner_svg), len(banners))
            if p.section == "suroviny":
                d.update(category=p.category, season=p.data["season"])
        else:
            d.update(section="recept · základ" if p.is_basic else "recept", groups=p.groups,
                     season=p.season, diet=p.diet, allergens=p.allergens, difficulty=p.difficulty,
                     time_total_min=p.time_total_min, cuisine=p.cuisine)
            if p.photo:
                d["photo"] = p.photo[min(p.photo)]
        return d

    return {
        "pages": [entry(p) for p in [*site.recipes, *(p for s in site.sections for p in s.pages)]],
        "groups": [{"slug": g.slug, "title": g.title, "kind": g.kind, "url": g.url} for g in site.groups],
        "sections": [{"slug": s.slug, "title": s.title, "url": s.url} for s in site.sections],
        "units": {slug: u.as_dict() for slug, u in site.units.items() if u.in_recipes},
        "banners": list(banners),
        "categories": {c: {"label": site.label("categories", c), "colour": colour, "icon": icon}
                       for c, (colour, icon) in category_pills.items()},
    }


def season_rows(site: Site) -> list[dict]:
    """Ingredients with a seasonal list, for the calendar; all-year ingredients are left out."""
    section = next(s for s in site.sections if s.slug == "suroviny")
    rows = [p for p in section.pages if isinstance(p.data["season"], list)]
    rows.sort(key=lambda p: (min(p.data["season"]), p.title))
    return [{"page": p, "category": p.category, "months": set(p.data["season"])} for p in rows]


def converter_data(site: Site) -> dict:
    section = next(s for s in site.sections if s.slug == "suroviny")
    return {
        "from": [u for u in site.units.values() if u.ml or u.g],
        "items": [p for p in section.pages if "density" in p.data],
    }


def render_site(site: Site, out: Path, templates: Path, static: Path, cache: Path) -> list[Path]:
    env = Environment(loader=FileSystemLoader(templates), undefined=StrictUndefined, autoescape=True,
                      trim_blocks=True, lstrip_blocks=True)
    env.filters.update(minutes=fmt_minutes, date=fmt_date, number=fmt_number)
    env.globals.update(cz_plural=cz_plural, default_link_text=default_link_text, season_wheel=season_wheel,
                       COLORS=COLORS, GROUP_KINDS=GROUP_KINDS, MONTHS=MONTHS, MONTHS_SHORT=MONTHS_SHORT,
                       SECTIONS=SECTIONS)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    make_photos(site, out, cache)
    for page in site.recipes:
        page.jsonld = recipe_jsonld(site, page)
    written: list[Path] = []

    def emit(rel: str, template: str, **ctx) -> None:
        root_prefix = "../" * rel.count("/")
        html = env.get_template(template).render(site=site, root=root_prefix, current=rel, **ctx)
        path = out / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        written.append(path)

    emit("index.html", "home.html", title="", nav="recepty")
    emit("recepty/index.html", "recipes.html", title="Recepty", nav="recepty")
    for section in site.sections:
        emit(section.url, "section.html", title=section.title, nav=section.slug, section=section)
    emit("skupiny/index.html", "groups.html", title="Skupiny", nav="skupiny")
    for group in site.groups:
        emit(group.url, "group.html", title=group.title, nav="skupiny", group=group)
    emit("prevodnik/index.html", "converter.html", title="Převodník", nav="prevodnik",
         converter=converter_data(site))
    emit("sezonni-kalendar/index.html", "calendar.html", title="Sezónní kalendář", nav="kalendar",
         seasons=season_rows(site))
    emit("o-webu/index.html", "about.html", title="O webu", nav="o-webu")
    for page in site.pages.values():
        prefix = "../" * page.url.count("/")
        body = render_body(site, page, prefix) if page.body_md else ""
        if page.kind == "recipe":
            emit(page.url, "recipe.html", title=page.title, nav="recepty", page=page, body=body)
        else:
            emit(page.url, "explainer.html", title=page.title, nav=page.section, page=page, body=body)

    static_out = out / "static"
    shutil.copytree(static, static_out)
    (static_out / "index.js").write_text(
        "window.SITE_INDEX = " + json.dumps(site_index(site, env.get_template("_macros.html").module.CATEGORY_PILLS), ensure_ascii=False) + ";\n", encoding="utf-8")
    (out / ".nojekyll").write_text("", encoding="utf-8")
    written.extend(p for p in static_out.rglob("*") if p.is_file())
    return written


def build(root: Path = HERE, out: Path | None = None) -> Site:
    out = out or root / "dist"
    site = load_site(root)
    render_site(site, out, HERE / "templates", HERE / "static", root / ".cache" / "photos")
    return site


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=HERE / "dist")
    args = parser.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):  # problems quote Czech text; Windows consoles default to cp1252
        stream.reconfigure(encoding="utf-8")
    try:
        site = build(HERE, args.out)
    except BuildError as e:
        print("Build failed:", file=sys.stderr)
        for p in e.problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    explainers = [p for s in site.sections for p in s.pages]
    tested = sum(p.recipe_status == "tested" for p in site.recipes)
    print(f"Built {args.out}: {len(site.recipes)} recipes ({tested} tested), "
          f"{sum(p.written for p in explainers)}/{len(explainers)} explainers written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
