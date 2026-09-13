from fastapi import FastAPI
from app.routers import auth,job,resume,agent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI JOB HUNT COPILOT",
    version="1.0.0"
)

@app.get('/')
def root():
    return {"message":"AI Job Hunt Copilot API is running!"}
app.include_router(auth.router)
app.include_router(job.router)
app.include_router(resume.router)
app.include_router(agent.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)