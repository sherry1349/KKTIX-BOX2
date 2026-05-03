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
# 📢 通知
# ======================
def send_normal(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={"content": msg}, timeout=5)
    except:
        pass


def send_urgent(msg):
    try:
        requests.post(DISCORD_WEBHOOK, json={
            "content": f"<@{USER_ID}> {msg}"
        }, timeout=5)
    except:
        pass


# ======================
# 🎟 查票（安全版）
# ======================
def check_ticket():
    try:
        res = requests.get(API_URL, timeout=5)

        if res.status_code != 200:
            print("API status:", res.status_code)
            return "ERROR"

        try:
            data = res.json()
        except:
            print("JSON 解析失敗")
            return "ERROR"

        return data.get("register_status", "UNKNOWN")

    except Exception as e:
        print("API錯誤:", e)
        return "ERROR"


# ======================
# 🌐 API入口
# ======================
@app.route("/")
def run():
    global last_status

    try:
        mode = request.args.get("mode", "check")
        now = datetime.now(tw).strftime("%H:%M:%S")

        # 🟡 每小時回報
        if mode == "status":
            send_normal(f"🟡 系統正常運作中（台灣時間 {now}）")
            return "status ok"

        status = check_ticket()

        print(f"目前狀態: {status} / 上次狀態: {last_status}")

        # 🔥 有票
        if status == "IN_STOCK" and last_status != "IN_STOCK":
            send_urgent(f"🔥 KKTIX 有票了！（台灣時間 {now}）")

        # ❌ 票沒了
        if last_status == "IN_STOCK" and status in ["SOLD_OUT", "OUT_OF_STOCK"]:
            send_urgent(f"❌ 票已售完或暫無票（台灣時間 {now}）")

        last_status = status

        return status if status else "unknown"

    except Exception as e:
        print("主程式錯誤:", e)
        return "服務正常，但發生例外"


# ======================
# 🚀 啟動
# ======================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)