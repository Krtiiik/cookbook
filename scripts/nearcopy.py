"""Near-copy check: flag draft sentences that share a long word run with a saved source text.

Usage: uv run python scripts/nearcopy.py content/recepty/<slug>.md [SOURCES_DIR]

SOURCES_DIR defaults to corpus/sources/<slug>/ (private, git-ignored). Each *.txt there is the recipe
text of one Czech source page, with its URL on line 1; variant-researcher saves them.
Text is compared without case and diacritics. A run of MIN_RUN or more consecutive shared words is a
hit. The ingredient list is not compared: shared ingredient names are expected and not protected.
Exit 1 on any hit, 0 when clean or when there are no sources. Only same-language sources make sense;
close translations of English sources are left to the reviewer.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
MIN_RUN = 6
LINK = re.compile(r"\[\[([^\]|]+?)(?:\|([^\]]+?))?\]\]")


@dataclass
class Hit:
    sentence: str  # the draft sentence, as written
    source: Path
    url: str
    words: list[str]  # the shared run, folded


def fold_words(text: str) -> list[str]:
    plain = unicodedata.normalize("NFD", text)
    plain = "".join(c for c in plain if not unicodedata.combining(c)).lower()
    return re.findall(r"[a-z0-9]+", plain)


def draft_sentences(markdown: str) -> list[str]:
    """Body sentences of a draft: frontmatter dropped, [[slug|text]] reduced to its text."""
    if markdown.startswith("---"):
        parts = re.split(r"^---[ \t]*$", markdown, maxsplit=2, flags=re.MULTILINE)
        markdown = parts[2] if len(parts) == 3 else markdown
    markdown = LINK.sub(lambda m: m.group(2) or m.group(1), markdown)
    sentences = []
    for line in markdown.splitlines():
        line = re.sub(r"^\s*(#+|[-*]|\d+\.)\s*", "", line).strip()
        if line:
            sentences.extend(s.strip() for s in re.split(r"(?<=[.!?:])\s+", line) if s.strip())
    return sentences


def read_source(path: Path) -> tuple[str, list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    url = lines[0].strip() if lines else ""
    return url, fold_words("\n".join(lines[1:]))


def shared_runs(words: list[str], source: list[str], min_run: int = MIN_RUN) -> list[list[str]]:
    """Longest runs of consecutive words that also appear consecutively in source (at least min_run)."""
    grams = {tuple(source[i:i + min_run]) for i in range(len(source) - min_run + 1)}
    text = " " + " ".join(source) + " "
    runs, i = [], 0
    while i <= len(words) - min_run:
        if tuple(words[i:i + min_run]) in grams:
            end = i + min_run
            while end < len(words) and f" {' '.join(words[i:end + 1])} " in text:
                end += 1
            runs.append(words[i:end])
            i = end
        else:
            i += 1
    return runs


def check(draft: Path, sources_dir: Path, min_run: int = MIN_RUN) -> list[Hit]:
    sources = [(p, *read_source(p)) for p in sorted(sources_dir.glob("*.txt"))] if sources_dir.is_dir() else []
    hits = []
    for sentence in draft_sentences(draft.read_text(encoding="utf-8")):
        words = fold_words(sentence)
        for path, url, source_words in sources:
            for run in shared_runs(words, source_words, min_run):
                hits.append(Hit(sentence, path, url, run))
    return hits


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("draft", type=Path)
    parser.add_argument("sources", type=Path, nargs="?")
    args = parser.parse_args(argv)
    sources = args.sources or HERE / "corpus" / "sources" / args.draft.stem
    if not sources.is_dir() or not any(sources.glob("*.txt")):
        print(f"No saved sources in {sources}; nothing to compare.")
        return 0
    hits = check(args.draft, sources)
    for h in hits:
        print(f"- {h.sentence}\n  {h.source.name} {h.url}\n  shared: {' '.join(h.words)}")
    print(f"{len(hits)} near-copy hit(s)." if hits else "clean")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
