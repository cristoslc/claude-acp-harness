import logging
import sys

import uvicorn

from config import HarnessConfig, load_config
from rest_api import create_app


def main():
    config = load_config()
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )
    logger = logging.getLogger("acp-harness")
    logger.info(
        "Starting ACP Harness — auth: %s, provider: %s",
        config.preference_auth.value,
        config.preference_provider.value,
    )
    if config.preference_auth.value != "subscription_oauth":
        logger.warning(
            "Using %s auth — per-token billing may apply", config.preference_auth.value
        )
    app = create_app(config)
    uvicorn.run(
        app,
        host=config.api_host,
        port=config.api_port,
        log_level=config.log_level.lower(),
    )
