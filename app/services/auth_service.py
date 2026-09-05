from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.repo.get_by_username(payload.username)
        if user is None or not user.is_active or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Invalid username or password")
        token = create_access_token(subject=user.username, role=user.role)
        return TokenResponse(access_token=token, role=user.role, username=user.username)
