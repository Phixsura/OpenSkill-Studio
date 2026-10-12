import logging

import structlog


def setup_logging(level: str = "DEBUG", fmt: str = "console") -> None:
    """
    Configure structlog.
    Dev: colored console output.
    Prod: JSON (ingestible by Datadog / Loki / ELK).
    """
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if fmt == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        # R353 (log-amplification guard): with rich installed, the default
        # console exception formatter prints LOCALS for every frame — one
        # unhandled exception in a request handler expanded the FastAPI
        # route table into ~550k lines (~100MB) of log. A hostile request
        # that triggers any 500 becomes a disk-filling primitive. Plain,
        # bounded tracebacks carry the same diagnostic value here.
        processors.append(
            structlog.dev.ConsoleRenderer(exception_formatter=structlog.dev.plain_traceback)
        )

    log_level = getattr(logging, level.upper(), logging.INFO)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
