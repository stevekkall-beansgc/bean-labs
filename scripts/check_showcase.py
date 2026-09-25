#!/usr/bin/env python3
"""Check local Markdown targets and SVG XML in the static showcase."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: list[str] = []

    for source in sorted(root.rglob("*.md")):
        if ".git" in source.parts:
            continue
        content = source.read_text(encoding="utf-8")
        for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            target = destination.strip().split("#", 1)[0].strip("<>")
            if not target or urlparse(target).scheme or target.startswith("//"):
                continue
            local = (source.parent / unquote(target)).resolve()
            if not local.is_file():
                errors.append(f"{source.relative_to(root)}: missing local target {target}")

    for diagram in sorted(root.rglob("*.svg")):
        try:
            ET.parse(diagram)
        except ET.ParseError as exc:
            errors.append(f"{diagram.relative_to(root)}: invalid SVG XML: {exc}")

    if errors:
        print("\n".join(errors))
        return 1
    print("Local Markdown targets and SVG XML are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
