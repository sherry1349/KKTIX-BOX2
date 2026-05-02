from flask import Flask, request
import requests
import os
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ======================
# 🔐 環境變數（安全做法）
# ======================
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
KKTIX_EMAIL = os.getenv("KKTIX_EMAIL")
KKTIX_PASSWORD = os.getenv("KKTIX_PASSWORD")
USER_ID = os.getenv("DISCORD_USER_ID")

URL = "https://kktix.com/events/ig9ree/registrations/new"

tw = timezone(timedelta(hours=8))


# ======================
# 📢 Discord通知
# ======================
def send_normal(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})


def send_urgent(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": f"<@{USER_ID}> {msg}"})


# ======================
# 🤖 登入 + 查票（核心）
# ======================
def check_ticket():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()

            # ======================
            # 1️⃣ 登入頁
            # ======================
            page.goto("https://kktix.com/users/sign_in", timeout=30000)

            page.fill("input[name='user[email]']", KKTIX_EMAIL)
            page.fill("input[name='user[password]']", KKTIX_PASSWORD)

            page.click("button[type='submit']")
            page.wait_for_timeout(5000)

            # ======================
            # 2️⃣ 進票頁
            # ======================
            page.goto(URL, timeout=30000)
            page.wait_for_timeout(5000)

            content = page.content()

            browser.close()

            # ======================
            # 3️⃣ 判斷有票
            # ======================
            return ("自行選位" in content or "電腦配位" in content)

    except Exception as e:
        print("錯誤:", e)
        return False


# ======================
# 🌐 API入口
# ======================
@app.route("/")
def run():
    mode = request.args.get("mode", "check")

    now = datetime.now(tw).strftime("%H:%M:%S")

    # 🟡 每小時回報（不@）
    if mode == "status":
        send_normal(f"🟡 系統正常運作中（台灣時間 {now}）")
        return "ok"

    # 🔥 查票
    if check_ticket():
        send_urgent(f"🔥 KKTIX 有票了！（台灣時間 {now}）")
        return "有票"

    return "沒票"


# ======================
# 🚀 啟動
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)