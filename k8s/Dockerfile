FROM python:3.12.6-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code
COPY ./requirements* /code/

RUN python3 -m pip install --no-cache-dir -IU pip

COPY . /code/
RUN python3 -m pip install --no-cache-dir .[export]

CMD ["uvicorn", "services.licensing.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "0"]
