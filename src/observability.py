"""Observability utilities for ACP Harness: logging, metrics, and tracing."""

import functools
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any, Optional

import structlog
from fastapi import Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)
from prometheus_client.registry import CollectorRegistry

# Configure structlog for JSON logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


# Prometheus metrics registry
REGISTRY = CollectorRegistry()

# Request metrics
REQUEST_COUNT = Counter(
    "acp_requests_total",
    "Total ACP requests processed",
    ["method", "endpoint", "status"],
    registry=REGISTRY,
)

REQUEST_LATENCY = Histogram(
    "acp_request_duration_seconds",
    "ACP request latency in seconds",
    ["method", "endpoint"],
    registry=REGISTRY,
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
)

# Session metrics
ACTIVE_SESSIONS = Gauge(
    "acp_active_sessions",
    "Number of active Claude sessions",
    registry=REGISTRY,
)

SESSION_ERRORS = Counter(
    "acp_session_errors_total",
    "Total session errors",
    ["error_type"],
    registry=REGISTRY,
)

SESSION_DURATION = Histogram(
    "acp_session_duration_seconds",
    "Session duration in seconds",
    registry=REGISTRY,
    buckets=[60, 300, 600, 1800, 3600, 7200, 14400, 28800],
)

# Command metrics
COMMANDS_DISPATCHED = Counter(
    "acp_commands_dispatched_total",
    "Total commands dispatched to Claude",
    ["status"],
    registry=REGISTRY,
)

COMMAND_LATENCY = Histogram(
    "acp_command_duration_seconds",
    "Command execution latency",
    registry=REGISTRY,
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0],
)

# Verification metrics
VERIFICATIONS_RUN = Counter(
    "acp_verifications_total",
    "Total verification cycles run",
    ["status"],
    registry=REGISTRY,
)

GAPS_DETECTED = Counter(
    "acp_gaps_detected_total",
    "Total gaps detected by verification",
    ["severity"],
    registry=REGISTRY,
)


def metrics_middleware(
    request: Request, call_next: Callable[[Request], Response]
) -> Response:
    """FastAPI middleware for collecting request metrics."""
    start_time = time.time()
    response = call_next(request)
    duration = time.time() - start_time

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

    return response


def get_metrics() -> tuple[bytes, str]:
    """Generate Prometheus metrics output."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST


@contextmanager
def timed_execution(
    metric: Histogram, labels: Optional[dict[str, str]] = None
) -> Iterator[None]:
    """Context manager for timing operations with Prometheus histograms."""
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        if labels:
            metric.labels(**labels).observe(duration)
        else:
            metric.observe(duration)


def traced(
    operation_name: str,
    attributes: Optional[dict[str, Any]] = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator for tracing function execution (placeholder for OpenTelemetry integration)."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        logger = get_logger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            ctx: dict[str, Any] = {
                "operation": operation_name,
                "function": func.__name__,
            }
            if attributes:
                ctx.update(attributes)

            logger.info("operation_started", **ctx)

            try:
                result = func(*args, **kwargs)
                ctx["duration_ms"] = round((time.time() - start_time) * 1000, 3)
                ctx["status"] = "success"
                logger.info("operation_completed", **ctx)
                return result
            except Exception as e:
                ctx["duration_ms"] = round((time.time() - start_time) * 1000, 3)
                ctx["status"] = "error"
                ctx["error"] = str(e)
                ctx["error_type"] = type(e).__name__
                logger.error("operation_failed", **ctx)
                raise

        return wrapper

    return decorator


class MetricsReporter:
    """Helper class for reporting component-specific metrics."""

    def __init__(self, component: str) -> None:
        self.component = component
        self.logger = get_logger(f"acp.metrics.{component}")

    def gauge(self, name: str, value: float, **labels: str) -> None:
        """Report a gauge metric."""
        self.logger.debug(
            "metric_gauge",
            component=self.component,
            metric=name,
            value=value,
            labels=labels,
        )

    def counter(self, name: str, increment: float = 1.0, **labels: str) -> None:
        """Report a counter metric increment."""
        self.logger.debug(
            "metric_counter",
            component=self.component,
            metric=name,
            increment=increment,
            labels=labels,
        )

    def histogram(self, name: str, value: float, **labels: str) -> None:
        """Report a histogram observation."""
        self.logger.debug(
            "metric_histogram",
            component=self.component,
            metric=name,
            value=value,
            labels=labels,
        )
