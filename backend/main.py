"""
File: main.py

Entry point for the RouteSplitter FastAPI application.

Responsibilities:
- Creating the FastAPI application instance
- Configuring CORS middleware (all origins allowed during development)
- Registering all routers: auth, rooms, maps, expenses
- Basic logging configuration
- Health-check endpoint GET /
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, rooms, maps, expenses
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="RouteSplitter API")

# CORS: in production replace allow_origins=["*"] with a list of allowed domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)      # /auth/*
app.include_router(rooms.router)     # /rooms/*
app.include_router(maps.router)      # /rooms/{id}/route-candidates, /rooms/{id}/save-route
app.include_router(expenses.router)  # /expenses/*

@app.get("/")
async def root():
    """
    Health-check endpoint.

    Returns:
        dict: {"status": "OK", "message": "Backend is running!"}
    """
    return {"status": "OK", "message": "Backend is running!"}