from fastapi import FastAPI
from routers import auth, rooms

app = FastAPI(
    title="RouteSplitter API",
    description="Бекенд MVP",
    version="0.1.0"
)

app.include_router(auth.router)
app.include_router(rooms.router)

@app.get("/")
async def root():
    return {"status": "OK", "message": "Backend is running!"}