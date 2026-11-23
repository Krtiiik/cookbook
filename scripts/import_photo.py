"""Shrink a recipe photo and store it as photos/<slug>.webp.

Usage: uv run python scripts/import_photo.py PATH SLUG

The original stays where it is (outside the repository). The copy is at most 2000 px on its long
side, WebP, and has no metadata, so GPS position and camera data from the phone are not published.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parents[1]
LONG_SIDE = 2000


def import_photo(source: Path, slug: str, photos: Path = HERE / "photos") -> Path:
    photos.mkdir(parents=True, exist_ok=True)
    target = photos / f"{slug}.webp"
    with Image.open(source) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")  # keep the phone's rotation, then drop EXIF
        img.thumbnail((LONG_SIDE, LONG_SIDE), Image.LANCZOS)
        img.save(target, "WEBP", quality=85)  # no exif= argument: metadata is not written
    return target


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path, help="the original photo")
    parser.add_argument("slug", help="the recipe slug, e.g. hovezi-gulas")
    args = parser.parse_args(argv)
    if not (HERE / "content" / "recepty" / f"{args.slug}.md").exists():
        print(f"No recipe content/recepty/{args.slug}.md", file=sys.stderr)
        return 1
    target = import_photo(args.path, args.slug)
    print(f"Saved {target.relative_to(HERE).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
