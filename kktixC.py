from flask import Flask, request
import requests
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# 🔔 Discord Webhook（:contentReference[oaicite:1]{index=1}）
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# 👉 換成你的 Discord User ID
USER_ID = "sherry_1349"

# 🎟 KKTIX頁面
URL = "https://kktix.com/events/akiba1/registrations/new"

# 🕒 台灣時間
tw = timezone(timedelta(hours=8))


# ======================
# 📢 通知系統
# ======================
def send_normal(msg):
    requests.post(DISCORD_WEBHOOK, json={
        "content": msg
    })


def send_urgent(msg):
    requests.post(DISCORD_WEBHOOK, json={
        "content": f"<@{USER_ID}> {msg}"
    })


# ======================
# 🎟 查票邏輯
# ======================
def check_ticket():
    try:
        res = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        html = res.text
        return ("自行選位" in html or "電腦配位" in html)
    except:
        return False


# ======================
# 🌐 API入口
# ======================
@app.route("/")
def run():
    mode = request.args.get("mode", "check")

    now = datetime.now(tw).strftime("%H:%M:%S")

    # 🟡 每小時回報（不 @）
    if mode == "status":
        send_normal(f"🟡 系統正常運作中（台灣時間 {now}）")
        return "status ok"

    # 🔥 查票模式
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