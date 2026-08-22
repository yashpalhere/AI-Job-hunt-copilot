from fastapi import FastAPI
from app.routers import auth,job
app = FastAPI(
    title="AI JOB HUNT COPILOT",
    version="1.0.0"
)

@app.get('/')
def root():
    return {"message":"AI Job Hunt Copilot API is running!"}
app.include_router(auth.router)
app.include_router(job.router)