import logging
from datetime import datetime
from uuid import UUID

from constants import PaymentStatus, SubscribeStatus
from core.settings import settings
from gateways.base import BaseAsyncGateway
from schemas.payment import PaymentScheme
from schemas.subscribe import SubscribeScheme


logger = logging.getLogger(settings.project_name)


class SubscribeServiceGateway(BaseAsyncGateway):
    async def get_pending_payments(self, access_token: str) -> list[PaymentScheme]:
        """Получение платежей в ожидании оплаты."""

        logger.debug("Try get pending payments...")
        response = await self._client.get(
            "/api/v1/payments/",
            params={"status": PaymentStatus.PENDING.value, "page_size": 500},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"Pending payments got with status {response.status_code}...")
        response.raise_for_status()
        logger.debug(f"Pending payments: {response.json()}")
        return [PaymentScheme.parse_obj(item) for item in response.json()]

    async def get_subscribe_payments(self, subscribe_id: UUID, access_token: str) -> list[PaymentScheme]:
        """Получение платежей в ожидании оплаты."""

        logger.debug("Try get subscribe payments...")
        response = await self._client.get(
            "/api/v1/payments/",
            params={"subscribe_id": str(subscribe_id), "page_size": 500},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"Subscribe payments got with status {response.status_code}...")
        response.raise_for_status()
        logger.debug(f"Subscribe payments: {response.json()}")
        return [PaymentScheme.parse_obj(item) for item in response.json()]

    async def update_payment(self, payment_id: UUID, access_token: str) -> PaymentScheme:
        """Обновление статуса платежа."""

        logger.debug("Try update payment...")
        response = await self._client.post(
            f"/api/v1/payments/{payment_id}/update",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"Payment updated with code {response.status_code}")
        response.raise_for_status()

        payment = PaymentScheme.parse_obj(response.json())
        logger.debug(f"Payment updated: {payment}")
        return payment

    async def get_pending_subscribes(self, access_token: str) -> list[SubscribeScheme]:
        """Получение подписок в ожидании."""

        logger.debug("Try get pending subscribes...")
        response = await self._client.get(
            "/api/v1/subscribe/",
            params={"status": SubscribeStatus.PENDING.value, "page_size": 500},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"Pending subscribes got with code {response.status_code}")
        response.raise_for_status()
        logger.debug(f"Pending subscribes: {response.json()}")
        return [SubscribeScheme.parse_obj(item) for item in response.json()]

    async def get_expired_subscribes(self, access_token: str) -> list[SubscribeScheme]:
        """Получение истекших подписок."""

        logger.debug("Try get expired subscribes...")
        response = await self._client.get(
            "/api/v1/subscribe/",
            params={"status": SubscribeStatus.ACTIVE.value, "end_date": datetime.utcnow().date(), "page_size": 500},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"Expired subscribes got with code {response.status_code}")
        response.raise_for_status()
        logger.debug(f"Expired subscribes: {response.json()}")
        return [SubscribeScheme.parse_obj(item) for item in response.json()]

    async def update_subscribe(
        self, subscribe_id: UUID, subscribe_status: SubscribeStatus, access_token: str
    ) -> list[PaymentScheme]:
        """Обновление статусов подписок."""

        logger.debug("Try update subscribe...")
        response = await self._client.patch(
            f"/api/v1/subscribe/{subscribe_id}",
            json={"status": subscribe_status},
            headers={"Authorization": f"Bearer {access_token}"},
        )
        logger.debug(f"Subscribe updated with code {response.status_code}")
        response.raise_for_status()
        logger.debug(f"Subscribe updated: {response.json()}")


subscribe_service_gateway = SubscribeServiceGateway(
    base_url=settings.subscribe_service_gateway,
)
