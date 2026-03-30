import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


class GoogleAuthService:
    @staticmethod
    def verify_token(credential: str) -> dict:
        """
        Verifica el token JWT enviado por el frontend (Google One Tap / OAuth).
        Retorna el payload con los datos del usuario si es válido.
        Lanza ValueError si el token es inválido.
        """
        if not GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID no configurado en .env")

        payload = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            GOOGLE_CLIENT_ID,
        )
        return {
            "google_id":  payload["sub"],           
            "email":      payload["email"],
            "name":       payload.get("name", ""),
            "avatar_url": payload.get("picture", ""),
            "verified":   payload.get("email_verified", False),
        }