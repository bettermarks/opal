ARG python_version 3.12.9

# INFO: we just install project dependencies in this layer
FROM python:${python_version}-slim-bookworm AS dependencies

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_PROJECT_ENVIRONMENT=/venv
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/

WORKDIR /code
COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv venv && uv sync --frozen --no-dev --no-install-project

# INFO: we take the virtual env and add the project itself
FROM python:${python_version}-slim-bookworm AS build
ENV UV_PROJECT_ENVIRONMENT=/venv
COPY --from=ghcr.io/astral-sh/uv:0.6.10 /uv /uvx /bin/
COPY --from=dependencies /venv /venv 

WORKDIR /code
COPY ./src .
COPY ./pyproject.toml .
COPY ./uv.lock .

RUN uv sync --extra export --frozen --no-editable --no-dev

# INFO: final image only with virtual env
FROM python:${python_version}-slim-bookworm
ENV PYTHONUNBUFFERED 1
COPY --from=build /venv /venv

CMD ["uvicorn", "services.licensing.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "0"]
