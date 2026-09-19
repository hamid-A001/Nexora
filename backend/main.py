from fastapi import FastAPI

from backend.api.users import router as users_router


app = FastAPI(title="Nexora API")


app.include_router(users_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Nexora",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }