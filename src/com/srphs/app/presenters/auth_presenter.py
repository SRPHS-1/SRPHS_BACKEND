from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..models.user import User
from ..services.auth_service import AuthService
from ..services.google_auth_service import GoogleAuthService

router = APIRouter()
auth_service   = AuthService()
google_service = GoogleAuthService()

class GoogleAuthRequest(BaseModel):
    credential: str

@router.post("/register")
async def register(user_data: User):
    existing = await User.find_one(User.email == user_data.email)
    if existing:
        return {"status": "error", "message": "El correo ya está registrado"}
    user_data.password = auth_service.hash_password(user_data.password)
    user_data.auth_provider = "local"
    await user_data.insert()
    return {"status": "success", "message": "Usuario registrado exitosamente"}

@router.post("/login")
async def login(email: str, password: str):
    user = await User.find_one(User.email == email)
    if not user:
        return {"status": "error", "message": "Credenciales inválidas"}
    if user.auth_provider == "google":
        return {"status": "error", "message": "Esta cuenta usa Google. Inicia sesión con Google."}
    if not auth_service.verify_password(password, user.password):
        return {"status": "error", "message": "Credenciales inválidas"}
    return {"status": "success", "message": "Login exitoso", "user": user.username, "avatar": user.avatar_url or ""}

@router.post("/auth/google/register")
async def google_register(body: GoogleAuthRequest):
    try:
        info = google_service.verify_token(body.credential)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")
    existing = await User.find_one(User.email == info["email"])
    if existing:
        return {"status": "error", "message": "Ya tienes una cuenta. Inicia sesión."}
    new_user = User(
        username=info["name"] or info["email"].split("@")[0],
        email=info["email"],
        google_id=info["google_id"],
        auth_provider="google",
        avatar_url=info["avatar_url"],
    )
    await new_user.insert()
    return {"status": "success", "message": "Cuenta creada con Google", "user": new_user.username, "avatar": new_user.avatar_url or ""}

@router.post("/auth/google/login")
async def google_login(body: GoogleAuthRequest):
    try:
        info = google_service.verify_token(body.credential)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {e}")
    user = await User.find_one(User.email == info["email"])
    if not user:
        return {"status": "error", "message": "No tienes cuenta. Regístrate primero con Google."}
    if user.auth_provider == "local":
        return {"status": "error", "message": "Esta cuenta usa contraseña. Inicia sesión con tu correo."}
    if user.avatar_url != info["avatar_url"]:
        user.avatar_url = info["avatar_url"]
        await user.save()
    return {"status": "success", "message": "Login exitoso con Google", "user": user.username, "avatar": user.avatar_url or ""}