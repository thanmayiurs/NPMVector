from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.packages import router as package_router
from app.api.dashboard import router as dashboard_router
from app.api.threats import router as threat_router
from app.database.database import Base, engine
from app.models.package import Package
from app.models.release import Release
from app.services.scheduler import start_scheduler

app = FastAPI(
    title="NPMVector API",
    description="npm Supply Chain Security Monitoring System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(package_router)
app.include_router(dashboard_router)
app.include_router(threat_router)

start_scheduler()


@app.get("/")
def root():
    return {"message": "NPMVector API is running", "status": "active"}


@app.get("/health")
def health():
    return {"status": "healthy"}
