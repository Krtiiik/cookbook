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

## Batches

When the user asks for several explainers, run up to 4 at once through the same steps, in lockstep: all writers and illustrators, then all checkers, then one fix round for the pages that need it.

- **Pick** pages that share a topic (the methods, the meat problems, the spices), so one map covers them. Link count from written pages first: `grep -rohE "\[\[[a-z0-9-]+|item: [a-z0-9-]+" content | sort | uniq -c | sort -rn`.
- **Topic map** in every writer's brief: which page of the batch owns which idea (the Maillard reaction lives in `browning`; `caramelising` links to it). Writers in one batch cannot see each other's pages, so the map is what keeps them from saying the same thing twice or differently. Start from "Owner page" in `.claude/CONTEXT.md` and add the batch's new owners there when you commit.
- **Re-check cheaply:** after the fix round, one `fact-checker` on only the changed claims of all pages, together with the auditor, replaces a full second round per page.
- **Shared files:** writers do not edit `catalog/` in a batch. They report catalog changes they want, and you apply them once, after the writers finish. Illustrators touch only their own `banners/<slug>.svg`.
- **Auditor** after the batch is clean, on the whole site: it finds drift between the new pages and the old ones. Send its blocker and major findings to the writers of the pages it names.
- **Commit** one commit per explainer, after the whole batch builds.
