print("### LOADED FROM:", __file__)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    repo_routes,
    query_routes,
    docs_routes,
    test_routes,
)

app = FastAPI(
    title="CodeSense AI",
    version="0.1.0",
)

# CORS Configuration
# Temporary: Allow all origins for deployment testing.
# After deploying the frontend to Vercel, replace "*" with your Vercel URL.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(repo_routes.router, prefix="/api", tags=["Repo"])
app.include_router(query_routes.router, prefix="/api", tags=["Query"])
app.include_router(docs_routes.router, prefix="/api", tags=["Docs"])
app.include_router(test_routes.router, prefix="/api", tags=["Tests"])


@app.get("/")
def read_root():
    return {
        "message": "🚀 CodeSense AI Backend is running successfully!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "CodeSense AI Backend",
        "version": "0.1.0"
    }