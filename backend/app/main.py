from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_projects import router as projects_router
from app.api.routes_openapi import router as openapi_router
from app.api.routes_auth import router as auth_router
from app.api.routes_scans import router as scans_router
from app.api.routes_findings import router as findings_router
from app.api.routes_reports import router as reports_router
from app.api.wordlists import router as wordlists_router
from app.api.routes_dashboard import router as dashboard_router

app = FastAPI(
    title="FlowShield Backend",
    version="0.1.0",
    description="Backend API for the FlowShield testing platform"
)

# CORS configuration
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)
app.include_router(openapi_router)
app.include_router(auth_router)
app.include_router(scans_router)
app.include_router(findings_router)
app.include_router(reports_router)
app.include_router(wordlists_router)
app.include_router(dashboard_router)

@app.get("/")
def read_root():
    return {"message": "FlowShield Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "backend"}
