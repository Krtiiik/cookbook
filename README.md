# Cookbook

Krtkova Kuchařka: a Czech recipe collection with pages about methods, ingredients, equipment and troubleshooting. A small Python build turns Markdown and YAML into a static site on GitHub Pages.

```
uv sync
uv run python scripts/build.py     # builds dist/
uv run pytest                      # tests
uv run python scripts/serve.py     # serves dist/ on http://localhost:8766/
```

- `docs/BRIEF.md`: what the site is and how content is organised.
- `docs/STYLE.md`: the visual style.
- `SPEC.md`: the contract between the build, the templates and the scripts.

Content is licensed under CC BY-NC-SA 4.0.
