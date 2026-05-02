from playwright.sync_api import sync_playwright
import requests
import os

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def send_discord(msg):
    requests.post(DISCORD_WEBHOOK, json={"content": msg})

def check_ticket():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://kktix.com/events/akiba1/registrations/new")
        page.wait_for_timeout(5000)

        content = page.content()
        browser.close()

        return ("自行選位" in content or "電腦配位" in content)

def main():
    if check_ticket():
        send_discord("🔥 KKTIX 釋票了！快搶！")
    else:
        print("還沒票")

if __name__ == "__main__":
    main()