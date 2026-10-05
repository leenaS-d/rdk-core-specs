#!/usr/bin/env python
"""Build a Markdown-driven RDK specification site.

    python build.py video/rdk8
    python build.py video/rdk8 --check
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))

from ssg import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
