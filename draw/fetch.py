"""Fetches the week's public activity for the ledger, with the gh CLI, and writes it as JSON.

It asks GitHub one question: for each of the three projects, the commits on the default branch and the pull requests
merged in the last seven days, and the last pull request merged; and for the account, the contributions of the last
twelve weeks, day by day. In a workflow, gh uses the workflow's own token, which sees only what is public.

The ledger covers whole days only and ends yesterday (UTC), so a run in the morning never shows a day that has
barely begun.
"""
import datetime
import json
import pathlib
import subprocess
import sys

LOGIN = "myhts"
REPOS = ["claude-kits", "claude-kits-boutique", "lombard"]
WEEKS = 12

entered = datetime.datetime.now(datetime.timezone.utc).date()
end = entered - datetime.timedelta(days=1)
week_start = end - datetime.timedelta(days=6)
# The tally starts on a Monday, so its week marks fall evenly.
tally_start = end - datetime.timedelta(days=end.weekday() + 7 * (WEEKS - 1))
since = f"{week_start.isoformat()}T00:00:00Z"
until = f"{end.isoformat()}T23:59:59Z"

repo_parts = "".join(
    f"""
  r{i}: repository(owner: "{LOGIN}", name: "{name}") {{
    defaultBranchRef {{ target {{ ... on Commit {{ history(since: "{since}", until: "{until}") {{ totalCount }} }} }} }}
    last: pullRequests(states: MERGED, first: 1, orderBy: {{field: UPDATED_AT, direction: DESC}}) {{ nodes {{ title mergedAt }} }}
  }}
  m{i}: search(type: ISSUE, query: "repo:{LOGIN}/{name} is:pr is:merged merged:{week_start.isoformat()}..{end.isoformat()}") {{ issueCount }}"""
    for i, name in enumerate(REPOS)
)
query = f"""{{
  user(login: "{LOGIN}") {{
    contributionsCollection(from: "{tally_start.isoformat()}T00:00:00Z", to: "{until}") {{
      contributionCalendar {{ weeks {{ contributionDays {{ date contributionCount }} }} }}
    }}
  }}{repo_parts}
}}"""

raw = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"], check=True, capture_output=True, text=True).stdout
data = json.loads(raw)["data"]

days = {
    d["date"]: d["contributionCount"]
    for w in data["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    for d in w["contributionDays"]
}
tally = []
day = tally_start
while day <= end:
    tally.append({"date": day.isoformat(), "count": days.get(day.isoformat(), 0)})
    day += datetime.timedelta(days=1)

rows = []
for i, name in enumerate(REPOS):
    repo = data[f"r{i}"]
    last = (repo["last"]["nodes"] or [None])[0]
    rows.append(
        {
            "name": name,
            "commits": repo["defaultBranchRef"]["target"]["history"]["totalCount"],
            "merged": data[f"m{i}"]["issueCount"],
            "last_title": last["title"] if last else "",
            "last_date": last["mergedAt"][:10] if last else "",
        }
    )

out = {"entered": entered.isoformat(), "end": end.isoformat(), "week_start": week_start.isoformat(), "rows": rows, "tally": tally}
pathlib.Path(sys.argv[1]).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
