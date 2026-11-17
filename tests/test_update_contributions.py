import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from update_contributions import render_contributions, render_languages, render_recent, replace_section


def pr(repo, title="t", closed="2026-01-01T00:00:00Z"):
    return {"repo": repo, "title": title, "url": f"https://github.com/{repo}/pull/1", "closed": closed}


def test_contributions_summary_and_sort():
    out = render_contributions([pr("b/x"), pr("a/y"), pr("a/y"), pr("c/z"), pr("c/z")], reviews=7).splitlines()
    assert out[0] == "**5** merged PRs across **3** projects, and **7** PRs reviewed."
    assert out[4:] == [
        "| [a/y](https://github.com/a/y) | 2 |",
        "| [c/z](https://github.com/c/z) | 2 |",
        "| [b/x](https://github.com/b/x) | 1 |",
    ]


def test_recent_newest_first_limited_and_brackets_escaped():
    prs = [pr("a/b", "old", "2026-01-01T00:00:00Z"), pr("a/b", "new [x]", "2026-03-01T00:00:00Z"),
           pr("a/b", "mid", "2026-02-01T00:00:00Z")]
    lines = render_recent(prs, n=2).splitlines()
    assert lines == [
        "- [new \\[x\\]](https://github.com/a/b/pull/1) in [a/b](https://github.com/a/b), 2026-03-01",
        "- [mid](https://github.com/a/b/pull/1) in [a/b](https://github.com/a/b), 2026-02-01",
    ]


def test_languages_percent_and_cap():
    out = render_languages(Counter({"Python": 75, "TypeScript": 25, "Shell": 1}), n=2).splitlines()
    assert out[2:] == ["| Python | 74.3% |", "| TypeScript | 24.8% |"]


def test_replace_section_swaps_only_named_markers():
    text = "a\n<!-- x:start -->\nold\n<!-- x:end -->\n<!-- y:start -->\nkeep\n<!-- y:end -->\n"
    assert replace_section(text, "x", "new") == "a\n<!-- x:start -->\nnew\n<!-- x:end -->\n<!-- y:start -->\nkeep\n<!-- y:end -->\n"
