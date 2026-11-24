---
name: write-explainer
description: Write one explainer (method, ingredient, equipment or troubleshooting page) end to end - writer and illustrator, review and fact check until clean, build, banner check, commit. Use when the user asks to write an explainer for the cooking site.
argument-hint: <explainer slug>
---

Run the site's agents to write one explainer. The argument names a slug from a catalog in `catalog/`.

You (the main session) only dispatch agents, run the build and commit. The agents write and judge.

## 1. Brief

Find the slug in `catalog/metody.yaml`, `suroviny.yaml`, `vybaveni.yaml` or `reseni-problemu.yaml`. If it is not there, ask the user whether to add it, and to which section, before you go on.

The brief is the slug, section, title, summary, the catalog data, the recipes that link to or use it (`grep -r "\[\[<slug>\|item: <slug>" content`), and anything the user said about the page.

## 2. Write and draw

Dispatch in parallel:

- `writer` with the brief.
- `illustrator` with the brief.

## 3. Check until clean

Dispatch in parallel, each with the slug and the file path:

- `reviewer`
- `fact-checker` (also checks the catalog entry)

The page is **clean** when both end with `clean`. If not, send the blocker and major findings (minor ones too, if cheap) to `writer`, and banner findings to `illustrator`. Then check again. After a clean round you may send cheap minor findings in one last pass and skip the re-check, unless the writer changed a fact, a number or the page's structure.

Stop and ask the user when the writer rejects a finding and the next round raises it again.

## 4. Build and look

1. Run `uv run python scripts/build.py` and `uv run pytest`. Send build errors to the agent that owns the file.
2. Open the page with `preview_start` (`site`) and look at the banner and page in light and dark mode, at desktop and phone width, and at the banner at card size on the section page. Send what looks wrong (clipped text, overlap, unclear picture, unreadable notes) to `illustrator`, then look again.

## 5. Commit

Commit content, banner and any catalog change together, for example `feat: write the braising explainer`.

Report to the user: the page, the number of check rounds, findings the writer rejected and why, and minor findings left open.
