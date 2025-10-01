import requests
import re
from datetime import datetime

# Zee5 Source
zee_m3u_url = "https://raw.githubusercontent.com/alex8875/m3u/refs/heads/main/z5.m3u"
m3u_file = "t5.m3u"

def get_zee_token():
    try:
        resp = requests.get(zee_m3u_url, timeout=5)
        resp.raise_for_status()
        text = resp.text
        match = re.search(r"\?hdntl=[^\s\"']+", text)
        if match:
            token_part = match.group(0).lstrip("?")
            return token_part
        else:
            print("⚠️ No hdntl token found in Zee m3u source.")
            return None
    except Exception as e:
        print("⚠️ Zee token fetch failed:", e)
        return None

def extract_old_zee_token():
    try:
        with open(m3u_file, "r", encoding="utf-8") as f:
            content = f.read()
        zee_old = re.search(r"hdntl=[^\s\"']+", content)
        return zee_old.group(0) if zee_old else None
    except FileNotFoundError:
        return None

def extract_expiry_time(token):
    if not token:
        return None
    match = re.search(r"(?:exp|~exp)=(\d+)", token)
    if not match:
        return None
    ts = int(match.group(1))
    from datetime import timezone, timedelta, datetime
    dt_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
    ist = dt_utc + timedelta(hours=5, minutes=30)
    return ist.strftime("%Y-%m-%d %H:%M:%S IST")

def update_zee_token(zee_token):
    with open(m3u_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Remove old Zee token
    content = re.sub(r"\?hdntl=[^\s\"]+", "", content)

    # Add new Zee token
    if zee_token:
        content = re.sub(
            r"(https://z5ak-cmaflive\.zee5\.com[^\s\"']+?\.m3u8)",
            rf"\1?{zee_token}",
            content
        )

    with open(m3u_file, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Zee5 playlist updated.")

def main():
    old_zee = extract_old_zee_token()

    zee_token = get_zee_token()
    if not zee_token:
        raise Exception("❌ Could not fetch Zee token")

    update_zee_token(zee_token)
    print(f"🕒 Zee token expires at: {extract_expiry_time(zee_token)}")

if __name__ == "__main__":
    main()
