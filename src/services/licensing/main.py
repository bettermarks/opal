import time
import structlog

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
from fastapi import FastAPI, Request, Response, status
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from uvicorn.protocols.utils import get_path_with_query_string

from services.licensing import settings
from services.licensing.exceptions import HTTPException
from services.licensing import __version__ as version
from services.licensing.logging import setup_logging, LogLevel
from services.licensing.api.v1.api import api_router


setup_logging(settings.log_format, settings.log_level)
access_logger = structlog.stdlib.get_logger("api.access")
error_logger = structlog.stdlib.get_logger("api.error")
exception_logger = structlog.stdlib.get_logger("api.exception")


app = FastAPI(
    title="Open Adaptive Licensing",
    version=version,
    openapi_url="/v1/openapi.json",
    debug=True if settings.log_level == LogLevel.DEBUG else False,
    description="An Open Adaptive Licensing service",
)

add_pagination(app)  # important! add pagination

# todo: SPECIFICS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origin_regex=r"https://apps.*\.your-domain\.(loc|com)",
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """General HTTPException (FastApiHTTPException) handler."""
    error_logger.info(
        "API failure",
        detail=exc.message,
        url=str(request.url),
        path=get_path_with_query_string(request.scope),
        status_code=exc.status_code,
        method=request.method,
        request_id=correlation_id.get(),
        **exc.kwargs,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": f"{exc.message}{': ' + str(exc.kwargs) if exc.kwargs else ''}"
        },
    )


@app.exception_handler(RequestValidationError)
async def starlette_http_exception_handler(request, exc):
    """Error handler for schema validation failures."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = None
    for err in exc.errors():
        detail = f"{'.'.join(err.get('loc'))}: {err.get('msg')}"
        break
    error_logger.info(
        "API failure",
        detail=detail,
        url=str(request.url),
        path=get_path_with_query_string(request.scope),
        status_code=status_code,
        method=request.method,
        request_id=correlation_id.get(),
    )
    return JSONResponse(
        status_code=status_code,
        content={"detail": f"{detail}"},
    )


@app.exception_handler(Exception)
async def exception_handler(request, exc):
    exception_logger.exception(
        "Uncaught exception",
        exception=str(exc),
        url=str(request.url),
        path=get_path_with_query_string(request.scope),
        method=request.method,
        request_id=correlation_id.get(),
    )
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    start_time = time.perf_counter_ns()

    structlog.contextvars.bind_contextvars(cf_ray_id=request.headers.get("Cf-Ray"))
    response = await call_next(request)
    process_time = time.perf_counter_ns() - start_time
    status_code = response.status_code
    # Ignore status calls and requests with bad status
    if not request.app.url_path_for("get_status") in request.url.path:
        if status_code < status.HTTP_400_BAD_REQUEST:
            access_logger.info(
                "API success",
                url=str(request.url),
                path=get_path_with_query_string(request.scope),
                status_code=status_code,
                method=request.method,
                request_id=correlation_id.get(),
                duration=process_time / 10**6,
            )
    return response


# This middleware must be placed after the logging, to populate the context with the
# request ID
# NOTE: Why last??
# Answer: middlewares are applied in the reverse order of when they are added (you can
# verify this by debugging `app.middleware_stack` and recursively drilling down the
# `app` property).
app.add_middleware(CorrelationIdMiddleware)


# add application performance monitoring middleware
apm = make_apm_client(
    {
        "SERVICE_NAME": f"licensing-{settings.segment}",
        "SECRET_TOKEN": settings.apm_secret_token,
        "SERVER_URL": settings.apm_url,
        "ENVIRONMENT": settings.segment,
        "TRANSACTIONS_IGNORE_PATTERNS": ["^OPTIONS", "/v1/status"],
        "ENABLED": settings.apm_enabled,
        "SERVICE_VERSION": version,
        "TRANSACTION_SAMPLE_RATE": settings.apm_transaction_sample_rate,
        "COLLECT_LOCAL_VARIABLES": True,  # TODO: check
    }
)
app.add_middleware(ElasticAPM, client=apm)


@app.on_event("startup")
async def startup():
    pass


@app.on_event("shutdown")
async def shutdown():
    pass


ROUTE_PREFIX = "/v1"
app.include_router(api_router, prefix=ROUTE_PREFIX)
