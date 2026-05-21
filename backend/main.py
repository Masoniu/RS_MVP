from fastapi import FastAPI

app = FastAPI(
    title="RouteSplitter API",
    description="Бекенд MVP",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {"status": "OK", "message": "Backend is running!"}