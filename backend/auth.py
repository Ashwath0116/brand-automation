"""
BizForge — Authentication Routes
Register, Login, Logout, OAuth, User management
"""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session as DBSession
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import bcrypt
import secrets
import os
import httpx

# Load env vars
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

from .database import get_db, User, Session

router = APIRouter(prefix="/api/auth", tags=["auth"])

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")


# ── Public config (safe to expose client IDs) ──
@router.get("/config")
async def auth_config():
    return {
        "google_client_id": GOOGLE_CLIENT_ID,
        "github_client_id": GITHUB_CLIENT_ID,
    }


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_session(db: DBSession, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    session = Session(token=token, user_id=user_id)
    db.add(session)
    db.commit()
    return token


def get_current_user(request: Request, db: DBSession = Depends(get_db)):
    """Extract user from session cookie. Returns None if not logged in."""
    token = request.cookies.get("session_token")
    if not token:
        return None
    session = db.query(Session).filter(Session.token == token).first()
    if not session:
        return None
    user = db.query(User).filter(User.id == session.user_id).first()
    return user


# ── Register ──
@router.post("/register")
async def register(request: Request, response: Response, db: DBSession = Depends(get_db)):
    body = await request.json()
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not name or not email or not password:
        raise HTTPException(400, "Name, email and password are required")

    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(409, "An account with this email already exists")

    # Create user
    is_admin = (email == ADMIN_EMAIL.lower()) if ADMIN_EMAIL else False
    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        provider="local",
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create session
    token = create_session(db, user.id)
    response.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=86400 * 30)

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "provider": user.provider,
            "is_admin": user.is_admin,
        }
    }


# ── Login ──
@router.post("/login")
async def login(request: Request, response: Response, db: DBSession = Depends(get_db)):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        raise HTTPException(400, "Email and password are required")

    user = db.query(User).filter(User.email == email).first()
    if not user or not user.hashed_password:
        raise HTTPException(401, "Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(401, "Invalid email or password")

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Create session
    token = create_session(db, user.id)
    response.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=86400 * 30)

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "provider": user.provider,
            "is_admin": user.is_admin,
        }
    }


# ── Get current user ──
@router.get("/me")
async def me(request: Request, db: DBSession = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return {"success": False, "user": None}
    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "provider": user.provider,
            "is_admin": user.is_admin,
        }
    }


# ── Logout ──
@router.post("/logout")
async def logout(request: Request, response: Response, db: DBSession = Depends(get_db)):
    token = request.cookies.get("session_token")
    if token:
        db.query(Session).filter(Session.token == token).delete()
        db.commit()
    response.delete_cookie("session_token")
    return {"success": True}


# ── Google Sign-In (client-side GSI button) ──
@router.post("/google/token")
async def google_token_login(request: Request, response: Response, db: DBSession = Depends(get_db)):
    """Verify Google ID token from Sign In With Google button."""
    body = await request.json()
    credential = body.get("credential", "")
    if not credential:
        raise HTTPException(400, "Missing Google credential")

    # Verify token with Google
    async with httpx.AsyncClient() as client:
        verify_resp = await client.get(
            f"https://oauth2.googleapis.com/tokeninfo?id_token={credential}"
        )
        if verify_resp.status_code != 200:
            raise HTTPException(401, "Invalid Google token")
        info = verify_resp.json()

    # Check audience matches our client ID
    if GOOGLE_CLIENT_ID and info.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(401, "Token audience mismatch")

    email = info.get("email", "").lower()
    name = info.get("name", email.split("@")[0])
    avatar = info.get("picture", "")

    if not email:
        raise HTTPException(400, "Could not get email from Google")

    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        is_admin = (email == ADMIN_EMAIL.lower()) if ADMIN_EMAIL else False
        user = User(name=name, email=email, provider="google", avatar_url=avatar, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        user.avatar_url = avatar or user.avatar_url
        db.commit()

    token = create_session(db, user.id)
    response.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=86400 * 30)

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "provider": user.provider,
            "is_admin": user.is_admin,
        }
    }


