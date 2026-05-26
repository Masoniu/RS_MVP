from fastapi import FastAPI
from routers import auth, rooms, maps, expenses
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RouteSplitter API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(maps.router)
app.include_router(expenses.router)

@app.get("/")
async def root():
    return {"status": "OK", "message": "Backend is running!"}