"""Private recipe corpus for drafting: download TheMealDB into SQLite and look up variants of a dish.

Usage: uv run python scripts/corpus.py fetch
       uv run python scripts/corpus.py search "beef stew" [--ingredients beef,onion,paprika] [--limit 8] [--json]
       uv run python scripts/corpus.py show <id>

The corpus lives in corpus/ (git-ignored). It is reference material for comparing ratios, temperatures
and times; its text is never published or copied into the site.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import string
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
DB = HERE / "corpus" / "corpus.sqlite"
API = "https://www.themealdb.com/api/json/v1/1/search.php?f={letter}"  # "1" is the free test key
SOURCE = "themealdb"
USER_AGENT = "cookbook-corpus/0.1 (private, non-commercial recipe reference)"

SCHEMA = """
CREATE TABLE IF NOT EXISTS meals (
    id TEXT PRIMARY KEY, source TEXT, name TEXT, category TEXT, area TEXT, instructions TEXT, url TEXT
);
CREATE TABLE IF NOT EXISTS ingredients (
    meal_id TEXT, pos INTEGER, name TEXT, measure TEXT, PRIMARY KEY (meal_id, pos)
);
CREATE VIRTUAL TABLE IF NOT EXISTS meals_fts USING fts5(id UNINDEXED, name, category, area, ingredients);
"""


def http_get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def normalise(name: str) -> str:
    """'Onions' -> 'onion', 'Plain Flour' -> 'plain flour': close enough to match ingredient lists."""
    words = name.lower().strip().split()
    if words and len(words[-1]) > 3 and words[-1].endswith("s") and not words[-1].endswith("ss"):
        words[-1] = words[-1][:-1].removesuffix("e") if words[-1].endswith("oes") else words[-1][:-1]
    return " ".join(words)


def connect(db: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row
    return con


def fetch(db: Path | None = None, get=http_get_json) -> int:
    """Download every meal letter by letter; a re-run replaces what is stored. Returns the meal count."""
    db = db or DB
    db.parent.mkdir(parents=True, exist_ok=True)
    con = connect(db)
    con.executescript(SCHEMA)
    for letter in string.ascii_lowercase:
        for meal in get(API.format(letter=letter)).get("meals") or []:
            store(con, meal)
    con.commit()
    count = con.execute("SELECT COUNT(*) FROM meals").fetchone()[0]
    con.close()
    return count


def store(con: sqlite3.Connection, meal: dict) -> None:
    mid = f"{SOURCE}-{meal['idMeal']}"
    items = []
    for i in range(1, 21):
        name = (meal.get(f"strIngredient{i}") or "").strip()
        if name:
            items.append((name, (meal.get(f"strMeasure{i}") or "").strip()))
    con.execute("INSERT OR REPLACE INTO meals VALUES (?, ?, ?, ?, ?, ?, ?)",
                (mid, SOURCE, meal.get("strMeal", ""), meal.get("strCategory") or "", meal.get("strArea") or "",
                 meal.get("strInstructions") or "", meal.get("strSource") or ""))
    con.execute("DELETE FROM ingredients WHERE meal_id = ?", (mid,))
    con.executemany("INSERT INTO ingredients VALUES (?, ?, ?, ?)",
                    [(mid, pos, normalise(n), m) for pos, (n, m) in enumerate(items, 1)])
    con.execute("DELETE FROM meals_fts WHERE id = ?", (mid,))
    con.execute("INSERT INTO meals_fts VALUES (?, ?, ?, ?, ?)",
                (mid, meal.get("strMeal", ""), meal.get("strCategory") or "", meal.get("strArea") or "",
                 " ".join(n for n, _ in items)))


def _fts_query(text: str) -> str:
    words = re.findall(r"\w+", text)
    return " OR ".join(f'"{w}"' for w in words)


def search(query: str = "", ingredients: list[str] | None = None, limit: int = 8, db: Path | None = None) -> list[dict]:
    """Meals ranked by text match and by how many of the wanted ingredients they share."""
    db = db or DB
    if not db.exists():
        raise FileNotFoundError("No corpus yet: run `uv run python scripts/corpus.py fetch` first.")
    con = connect(db)
    scores: dict[str, float] = {}
    if query.strip():
        rows = con.execute("SELECT id, bm25(meals_fts, 0, 10, 2, 2, 1) AS r FROM meals_fts "
                           "WHERE meals_fts MATCH ? ORDER BY r LIMIT 200", (_fts_query(query),)).fetchall()
        for row in rows:
            scores[row["id"]] = -row["r"]  # bm25: lower is better
    wanted = [set(normalise(i).split()) for i in ingredients or [] if i.strip()]
    if wanted:
        # one point block per wanted ingredient the meal has; "beef" matches "beef shin", not "beefsteak"
        for meal_id, names in _ingredient_words(con).items():
            shared = sum(1 for w in wanted if any(w <= n or n <= w for n in names))
            if shared:
                scores[meal_id] = scores.get(meal_id, 0) + 3 * shared
    ranked = sorted(scores, key=lambda mid: scores[mid], reverse=True)[:limit]
    result = [meal(con, mid) for mid in ranked]
    con.close()
    return result


def _ingredient_words(con: sqlite3.Connection) -> dict[str, list[set[str]]]:
    out: dict[str, list[set[str]]] = {}
    for row in con.execute("SELECT meal_id, name FROM ingredients"):
        out.setdefault(row["meal_id"], []).append(set(row["name"].split()))
    return out


def meal(con: sqlite3.Connection, mid: str) -> dict:
    row = con.execute("SELECT * FROM meals WHERE id = ?", (mid,)).fetchone()
    if row is None:
        raise KeyError(mid)
    items = con.execute("SELECT name, measure FROM ingredients WHERE meal_id = ? ORDER BY pos", (mid,)).fetchall()
    return {**dict(row), "ingredients": [{"name": i["name"], "measure": i["measure"]} for i in items]}


def format_meal(m: dict) -> str:
    head = f"## {m['name']}  [{m['id']}]  {m['area']} · {m['category']}"
    ings = "\n".join(f"- {i['measure']} {i['name']}".replace("-  ", "- ") for i in m["ingredients"])
    return f"{head}\n{ings}\n\n{m['instructions'].strip()}\n"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch", help="download TheMealDB into corpus/corpus.sqlite")
    s = sub.add_parser("search", help="find variants of a dish")
    s.add_argument("query", nargs="?", default="", help="English words, e.g. 'beef stew'")
    s.add_argument("--ingredients", default="", help="comma-separated English ingredient names")
    s.add_argument("--limit", type=int, default=8)
    s.add_argument("--json", action="store_true")
    show = sub.add_parser("show", help="print one meal in full")
    show.add_argument("id")
    args = parser.parse_args(argv)

    if args.command == "fetch":
        print(f"Stored {fetch()} meals in {DB.relative_to(HERE).as_posix()}.")
        return 0
    try:
        if args.command == "search":
            if not args.query.strip() and not args.ingredients.strip():
                parser.error("give a query, --ingredients, or both")
            found = search(args.query, args.ingredients.split(","), args.limit)
            if args.json:
                print(json.dumps(found, ensure_ascii=False, indent=1))
            else:
                print("\n".join(format_meal(m) for m in found) or "No variants found.")
            return 0
        if not DB.exists():
            raise FileNotFoundError("No corpus yet: run `uv run python scripts/corpus.py fetch` first.")
        con = connect(DB)
        print(format_meal(meal(con, args.id)))
        return 0
    except (FileNotFoundError, KeyError) as e:
        print(e.args[0] if e.args else e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
