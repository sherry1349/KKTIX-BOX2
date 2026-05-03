from flask import Flask, request
import requests
import os
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

# 🔔 Discord Webhook
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

# 👉 你的 Discord ID
USER_ID = "你的DiscordID"

# 🎟 KKTIX API
API_URL = "https://kktix.com/g/events/akiba1/register_info"

# 🕒 台灣時間
tw = timezone(timedelta(hours=8))

# 🧠 狀態記憶（關鍵）
last_status = None


# ======================
# 📢 通知系統
# ======================
def send_normal(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})


def send_urgent(msg):
    requests.post(DISCORD_WEBHOOK, json={
        "content": f"<@{USER_ID}> {msg}"
    })


# ======================
# 🎟 查票
# ======================
def check_ticket():
    try:
        res = requests.get(API_URL, timeout=10)
        data = res.json()
        return data.get("register_status", "")
    except Exception as e:
        print("錯誤:", e)
        return "ERROR"


# ======================
# 🌐 API入口
# ======================
@app.route("/")
def run():
    return "OK"

    mode = request.args.get("mode", "check")
    now = datetime.now(tw).strftime("%H:%M:%S")

    # 🟡 每小時回報（不 @）
    if mode == "status":
        send_normal(f"🟡 系統正常運作中（台灣時間 {now}）")
        return "status ok"

    # 🎟 查票
    status = check_ticket()

    print(f"目前狀態: {status} / 上次狀態: {last_status}")

    # ======================
    # 🔥 有票（第一次出現）
    # ======================
    if status == "IN_STOCK" and last_status != "IN_STOCK":
        send_urgent(f"🔥 KKTIX 有票了！（台灣時間 {now}）")

    # ======================
    # ❌ 票沒了（從有票變沒票）
    # ======================
    if last_status == "IN_STOCK" and status in ["SOLD_OUT", "OUT_OF_STOCK"]:
        send_urgent(f"❌ 票已售完或暫無票（台灣時間 {now}）")

    # 更新狀態
    last_status = status

    return status


# ======================
# 🚀 啟動
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)