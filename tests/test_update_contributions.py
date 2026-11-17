import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from update_contributions import END, START, render, replace_section


def test_render_sorts_by_count_then_name():
    assert render(["b/x", "a/y", "a/y", "c/z", "c/z"]).splitlines()[2:] == [
        "| [a/y](https://github.com/a/y) | 2 |",
        "| [c/z](https://github.com/c/z) | 2 |",
        "| [b/x](https://github.com/b/x) | 1 |",
    ]


def test_replace_section_swaps_only_between_markers():
    text = f"before\n{START}\nold\n{END}\nafter\n"
    assert replace_section(text, "new") == f"before\n{START}\nnew\n{END}\nafter\n"
