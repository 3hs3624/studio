# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
ARG APP_UID=1000
ARG APP_GID=1000
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
COPY deploy/requirements.txt /app/deploy/requirements.txt
RUN --mount=type=secret,id=proxy_ca \
    if [ -s /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir -r deploy/requirements.txt; else pip install --no-cache-dir -r deploy/requirements.txt; fi
COPY config /app/config
COPY desk /app/desk
COPY manage.py /app/manage.py
COPY deploy/local_split/start.py /app/deploy/local_split/start.py
# Build sources may have host permissions 0600/0700. Runtime UID must read them.
RUN chmod -R a+rX /app && DEBUG=1 SERVE_STATIC=1 python manage.py collectstatic --noinput
USER ${APP_UID}:${APP_GID}
CMD ["python", "deploy/local_split/start.py", "web"]
