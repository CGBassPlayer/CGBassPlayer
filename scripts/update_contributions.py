import json
import re
import subprocess
from collections import Counter
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
USER = "CGBassPlayer"
OTHERS = f"-user:{USER} -org:goodwinlabs"
MERGED = f"author:{USER} type:pr is:merged {OTHERS}"
REVIEWED = f"type:pr reviewed-by:{USER} -author:{USER} {OTHERS}"
NOT_LANGUAGES = {"JSON", "YAML", "TOML", "XML", "CSS", "SCSS", "HTML", "Markdown", "Jinja", "Smarty", "Dockerfile"}


def gh(*args: str) -> str:
    return subprocess.run(["gh", "api", *args], check=True, capture_output=True, text=True).stdout


def search(query: str, *args: str) -> str:
    return gh("-X", "GET", "search/issues", "-f", f"q={query}", *args)


def fetch_prs() -> list[dict]:
    jq = ".items[] | {repo: (.repository_url | split(\"repos/\")[1]), title, url: .html_url, closed: .closed_at}"
    out = search(MERGED, "--paginate", "-f", "per_page=100", "--jq", jq)
    return [json.loads(line) for line in out.splitlines()]


def fetch_reviews() -> int:
    return int(search(REVIEWED, "-f", "per_page=1", "--jq", ".total_count"))


def repo_names(endpoint: str) -> list[str]:
    return gh("--paginate", "-X", "GET", endpoint, "-f", "per_page=100",
              "--jq", ".[] | select(.fork | not) | select(.archived | not) | .full_name").split()


def fetch_languages() -> Counter:
    names = repo_names(f"users/{USER}/repos")
    total = Counter()
    for name in names:
        total.update(json.loads(gh(f"repos/{name}/languages")))
    return total


def render_contributions(prs: list[dict], reviews: int) -> str:
    counts = Counter(pr["repo"] for pr in prs)
    rows = [
        f"| [{repo}](https://github.com/{repo}) | {n} |"
        for repo, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    summary = f"**{len(prs)}** merged PRs across **{len(counts)}** projects, and **{reviews}** PRs reviewed."
    return "\n".join([summary, "", "| Project | Merged PRs |", "| --- | ---: |", *rows])


def render_recent(prs: list[dict], n: int = 5) -> str:
    recent = sorted(prs, key=lambda pr: pr["closed"], reverse=True)[:n]
    escape = re.compile(r"([\[\]])")
    return "\n".join(
        "- [{}]({}) in [{}](https://github.com/{}), {}".format(
            escape.sub(r"\\\1", pr["title"]), pr["url"], pr["repo"], pr["repo"], pr["closed"][:10]
        )
        for pr in recent
    )


def render_languages(langs: Counter, n: int = 5) -> str:
    langs = Counter({k: v for k, v in langs.items() if k not in NOT_LANGUAGES})
    total = sum(langs.values())
    rows = [f"| {lang} | {size / total:.1%} |" for lang, size in langs.most_common(n)]
    return "\n".join(["| Language | Share |", "| --- | ---: |", *rows])


def replace_section(text: str, name: str, body: str) -> str:
    start, end = f"<!-- {name}:start -->", f"<!-- {name}:end -->"
    pattern = re.compile(f"{re.escape(start)}.*?{re.escape(end)}", re.DOTALL)
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", text)


if __name__ == "__main__":
    prs = fetch_prs()
    text = README.read_text()
    text = replace_section(text, "contributions", render_contributions(prs, fetch_reviews()))
    text = replace_section(text, "recent", render_recent(prs))
    text = replace_section(text, "languages", render_languages(fetch_languages()))
    README.write_text(text)
