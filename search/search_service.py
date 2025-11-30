# ...existing code...
import requests
from flask import Flask, request, jsonify
from rapidfuzz import process, fuzz

app = Flask(__name__)

DJANGO_USERS_API = "http://127.0.0.1:8000/api/users/"

# ...existing code...
@app.route("/search")
@app.route("/search/")
def search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": [], "query": q})

    try:
        resp = requests.get(DJANGO_USERS_API, timeout=2)
        resp.raise_for_status()
        users = resp.json()
        usernames = [u.get("username") for u in users if u.get("username")]
    except requests.exceptions.RequestException:
        return jsonify({"results": [], "query": q})

    # build lowercase mapping to preserve original casing and handle duplicates
    lower_map = {}
    for name in usernames:
        key = name.lower()
        lower_map.setdefault(key, []).append(name)

    q_l = q.lower()

    # exact case-insensitive matches first (force top with score 100)
    results = []
    added = set()
    for orig in lower_map.get(q_l, []):
        results.append({"username": orig, "score": 100})
        added.add(orig)

    # fuzzy match on lowercased choices
    choices = list(lower_map.keys())
    scorer = fuzz.token_sort_ratio
    raw_matches = process.extract(q_l, choices, scorer=scorer, limit=50)

    THRESHOLD = 55
    for lower_name, score, _ in raw_matches:
        if score < THRESHOLD:
            continue
        for orig in lower_map.get(lower_name, []):
            if orig in added:
                continue
            results.append({"username": orig, "score": score})
            added.add(orig)
        if len(results) >= 20:
            break

    return jsonify({"results": results, "query": q})
# ...existing code...

if __name__ == "__main__":
    app.run(port=5001, debug=True)
# ...existing code...