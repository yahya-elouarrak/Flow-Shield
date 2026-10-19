import uuid
from fastapi import APIRouter, HTTPException, status

from app import database
from app.auth import hash_password, verify_password, create_access_token
from app.models import UserRegister, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED,
             summary="Register a new user account")
def register(body: UserRegister):
    """Register a new customer account and receive an access token."""
    # Check for duplicate email
    for u in database.users.values():
        if u["email"] == body.email:
            raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"user-{uuid.uuid4().hex[:8]}"
    database.users[user_id] = {
        "id": user_id,
        "email": body.email,
        "name": body.name,
        "role": "customer",
        "hashed_password": hash_password(body.password),
        "subscription_status": None,
        "plan": None,
    }

    token = create_access_token(user_id, "customer")
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse,
             summary="Login with email and password")
def login(body: UserLogin):
    """Authenticate and receive a JWT access token."""
    user = None
    for u in database.users.values():
        if u["email"] == body.email:
            user = u
            break

    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user["id"], user["role"])
    return TokenResponse(access_token=token)
