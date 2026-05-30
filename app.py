from flask import Flask, jsonify, request, send_from_directory
import threading
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, random

app = Flask(__name__, static_folder=".")

driver      = None
wait        = None
USERNAME    = ""
USER_ID     = ""
scan_status = {
    "step": "idle", "log": [], "progress": 0,
    "results": [], "followers_count": 0,
    "following_count": 0, "unfollowers_count": 0
}

# ── Serve frontend ───────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ── API: start ───────────────────────────────────────────────────
@app.route("/api/start", methods=["POST"])
def start():
    global driver, wait, USERNAME, USER_ID, scan_status
    USERNAME = request.json.get("username", "").strip().lower()
    USER_ID  = ""
    scan_status = {
        "step": "login", "log": [], "progress": 0,
        "results": [], "followers_count": 0,
        "following_count": 0, "unfollowers_count": 0
    }
    options = uc.ChromeOptions()
    options.add_argument("--lang=en-US")
    driver = uc.Chrome(options=options, version_main=148)
    wait   = WebDriverWait(driver, 20)
    driver.get("https://www.instagram.com/")
    scan_status["log"].append("[init] Chrome launched.")
    scan_status["log"].append("[auth] Waiting for manual login in browser...")
    return jsonify({"ok": True})

# ── API: confirm login ───────────────────────────────────────────
@app.route("/api/confirm-login", methods=["POST"])
def confirm_login():
    scan_status["log"].append("[auth] Login confirmed. Starting scan...")
    scan_status["step"] = "scanning"
    threading.Thread(target=run_scan, daemon=True).start()
    return jsonify({"ok": True})

# ── API: poll status ─────────────────────────────────────────────
@app.route("/api/scan-status")
def get_scan_status():
    return jsonify(scan_status)

# ── API: results ─────────────────────────────────────────────────
@app.route("/api/results")
def get_results():
    return jsonify({"results": scan_status["results"]})


# ════════════════════════════════════════════════════════════════
#  CORE ENGINE
# ════════════════════════════════════════════════════════════════

def log(msg):
    scan_status["log"].append(msg)


def resolve_user_id(username: str) -> str:
    """
    Get the numeric Instagram user ID for a username.
    Uses the browser's live session — no separate auth needed.
    """
    log(f"[init] Resolving user ID for @{username}...")
    driver.get(f"https://www.instagram.com/{username}/")
    time.sleep(random.uniform(3.0, 5.0))

    # Method 1: read from embedded JSON scripts on the profile page
    try:
        uid = driver.execute_script("""
            const scripts = document.querySelectorAll('script[type="application/json"]');
            for (const s of scripts) {
                try {
                    const str = JSON.stringify(JSON.parse(s.textContent));
                    const match = str.match(/"pk":"(\\d+)"/);
                    if (match) return match[1];
                } catch(e) {}
            }
            return null;
        """)
        if uid:
            log(f"[init] User ID found: {uid}")
            return str(uid)
    except Exception:
        pass

    # Method 2: call Instagram's web_profile_info endpoint
    try:
        uid = driver.execute_script(f"""
            const resp = await fetch(
                'https://www.instagram.com/api/v1/users/web_profile_info/?username={username}',
                {{
                    headers: {{
                        'x-ig-app-id': '936619743392459',
                        'x-csrftoken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
                    }},
                    credentials: 'include'
                }}
            );
            const data = await resp.json();
            return data?.data?.user?.id || null;
        """)
        if uid:
            log(f"[init] User ID found via profile API: {uid}")
            return str(uid)
    except Exception:
        pass

    raise Exception(
        f"Could not resolve user ID for @{username}. "
        "Make sure you are fully logged in as this account."
    )


def fetch_list_via_api(endpoint: str, label: str) -> set:
    """
    Fetch a complete followers or following list by paginating
    through Instagram's internal API using the browser's live
    session cookies.

    - Returns up to 200 accounts per page
    - Follows next_max_id pagination until the full list is done
    - No scrolling, no DOM reading, no UI interaction
    - Works for any account size
    """
    usernames   = set()
    next_max_id = ""
    page        = 1

    while True:
        url = f"https://www.instagram.com/api/v1/{endpoint}/?count=200"
        if next_max_id:
            url += f"&max_id={next_max_id}"

        log(f"[{label}] Fetching page {page} — {len(usernames)} collected so far...")

        try:
            result = driver.execute_script(f"""
                const resp = await fetch('{url}', {{
                    headers: {{
                        'x-ig-app-id': '936619743392459',
                        'x-csrftoken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '',
                        'x-requested-with': 'XMLHttpRequest'
                    }},
                    credentials: 'include'
                }});
                return await resp.json();
            """)
        except Exception as e:
            log(f"[{label}] Request failed on page {page}: {str(e)}")
            break

        if not result:
            log(f"[{label}] Empty response on page {page}. Stopping.")
            break

        users = result.get("users", [])
        if not users:
            log(f"[{label}] No more users returned. List complete.")
            break

        for user in users:
            uname = (user.get("username") or "").lower().strip()
            if uname:
                usernames.add(uname)

        log(f"[{label}] Page {page} done — +{len(users)} accounts (total: {len(usernames)})")

        # check if there's another page
        next_max_id = (
            result.get("next_max_id") or
            result.get("next_max_id_str") or
            ""
        )

        if not next_max_id:
            log(f"[{label}] ✓ All pages fetched. Final count: {len(usernames)}")
            break

        page += 1
        # polite delay between pages
        time.sleep(random.uniform(2.0, 4.0))

    return usernames


# ════════════════════════════════════════════════════════════════
#  MAIN SCAN THREAD
# ════════════════════════════════════════════════════════════════

def run_scan():
    global scan_status, USER_ID

    try:
        # ── Resolve numeric user ID ──────────────────────────────
        USER_ID = resolve_user_id(USERNAME)
        scan_status["progress"] = 8

        # ── Fetch accounts that follow YOU ───────────────────────
        log("[scan] Step 1/2 — Fetching your followers...")
        followers = fetch_list_via_api(
            f"friendships/{USER_ID}/followers",
            "followers"
        )
        log(f"[followers] ✓ {len(followers)} followers total.")
        scan_status["progress"] = 50

        # ── Fetch accounts YOU follow ────────────────────────────
        log("[scan] Step 2/2 — Fetching your following list...")
        following = fetch_list_via_api(
            f"friendships/{USER_ID}/following",
            "following"
        )
        log(f"[following] ✓ {len(following)} following total.")
        scan_status["progress"] = 90

        # ── Compare sets ─────────────────────────────────────────
        #   following - followers = you follow them, they don't follow back
        not_following_back = following - followers

        log(f"[result] ✓ {len(not_following_back)} accounts don't follow you back.")
        scan_status["progress"] = 100

        scan_status["followers_count"]   = len(followers)
        scan_status["following_count"]   = len(following)
        scan_status["unfollowers_count"] = len(not_following_back)
        scan_status["results"] = [
            f"https://www.instagram.com/{u}/" for u in sorted(not_following_back)
        ]
        scan_status["step"] = "done"

    except Exception as e:
        log(f"[error] {str(e)}")
        scan_status["step"]  = "error"
        scan_status["error"] = str(e)

    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    app.run(port=5000, debug=False)