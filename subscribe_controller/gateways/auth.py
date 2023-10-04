import logging
from uuid import UUID

from core.settings import settings
from gateways.base import BaseAsyncGateway


logger = logging.getLogger(settings.project_name)


class AuthGateway(BaseAsyncGateway):
    async def login(self) -> tuple[str, str]:
        logger.debug("Try login...")
        response = await self._client.post(
            "/api/v1/auth/login", json={"email": settings.admin_email, "password": settings.admin_password}
        )
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")
        return access_token, refresh_token

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        logger.debug("Try refresh...")
        response = await self._client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        response.raise_for_status()
        response_data = response.json()
        access_token = response_data.get("access_token")
        refresh_token = response_data.get("refresh_token")
        return access_token, refresh_token

    async def set_user_role(self, user_id: UUID, access_token: str) -> None:
        """Установка пользователю роли подписчика."""

        logger.debug("Try set user role...")
        response = await self._client.post(
            f"/api/v1/users/{user_id}/set_role",
            params={"role_id": settings.subscribe_role_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"User role set with code {response.status_code}")
        response.raise_for_status()

    async def remove_user_role(self, user_id: UUID, access_token: str) -> None:
        """Установка пользователю роли подписчика."""

        logger.debug("Try remove user role...")
        response = await self._client.post(
            f"/api/v1/users/{user_id}/remove_role",
            params={"role_id": settings.subscribe_role_id},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"User role removed with code {response.status_code}")
        response.raise_for_status()


auth_gateway = AuthGateway(
    base_url=settings.auth_gateway,
)
