import logging
from typing import NoReturn, Sequence

from sentry_sdk import init
from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

from core.settings import Settings


def connect_sentry(settings: Settings, integrations: Sequence[Integration] = None) -> NoReturn:
    integrations = (integrations or []) + [AsyncioIntegration(), HttpxIntegration()]

    logging.getLogger("sentry_sdk.errors").setLevel(logging.ERROR)
    init(
        environment=settings.environment,
        dsn=settings.sentry.sentry_dsn,
        server_name=settings.project_name,
        debug=settings.debug,
        include_local_variables=settings.sentry.with_locals,
        shutdown_timeout=settings.sentry.shutdown_timeout,
        integrations=integrations,
        # traces_sample_rate=0.2,
        # release="0.1.0",
    )
