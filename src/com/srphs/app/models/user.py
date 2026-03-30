from beanie import Document
from typing import Optional
 
 
class User(Document):
    username: str
    email: str
    password: Optional[str] = None          # Opcional para usuarios de Google
    google_id: Optional[str] = None         # NUEVO: ID único de Google
    auth_provider: str = "local"            # NUEVO: "local" | "google"
    avatar_url: Optional[str] = None        # NUEVO: foto de perfil de Google
 
    class Settings:
        name = "users"
 