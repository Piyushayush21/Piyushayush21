"""
Generates assets/stats-card.svg — a bespoke, on-brand dashboard card built
from your real GitHub data (not a third-party badge generator).

Run in CI via .github/workflows/update-stats.yml, which supplies GH_TOKEN
and commits the regenerated SVG on a schedule.

Requires: pip install requests
"""

import os
import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "Piyushayush21")
TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes {
        stargazerCount
        primaryLanguage { name }
      }
    }
  }
}
"""


def fetch_stats():
    resp = requests.post(
        "https://api.github.com/graphql",
        json={"query": QUERY, "variables": {"login": USERNAME}},
        headers={"Authorization": f"bearer {TOKEN}"},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()["data"]["user"]

    repos = data["repositories"]["nodes"]
    total_stars = sum(r["stargazerCount"] for r in repos)

    lang_counts = {}
    for r in repos:
        lang = r["primaryLanguage"]["name"] if r["primaryLanguage"] else None
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    top_lang = max(lang_counts, key=lang_counts.get) if lang_counts else "—"

    return {
        "followers": data["followers"]["totalCount"],
        "contributions": data["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "stars": total_stars,
        "repos": len(repos),
        "top_lang": top_lang,
    }


def render_svg(stats):
    return f"""<svg width="900" height="180" viewBox="0 0 900 180" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="edge" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#7C3AED"/>
      <stop offset="100%" stop-color="#00E5FF"/>
    </linearGradient>
  </defs>
  <rect width="900" height="180" rx="14" fill="#05070d"/>
  <rect x="1" y="1" width="898" height="178" rx="13" fill="none" stroke="url(#edge)" stroke-opacity="0.4"/>
  <text x="30" y="34" font-family="JetBrains Mono, Consolas, monospace" font-size="13" fill="#556072">$ curl api.github.com/users/{USERNAME}/stats --live</text>

  <g font-family="JetBrains Mono, Consolas, monospace" text-anchor="middle">
    <text x="140" y="95" font-size="34" font-weight="700" fill="#00E5FF">{stats['contributions']}</text>
    <text x="140" y="120" font-size="12" fill="#8b95a8">contributions / yr</text>

    <text x="320" y="95" font-size="34" font-weight="700" fill="#7C3AED">{stats['repos']}</text>
    <text x="320" y="120" font-size="12" fill="#8b95a8">public repos</text>

    <text x="500" y="95" font-size="34" font-weight="700" fill="#00E5FF">{stats['stars']}</text>
    <text x="500" y="120" font-size="12" fill="#8b95a8">stars earned</text>

    <text x="680" y="95" font-size="34" font-weight="700" fill="#7C3AED">{stats['followers']}</text>
    <text x="680" y="120" font-size="12" fill="#8b95a8">followers</text>
  </g>

  <text x="30" y="160" font-family="JetBrains Mono, Consolas, monospace" font-size="12" fill="#3d4657">top language: {stats['top_lang']} &#183; auto-refreshed daily via GitHub Actions</text>
</svg>"""


def main():
    stats = fetch_stats()
    svg = render_svg(stats)
    out_path = os.path.join(os.path.dirname(__file__), "..", "assets", "stats-card.svg")
    with open(out_path, "w") as f:
        f.write(svg)
    print("Wrote", out_path, stats)


if __name__ == "__main__":
    main()
  
