---
name: write-recipe
description: Draft one recipe end to end - research variants, write, check with reviewer, fact-checker and test-cook until clean, build, look, commit. Use when the user asks to write or add a recipe to the cooking site.
argument-hint: <dish name | recipe slug to revise>
---

Run the site's agents to draft one recipe. The result is a recipe with `status: draft`; it becomes tested only after the owner cooks it (`mark-tested`).

You (the main session) only dispatch agents, run the build and commit. The agents write and judge.

## 1. Brief

Settle with the user, unless the argument or a planner suggestion already gives it: the Czech title, the slug (Czech name without diacritics), groups from `catalog/skupiny.yaml`, the season, and anything the user said (servings, a family version, what to avoid). A new group needs the user's yes before it goes into the catalog.

## 2. Research

Dispatch `variant-researcher` with the dish, the slug and the brief. Keep its source list for step 4.

For a revision of an existing recipe, skip this step unless the user wants new variants.

## 3. Write

Dispatch `writer` with the brief and the researcher's report (not its sources' text). The writer adds missing ingredients to `catalog/suroviny.yaml` as planned entries.

## 4. Check until clean

Dispatch in parallel, each with the slug and the file path:

- `reviewer`
- `fact-checker` (also checks the catalog entries the writer added)
- `test-cook`

The near-copy rule: no sentence may be close to a source. Run `uv run python scripts/nearcopy.py content/recepty/<slug>.md`; it compares the draft with the Czech sources the researcher saved in `corpus/sources/<slug>/`. Send every hit to the writer as a blocker, and run it again after each writer pass. The script cannot compare Czech with English, so also give the reviewer the researcher's English source list and ask it to flag sentences that read like close translations.

The recipe is **clean** when all three end with `clean` and `nearcopy.py` prints `clean` (or finds no saved sources). If not, send the blocker and major findings (minor ones too, if cheap) to `writer`, then check again. After a clean round you may send cheap minor findings in one last pass and skip the re-check, unless the writer changed a fact, a number, an amount or the steps.

Stop and ask the user when the writer rejects a finding and the next round raises it again: the agents disagree and the user decides.

## 5. Build and look

1. Run `uv run python scripts/build.py` and `uv run pytest`. Send build errors to the writer.
2. Open the recipe with `preview_start` (`site`) and look in light and dark mode, at desktop and phone width: the ingredient list, the scaler at half and double, the step links and their previews, the derived allergens and diet in the facts box.

## 6. Commit

Commit the recipe and its new catalog entries together, for example `feat: draft the svíčková recipe`.

Report to the user: the recipe, its derived allergens and diet, the new planned explainers it created, the number of check rounds, findings the writer rejected and why, and minor findings left open. Remind the user that the recipe is a draft until it is cooked.
