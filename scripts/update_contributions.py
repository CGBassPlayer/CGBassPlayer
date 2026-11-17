import re
import subprocess
from collections import Counter
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
QUERY = "author:CGBassPlayer type:pr is:merged -user:CGBassPlayer -org:goodwinlabs"
START, END = "<!-- contributions:start -->", "<!-- contributions:end -->"


def fetch_repos() -> list[str]:
    out = subprocess.run(
        ["gh", "api", "--paginate", "search/issues", "-X", "GET", "-f", f"q={QUERY}", "-f", "per_page=100",
         "--jq", ".items[].repository_url"],
        check=True, capture_output=True, text=True,
    ).stdout
    return [url.rsplit("repos/", 1)[1] for url in out.split()]


def render(repos: list[str]) -> str:
    rows = [
        f"| [{repo}](https://github.com/{repo}) | {n} |"
        for repo, n in sorted(Counter(repos).items(), key=lambda kv: (-kv[1], kv[0]))
    ]
    return "\n".join(["| Project | Merged PRs |", "| --- | ---: |", *rows])


def replace_section(text: str, body: str) -> str:
    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)
    return pattern.sub(lambda _: f"{START}\n{body}\n{END}", text)


if __name__ == "__main__":
    README.write_text(replace_section(README.read_text(), render(fetch_repos())))
