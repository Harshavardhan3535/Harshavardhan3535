"""Generate languages.svg and stats.svg for a GitHub profile from the public GitHub API.
Run by GitHub Actions (see .github/workflows/stats.yml). No third-party service involved."""
import json, os, urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Harshavardhan3535")
TOKEN = os.environ.get("GITHUB_TOKEN")
COLORS = {"Java":"#b07219","JavaScript":"#f1e05a","HTML":"#e34c26","CSS":"#563d7c",
          "TypeScript":"#3178c6","Python":"#3572A5","PLpgSQL":"#336790","SQL":"#e38c00",
          "Shell":"#89e051","Dockerfile":"#384d54"}

def get(url):
    req = urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","User-Agent":"profile-stats"})
    if TOKEN: req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

# Repos counted in the language chart. Edit this list to add or remove projects.
# Use the EXACT repo name from the repo's URL (capital letters don't matter).
INCLUDE = [
    "hospital-management-system",
    "user-auth-api",
    "blog-api",
    "library-management-system",
    "TechStore.Project",
    "student-management-system-jdbc",
    "servlet-employee-management-system",
    "Task-Management-Application-Project",
    "dsa-java",
]

all_repos = [r for r in get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner") if not r["fork"]]
repos = [r for r in all_repos if r["name"].lower() in [n.lower() for n in INCLUDE]]
found = {r["name"].lower() for r in repos}
for n in INCLUDE:
    if n.lower() not in found:
        print(f"WARNING: no repo named '{n}' found - check the spelling against the repo URL")
langs = {}
for r in repos:
    for lang, n in get(r["languages_url"]).items():
        langs[lang] = langs.get(lang, 0) + n
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
stars = sum(r["stargazers_count"] for r in all_repos)

STYLE = ('<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:14px;fill:#8b949e}'
         '.v{font-weight:600}.h{font-size:15px;font-weight:700}</style>')

# Most used languages card
W, x0, bw, rowh = 620, 150, 360, 30
H = 50 + rowh * len(top)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Most used languages">', STYLE,
     '<text class="h" x="0" y="20">Languages across my project repos</text>']
for i,(lang,n) in enumerate(top):
    pct = n*100/total
    cy = 50 + i*rowh
    c = COLORS.get(lang, "#8b949e")
    o += [f'<text x="0" y="{cy+5}">{escape(lang)}</text>',
          f'<rect x="{x0}" y="{cy-5}" width="{bw}" height="10" rx="5" fill="#8b949e" fill-opacity="0.25"/>',
          f'<rect x="{x0}" y="{cy-5}" width="{max(bw*pct/100,4):.0f}" height="10" rx="5" fill="{c}"/>',
          f'<text class="v" x="{x0+bw+14}" y="{cy+5}">{pct:.1f}%</text>']
o.append('</svg>')
open("languages.svg","w").write("\n".join(o))

# Simple numbers card
items = [("Public repos", len(all_repos)), ("Stars earned", stars)]
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="{40+30*len(items)}" role="img" aria-label="GitHub numbers">', STYLE,
     '<text class="h" x="0" y="20">GitHub at a glance</text>']
for i,(k,v) in enumerate(items):
    o += [f'<text x="0" y="{52+i*30}">{k}</text>', f'<text class="v" x="200" y="{52+i*30}">{v}</text>']
o.append('</svg>')
open("stats.svg","w").write("\n".join(o))
print("repos:", len(repos), "langs:", top)
