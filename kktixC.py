from flask import Flask, request
import requests
import os
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ======================
# 🔐 環境變數
# ======================
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID")

KKTIX_EMAIL = os.getenv("KKTIX_EMAIL")
KKTIX_PASSWORD = os.getenv("KKTIX_PASSWORD")

URL = "https://kktix.com/events/ig9ree/registrations/new"

tw = timezone(timedelta(hours=8))


# ======================
# 📢 Discord
# ======================
def send(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def send_mention(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": f"<@{DISCORD_USER_ID}> {msg}"})


# ======================
# 🔐 KKTIX 登入
# ======================
def login(page):
    page.goto("https://kktix.com/users/sign_in", timeout=30000)

    page.wait_for_load_state("domcontentloaded")

    page.fill("input[name='user[email]']", KKTIX_EMAIL)
    page.fill("input[name='user[password]']", KKTIX_PASSWORD)

    page.click("button[type='submit']")

    # 等登入完成
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)


# ======================
# 🧠 Angular 完整等待
# ======================
def wait_angular_ready(page):
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("body")
    page.wait_for_timeout(4000)
    page.evaluate("() => new Promise(r => setTimeout(r, 1000))")


# ======================
# 🎯 判斷票
# ======================
def has_ticket(page):
    wait_angular_ready(page)

    return page.locator("text=自行選位").count() > 0


# ======================
# 🤖 主檢查流程
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
            # 🔐 1. 登入
            # ======================
            login(page)

            # ======================
            # 🎫 2. 進活動頁
            # ======================
            page.goto(URL, timeout=30000)

            # ======================
            # 🧠 3. 等 Angular
            # ======================
            result = has_ticket(page)

            browser.close()

            return result

    except Exception as e:
        print("錯誤:", e)
        return False


# ======================
# 🌐 API
# ======================
@app.route("/")
def run():
    mode = request.args.get("mode", "check")

    now = datetime.now(tw).strftime("%H:%M:%S")

    if mode == "status":
        send(f"🟡 系統正常（台灣時間 {now}）\n{URL}")
        return "ok"

    if check_ticket():
        send_mention(f"🔥 KKTIX 釋票啦 {now}\n{URL}")
        return "有票"

    return "沒票"


# ======================
# 🚀 啟動
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)