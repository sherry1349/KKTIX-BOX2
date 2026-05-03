from flask import Flask, request
import requests
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
USER_ID = "你的DiscordID"

API_URL = "https://kktix.com/g/events/akiba1/register_info"

tw = timezone(timedelta(hours=8))

last_status = None


# ======================
# 📢 通知（不會卡）
# ======================
def send_normal(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=3)
    except:
        print("Discord normal 發送失敗")


def send_urgent(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={
            "content": f"<@{USER_ID}> {msg}"
        }, timeout=3)
    except:
        print("Discord urgent 發送失敗")


# ======================
# 🎟 查票（不會卡）
# ======================
def check_ticket():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://kktix.com/events/akiba1/registrations/new"
        }

        res = requests.get(API_URL, headers=headers, timeout=3)

        print("status code:", res.status_code)
        print("response text:", res.text[:200])  # debug 前200字

        if res.status_code != 200:
            return "ERROR"

        try:
            data = res.json()
        except:
            return "ERROR"

        return data.get("register_status", "UNKNOWN")

    except Exception as e:
        print("API錯誤:", e)
        return "ERROR"


# ======================
# 🌐 API入口（保證回應）
# ======================
@app.route("/")
def run():
    global last_status

    try:
        mode = request.args.get("mode", "check")
        now = datetime.now(tw).strftime("%H:%M:%S")

        if mode == "status":
            send_normal(f"🟡 系統正常運作中（台灣時間 {now}）")
            return "status ok"

        status = check_ticket()

        print(f"狀態: {status} / 上次: {last_status}")

        if status == "IN_STOCK" and last_status != "IN_STOCK":
            send_urgent(f"🔥 有票！（{now}）")

        if last_status == "IN_STOCK" and status in ["SOLD_OUT", "OUT_OF_STOCK"]:
            send_urgent(f"❌ 票沒了！（{now}）")

        last_status = status

        return f"OK - {status}"

    except Exception as e:
        print("主程式錯誤:", e)
        return "OK（發生例外但已處理）"


# ======================
# 🚀 啟動
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)