# ── Google OAuth (redirect flow, kept as fallback) ──
@router.get("/google/login")
async def google_login():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(501, "Google OAuth not configured. Add GOOGLE_CLIENT_ID to .env")
    redirect_uri = "http://localhost:8001/api/auth/google/callback"
    url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid email profile"
    )
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@router.get("/google/callback")
async def google_callback(code: str, response: Response, db: DBSession = Depends(get_db)):
    redirect_uri = "http://localhost:8001/api/auth/google/callback"
    # Exchange code for token
    async with httpx.AsyncClient() as client:
        token_resp = await client.post("https://oauth2.googleapis.com/token", data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        })
        tokens = token_resp.json()
        # Get user info
        user_resp = await client.get("https://www.googleapis.com/oauth2/v2/userinfo",
                                     headers={"Authorization": f"Bearer {tokens['access_token']}"})
        info = user_resp.json()

    email = info.get("email", "").lower()
    name = info.get("name", email.split("@")[0])
    avatar = info.get("picture", "")

    # Find or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        is_admin = (email == ADMIN_EMAIL.lower()) if ADMIN_EMAIL else False
        user = User(name=name, email=email, provider="google", avatar_url=avatar, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        user.avatar_url = avatar or user.avatar_url
        db.commit()

    token = create_session(db, user.id)
    from fastapi.responses import RedirectResponse
    resp = RedirectResponse("/")
    resp.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=86400 * 30)
    return resp


# ── GitHub OAuth ──
@router.get("/github/login")
async def github_login():
    if not GITHUB_CLIENT_ID:
        raise HTTPException(501, "GitHub OAuth not configured. Add GITHUB_CLIENT_ID to .env")
    redirect_uri = "http://localhost:8001/api/auth/github/callback"
    url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=user:email"
    )
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url)


@router.get("/github/callback")
async def github_callback(code: str, response: Response, db: DBSession = Depends(get_db)):
    redirect_uri = "http://localhost:8001/api/auth/github/callback"
    async with httpx.AsyncClient() as client:
        token_resp = await client.post("https://github.com/login/oauth/access_token", data={
            "code": code,
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
        }, headers={"Accept": "application/json"})
        tokens = token_resp.json()

        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        user_resp = await client.get("https://api.github.com/user", headers=headers)
        info = user_resp.json()

        # Get email (may need separate call)
        email = info.get("email")
        if not email:
            emails_resp = await client.get("https://api.github.com/user/emails", headers=headers)
            emails = emails_resp.json()
            for e in emails:
                if e.get("primary"):
                    email = e["email"]
                    break

    email = (email or "").lower()
    name = info.get("name") or info.get("login", "User")
    avatar = info.get("avatar_url", "")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        is_admin = (email == ADMIN_EMAIL.lower()) if ADMIN_EMAIL else False
        user = User(name=name, email=email, provider="github", avatar_url=avatar, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        user.avatar_url = avatar or user.avatar_url
        db.commit()

    token = create_session(db, user.id)
    from fastapi.responses import RedirectResponse
    resp = RedirectResponse("/")
    resp.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=86400 * 30)
    return resp


# ── Admin: List all users ──
@router.get("/admin/users")
async def admin_users(request: Request, db: DBSession = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin access required")

    users = db.query(User).order_by(User.created_at.desc()).all()
    return {
        "success": True,
        "users": [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "avatar_url": u.avatar_url,
                "provider": u.provider,
                "is_admin": u.is_admin,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in users
        ],
        "total": len(users),
    }


# ── Admin: Delete user ──
@router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: int, request: Request, db: DBSession = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or not user.is_admin:
        raise HTTPException(403, "Admin access required")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(404, "User not found")

    if target.id == user.id:
        raise HTTPException(400, "Cannot delete yourself")

    # Delete sessions
    db.query(Session).filter(Session.user_id == user_id).delete()
    db.delete(target)
    db.commit()
    return {"success": True}
