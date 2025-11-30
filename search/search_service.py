import requests
from flask import Flask, request, jsonify
from rapidfuzz import fuzz

app = Flask(__name__)

DJANGO_USERS_API = "http://127.0.0.1:8000/api/users/"


@app.route("/search")
@app.route("/search/")
def search():
    query = request.args.get("q", "").strip().lower()

    # If query is empty, return empty list
    if not query:
        return jsonify([])

    # Get users from Django
    users = requests.get(DJANGO_USERS_API).json()

    results = []

    for user in users:
        username = user["username"].lower()  # 👈 FIXED

        # 1️⃣ direct substring match
        if query in username:
            results.append(user)
            continue

        # 2️⃣ fuzzy match
        if fuzz.ratio(query, username) >= 50:
            results.append(user)

    return jsonify(results)


if __name__ == "__main__":
    app.run(port=5001, debug=True)
