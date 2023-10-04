import logging

from constants import PaymentStatus, SubscribeStatus
from gateways.auth import AuthGateway
from gateways.notification_api import NotificationApiGateway
from gateways.subscribe_service import SubscribeServiceGateway
from templates.message import PAYMENT_CANCELED, PAYMENT_SUCCESS, SUBSCRIBE_CANCELED, SUBSCRIBE_IS_ACTIV


logger = logging.getLogger(__name__)


class SubscribeService:
    def __init__(
        self,
        auth_gateway: AuthGateway,
        subscribe_service_gateway: SubscribeServiceGateway,
        notification_api_gateway: NotificationApiGateway,
    ):
        self.auth_gateway = auth_gateway
        self.subscribe_service_gateway = subscribe_service_gateway
        self.notification_api_gateway = notification_api_gateway
        self._access_token = None
        self._refresh_token = None

    @property
    async def access_token(self) -> str:
        if self._access_token is None:
            self._access_token, self._refresh_token = await self.auth_gateway.login()

        return self._access_token

    async def update_token(self):
        self._access_token, self._refresh_token = await self.auth_gateway.refresh(refresh_token=self._refresh_token)

    async def update_pending_payments(self, update_token: bool = False) -> None:
        """Обновление статуса у платежей в статусе pending."""

        if update_token:
            await self.update_token()

        pending_payments = await self.subscribe_service_gateway.get_pending_payments(
            access_token=await self.access_token
        )

        for payment in pending_payments:
            payment = await self.subscribe_service_gateway.update_payment(
                payment_id=payment.id,
                access_token=await self.access_token,
            )
            if payment.status == PaymentStatus.SUCCEEDED:
                await self.notification_api_gateway.send_email(
                    user_id=payment.user_id, message=PAYMENT_SUCCESS.format(amount=payment.amount)
                )
            elif payment.status == PaymentStatus.CANCELED:
                await self.notification_api_gateway.send_email(
                    user_id=payment.user_id, message=PAYMENT_CANCELED.format(amount=payment.amount)
                )

    async def update_pending_subscribes(self, update_token: bool = False) -> None:
        """Обновление статусов подписок в ожидании."""

        if update_token:
            await self.update_token()

        pending_subscribes = await self.subscribe_service_gateway.get_pending_subscribes(
            access_token=await self.access_token
        )

        for subscribe in pending_subscribes:
            subscribe_payments = await self.subscribe_service_gateway.get_subscribe_payments(
                subscribe_id=subscribe.id, access_token=await self.access_token
            )
            if any(payment.status == PaymentStatus.SUCCEEDED for payment in subscribe_payments):
                await self.subscribe_service_gateway.update_subscribe(
                    subscribe_id=subscribe.id,
                    subscribe_status=SubscribeStatus.ACTIVE,
                    access_token=await self.access_token,
                )
                await self.auth_gateway.set_user_role(user_id=subscribe.user_id, access_token=await self.access_token)
                await self.notification_api_gateway.send_email(
                    user_id=subscribe.user_id,
                    message=SUBSCRIBE_IS_ACTIV.format(
                        start_date=subscribe.start_date.date().isoformat(),
                        end_date=subscribe.end_date.date().isoformat(),
                    ),
                )

    async def update_expired_subscribes(self, update_token: bool = False) -> None:
        """Обновление статусов истекших подписок."""

        if update_token:
            await self.update_token()

        expired_subscribes = await self.subscribe_service_gateway.get_expired_subscribes(
            access_token=await self.access_token
        )

        for subscribe in expired_subscribes:
            await self.subscribe_service_gateway.update_subscribe(
                subscribe_id=subscribe.id,
                subscribe_status=SubscribeStatus.CANCELED,
                access_token=await self.access_token,
            )
            await self.auth_gateway.remove_user_role(user_id=subscribe.user_id, access_token=await self.access_token)
            await self.notification_api_gateway.send_email(user_id=subscribe.user_id, message=SUBSCRIBE_CANCELED)
