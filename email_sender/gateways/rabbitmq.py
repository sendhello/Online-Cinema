import json
import logging
from typing import Callable, Coroutine

from aio_pika import Channel, Exchange, Message, connect_robust
from aio_pika.connection import Connection
from pydantic import BaseModel

from core.settings import settings


logger = logging.getLogger(settings.project_name)


class LiveProbeStatus(BaseModel):
    service_name: str
    status: bool


class RabbitGateway:
    def __init__(self) -> None:
        self._dsn = settings.rabbitmq_dsn
        self.prefetch_count = settings.rabbitmq_prefetch_count
        self.exchange_type = settings.rabbitmq_exchange_type
        self._connection = None
        self._channel = None
        self._exchange = None
        self.connected: bool = False

    def shutdown(self) -> Coroutine:
        return self._close_connection()

    def startup(self) -> Coroutine:
        return self._create_connection()

    async def is_connected(self) -> LiveProbeStatus:
        return LiveProbeStatus(service_name="RabbitMQ", status=self.connected)

    async def _create_connection(self) -> None:
        logger.info("Create connection RabbitMQ")
        try:
            self._connection = await connect_robust(self._dsn)
            self._connection.reconnect_callbacks.add(self._on_connection_restore)
            self._connection.close_callbacks.add(self._on_close_connection)
            self.connected = True
        except ConnectionError as exc:
            err_message = f"Rabbit connection problem: {exc}"
            logger.error(err_message)
            raise ConnectionError(err_message)

    async def _close_connection(self) -> None:
        if self._connection:
            await self._connection.close()

    async def get_connection(self) -> Connection:
        return self._connection

    async def get_channel(self) -> Channel:
        if not self._channel:
            connection = await self.get_connection()
            self._channel = await connection.channel()
            await self._channel.set_qos(prefetch_count=self.prefetch_count)
        return self._channel

    async def get_exchange(self) -> Exchange:
        if not self._exchange:
            channel = await self.get_channel()
            self._exchange = await channel.declare_exchange(self.exchange_type, auto_delete=False, durable=True)
        return self._exchange

    async def create_queue_listener(
        self,
        queue_name: str,
        callback_worker: Callable,
    ) -> None:
        channel = await self.get_channel()
        exchange = await self.get_exchange()
        queue = await channel.declare_queue(queue_name, auto_delete=False, durable=True)
        await queue.bind(exchange)
        await queue.consume(callback_worker)

    async def declare_queue(
        self,
        name: str,
    ) -> None:
        connection = await self.get_connection()
        channel = await connection.channel()
        exchange = await self.get_exchange()
        queue = await channel.declare_queue(name, auto_delete=False, durable=True)
        await queue.bind(exchange, name)

    async def send_data_in_queue(self, data: dict, queue_name: str) -> None:
        data_bytes = json.dumps(data).encode()
        exchange = await self.get_exchange()
        logger.debug(f'Send message in "{queue_name}". Message: {data}')
        message = Message(data_bytes)
        message.delivery_mode = 2
        await exchange.publish(message, routing_key=queue_name)

    def _on_close_connection(self, *args):
        logger.error("Lost connection to RabbitMQ...")
        self.connected = False

    def _on_connection_restore(self, *args):
        logger.info("Connection to RabbitMQ has been restored...")
        self._channel = None
        self._exchange = None
        self.connected = True
