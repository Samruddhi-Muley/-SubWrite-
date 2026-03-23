from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
from app.routes import auth, articles, pages

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SubWrite",
    description="A blogging platform built with FastAPI and HTMX",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(pages.router)      # Pages (HTML)
app.include_router(auth.router)       # API Auth
app.include_router(articles.router)   # API Articles