from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import routers
from .routers import admin, class_change, player, team_permission, tournament

app = FastAPI(title="JDL Constructor API", version="0.1.0")

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(class_change.router, prefix="/api/class-changes", tags=["class_change"])
app.include_router(player.router, prefix="/api/players", tags=["player"])
app.include_router(team_permission.router, prefix="/api/team-permissions", tags=["team_permission"])
app.include_router(tournament.router, prefix="/api/tournaments", tags=["tournament"])

@app.get("/")
async def root():
    return {"message": "JDL Constructor Management System API"}

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Add other application setup if needed, e.g., database connection

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
