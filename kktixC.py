import requests
import os

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

URL = "https://kktix.com/events/akiba1/registrations/new"

def send_discord(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def check_ticket():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(URL, headers=headers)
    text = res.text

    return ("自行選位" in text or "電腦配位" in text)

def main():
    if check_ticket():
        send_discord("🔥 KKTIX 有票了！")
    else:
        print("還沒票")

if __name__ == "__main__":
    main()