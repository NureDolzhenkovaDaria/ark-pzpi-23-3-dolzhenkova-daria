from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routes.api_routes import router
from services.db_service import init_db

app = FastAPI(title="EmoAd Extended API")


init_db()

app.include_router(router)

@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")