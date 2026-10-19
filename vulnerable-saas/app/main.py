from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app import database
from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.subscription_routes import router as subscription_router
from app.routes.payment_routes import router as payment_router
from app.routes.invoice_routes import router as invoice_router
from app.routes.coupon_routes import router as coupon_router
from app.routes.refund_routes import router as refund_router
from app.routes.premium_routes import router as premium_router
from app.routes.admin_routes import router as admin_router
from app.routes.openapi_docs_routes import router as docs_router
from app.routes.sspp_routes import router as sspp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed data
    print(f"[MiniSub] Starting in {'VULNERABLE' if settings.VULNERABLE_MODE else 'SECURE'} mode")
    database.seed()
    yield
    # Shutdown
    print("[MiniSub] Shutting down.")


app = FastAPI(
    title="MiniSub SaaS API",
    version="1.0.0",
    description=(
        "Intentionally vulnerable subscription/payment SaaS API for FlowShield testing.\n\n"
        f"**Mode: {'🔓 VULNERABLE' if settings.VULNERABLE_MODE else '🔒 SECURE'}**"
    ),
    lifespan=lifespan,
)

# CORS — allow FlowShield dashboard and backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(subscription_router)
app.include_router(payment_router)
app.include_router(invoice_router)
app.include_router(coupon_router)
app.include_router(refund_router)
app.include_router(premium_router)
app.include_router(admin_router)
app.include_router(docs_router)
app.include_router(sspp_router)


@app.get("/", tags=["system"])
def read_root():
    return {
        "service": "MiniSub SaaS API",
        "version": "1.0.0",
        "mode": "vulnerable" if settings.VULNERABLE_MODE else "secure",
    }


@app.get("/health", tags=["system"])
def health_check():
    return {
        "status": "ok",
        "service": "vulnerable-saas",
        "mode": "vulnerable" if settings.VULNERABLE_MODE else "secure",
        "users_loaded": len(database.users),
    }
