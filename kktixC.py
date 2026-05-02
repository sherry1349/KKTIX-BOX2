from flask import Flask, request
import requests
import os
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# ======================
# 🔔 Discord 設定
# ======================
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# 👉 改成你的 Discord User ID
USER_ID = "sherry_1349"

# 🎟 KKTIX網址
URL = "https://kktix.com/events/ig9ree/registrations/new"

# 🕒 台灣時間
tw = timezone(timedelta(hours=8))


# ======================
# 📢 通知系統
# ======================
def send_normal(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})


def send_urgent(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": f"<@{USER_ID}> {msg}"})


# ======================
# 🎟 Playwright查票（核心）
# ======================
def check_ticket():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )

            page = browser.new_page()

            page.goto(URL, timeout=30000)
            page.wait_for_timeout(5000)  # 等JS跑完

            content = page.content()

            browser.close()

            return ("自行選位" in content or "電腦配位" in content)

    except Exception as e:
        print("錯誤:", e)
        return False


# ======================
# 🌐 Web入口
# ======================
@app.route("/")
def run():
    mode = request.args.get("mode", "check")

    now = datetime.now(tw).strftime("%H:%M:%S")

    # 🟡 每小時狀態回報（不 @）
    if mode == "status":
        send_normal(f"🟡 系統正常運作中（台灣時間 {now}）\n{URL}")
        return "status ok"

    # 🔥 查票
    if check_ticket():
        send_urgent(f"🔥 KKTIX 有票了！（台灣時間 {now}）\n{URL}")
        return "有票"

    return "沒票"


# ======================
# 🚀 啟動
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)