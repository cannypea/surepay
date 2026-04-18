from fastapi import FastAPI
from app.database import engine, Base
from app.routes import users

# Create FastAPI app (ONLY ONCE)
app = FastAPI(title="SurePay API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(users.router, prefix="/users")

# Root endpoint
@app.get("/")
def home():
    return {
        "app": "SurePay",
        "status": "running"
    }