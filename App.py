from fastapi import FastAPI, Query
from playwright.sync_api import sync_playwright
import uvicorn

app = FastAPI()

# ⚠️ À personnaliser avec les cookies TikTok valides
TIKTOK_COOKIES = {
    "sessionid": "TON_SESSIONID_ICI",
    "tt_csrf_token": "TON_CSRF_TOKEN_ICI"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/114.0.0.0 Safari/537.36"
}

@app.get("/verify_booster")
def verify_booster(
    video_id: str = Query(default=None),
    target_username: str = Query(default=None),
    booster_username: str = Query(...)
):
    result = {
        "liked": False,
        "followed": False,
        "verified": False
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=HEADERS["User-Agent"])

        # Ajouter les cookies
        context.add_cookies([
            {"name": k, "value": v, "domain": ".tiktok.com", "path": "/"}
            for k, v in TIKTOK_COOKIES.items()
        ])

        page = context.new_page()

        # Vérifie l'abonnement
        if target_username:
            try:
                page.goto(f"https://www.tiktok.com/@{target_username}/followers")
                page.wait_for_timeout(5000)
                if booster_username.lower() in page.content().lower():
                    result["followed"] = True
            except Exception as e:
                print("Erreur abonnement:", e)

        # Vérifie le like
        if video_id:
            try:
                page.goto(f"https://www.tiktok.com/@{target_username}/video/{video_id}/likes")
                page.wait_for_timeout(5000)
                if booster_username.lower() in page.content().lower():
                    result["liked"] = True
            except Exception as e:
                print("Erreur like:", e)

        browser.close()

    result["verified"] = result["liked"] or result["followed"]
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
