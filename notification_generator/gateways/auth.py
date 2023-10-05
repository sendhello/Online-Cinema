import logging
from uuid import UUID

from core.settings import settings
from gateways.base import BaseAsyncGateway
from schemas.user import User


logger = logging.getLogger(settings.project_name)


class AuthGateway(BaseAsyncGateway):
    async def login(self) -> str:
        response = await self._client.post(
            "/api/v1/auth/login", json={"email": settings.admin_email, "password": settings.admin_password}
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
        return access_token

    async def get_user_data(self, user_id: UUID, access_token: str) -> User:
        response = await self._client.get(
            f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return User.parse_obj(response.json())


auth_gateway = AuthGateway(
    base_url=settings.auth_gateway,
)
