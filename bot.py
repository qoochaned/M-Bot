import os, requests

BEARER = os.environ["X_BEARER_TOKEN"]
USER_ID = os.environ["X_USER_ID"]
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
KEYWORDS = ["出場選手発表", "試合結果"]
STATE = "last_id.txt"

since = open(STATE).read().strip() if os.path.exists(STATE) else None
params = {"max_results": 10, "exclude": "retweets,replies"}
if since:
    params["since_id"] = since

r = requests.get(
    f"https://api.x.com/2/users/{USER_ID}/tweets",
    headers={"Authorization": f"Bearer {BEARER}"},
    params=params, timeout=30,
)
r.raise_for_status()
posts = r.json().get("data", [])

if posts:
    posts.sort(key=lambda p: int(p["id"]))
    # 初回実行時は過去分を投稿せず、最新IDの記録だけ行う
    if since:
        for p in posts:
            if any(k in p["text"] for k in KEYWORDS):
                requests.post(WEBHOOK, json={
                    "content": f"https://x.com/m_league_/status/{p['id']}"
                }, timeout=30).raise_for_status()
    open(STATE, "w").write(posts[-1]["id"])
