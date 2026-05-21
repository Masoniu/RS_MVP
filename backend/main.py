from fastapi import FastAPI
from routers import auth

app = FastAPI(
    title="RouteSplitter API",
    description="Бекенд MVP",
    version="0.1.0"
)

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"status": "OK", "message": "Backend is running!"}