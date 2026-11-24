import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


corpus = _load("cookbook_corpus", "corpus.py")


def themealdb(id_, name, category, area, ingredients, instructions="Cook it."):
    meal = {"idMeal": id_, "strMeal": name, "strCategory": category, "strArea": area,
            "strInstructions": instructions, "strSource": ""}
    for i, (ing, measure) in enumerate(ingredients, 1):
        meal[f"strIngredient{i}"] = ing
        meal[f"strMeasure{i}"] = measure
    meal["strIngredient20"] = ""  # the API pads unused slots with empty strings or null
    return meal


MEALS = {
    "b": [themealdb("1", "Beef Goulash", "Beef", "Hungarian",
                    [("Beef", "1kg"), ("Onions", "3"), ("Paprika", "2 tbs")], "Brown the beef, stew 2 hours.")],
    "c": [themealdb("2", "Chicken Curry", "Chicken", "Indian",
                    [("Chicken", "500g"), ("Onion", "1"), ("Curry Powder", "2 tbs")])],
    "t": [themealdb("3", "Tomato Soup", "Vegetarian", "British", [("Tomatoes", "1kg"), ("Onion", "1")])],
}


def fake_get(url: str) -> dict:
    letter = url.rsplit("=", 1)[1]
    return {"meals": MEALS.get(letter)}


@pytest.fixture
def db(tmp_path: Path) -> Path:
    path = tmp_path / "corpus.sqlite"
    assert corpus.fetch(path, get=fake_get) == 3
    return path


def test_fetch_stores_meals_and_a_rerun_replaces_them(db):
    assert corpus.fetch(db, get=fake_get) == 3
    goulash = corpus.search("goulash", db=db)[0]
    assert goulash["name"] == "Beef Goulash"
    assert goulash["ingredients"] == [{"name": "beef", "measure": "1kg"}, {"name": "onion", "measure": "3"},
                                      {"name": "paprika", "measure": "2 tbs"}]


@pytest.mark.parametrize("word, base", [("Onions", "onion"), ("Tomatoes", "tomato"), ("Plain Flour", "plain flour"),
                                        ("Cress", "cress"), ("Peas", "pea")])
def test_ingredient_names_are_normalised(word, base):
    assert corpus.normalise(word) == base


def test_search_ranks_by_shared_ingredients(db):
    names = [m["name"] for m in corpus.search(ingredients=["beef", "onion", "paprika"], db=db)]
    assert names[0] == "Beef Goulash"
    assert set(names) == {"Beef Goulash", "Chicken Curry", "Tomato Soup"}  # all share onion


def test_search_combines_text_and_ingredients(db):
    names = [m["name"] for m in corpus.search("soup", ["tomato"], db=db)]
    assert names == ["Tomato Soup"]


def test_search_json_output_is_valid(db, monkeypatch, capsys):
    monkeypatch.setattr(corpus, "DB", db)
    assert corpus.main(["search", "curry", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["area"] == "Indian"


def test_search_without_a_corpus_asks_for_fetch(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(corpus, "DB", tmp_path / "missing.sqlite")
    assert corpus.main(["search", "goulash"]) == 1
    assert "corpus.py fetch" in capsys.readouterr().err
