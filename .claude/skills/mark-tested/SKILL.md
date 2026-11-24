---
name: mark-tested
description: Record that the owner cooked a recipe - import the photo, apply the owner's changes and notes, add a changes entry, set status tested, check, commit. Use when the user says they cooked a recipe, or gives notes or a photo for one.
argument-hint: <recipe slug> [photo path] [notes]
---

Turn the owner's cooking session into a tested recipe. The owner's notes are the source of truth: they cooked it.

## 1. Gather

From the argument and the user's message, get:

- the recipe slug (`content/recepty/<slug>.md`),
- the photo path (an original outside the repository),
- what the owner changed while cooking (amounts, times, steps) and what they noticed.

If the photo or the changes are missing, ask once. A recipe cannot be tested without a photo; notes are optional ("cooked as written" is fine).

## 2. Photo

Run `uv run python scripts/import_photo.py <path> <slug>`. It writes `photos/<slug>.webp` at most 2000 px wide, without metadata. Never commit the original.

## 3. Update the recipe

Dispatch `writer` with the slug and the owner's notes, and ask it to:

- apply the owner's changes to the amounts and steps, in the site's voice,
- put the owner's practical observations in Poznámky,
- set `status: tested`,
- add a `changes` entry at the top with today's date and one line of what changed, or "Otestováno, přidána fotka." when nothing changed.

## 4. Check

If the owner changed amounts, times or steps, dispatch `test-cook` and, when a number touches food safety, `fact-checker`. Send blocker and major findings to `writer`. Findings that contradict what the owner did in the kitchen go to the user to decide; the owner's experience wins unless it is a safety issue.

## 5. Build, look and commit

1. Run `uv run python scripts/build.py` and `uv run pytest`.
2. Open the recipe with `preview_start` (`site`) and check the photo in the polaroid, on the recipe card on the home page and in a link preview, at desktop and phone width.
3. Commit the recipe and the photo together, for example `feat: mark the guláš recipe as tested`.

Report to the user what changed in the recipe and the new `changes` line.
