from dataclasses import dataclass

from fastapi import Depends, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import UserRole, decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.utils.audit import set_current_actor

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthContext:
    actor: str
    role: str
    auth_type: str
    user: User | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN.value or self.auth_type == "api_key"


def get_current_auth(
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> AuthContext:
    settings = get_settings()

    if x_api_key:
        if x_api_key != settings.API_KEY:
            raise UnauthorizedError("Invalid API key")
        ctx = AuthContext(actor="synchain-ai", role=UserRole.ADMIN.value, auth_type="api_key")
        set_current_actor(ctx.actor)
        return ctx

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Provide a valid X-API-Key header or Bearer token")

    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc

    username = payload.get("sub")
    if not username:
        raise UnauthorizedError("Invalid token payload")

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    ctx = AuthContext(
        actor=user.email or user.username,
        role=user.role,
        auth_type="jwt",
        user=user,
    )
    set_current_actor(ctx.actor)
    return ctx


def require_admin(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
    if not auth.is_admin:
        raise ForbiddenError("Admin role is required for this action")
    return auth
