# syntax=docker/dockerfile:1
FROM postgres:16-bookworm AS postgres-tools
FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 liblz4-1 libzstd1 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=postgres-tools /usr/lib/postgresql/16/bin/pg_dump /usr/local/bin/pg_dump
COPY --from=postgres-tools /usr/lib/postgresql/16/bin/pg_restore /usr/local/bin/pg_restore
COPY --from=postgres-tools /usr/lib/x86_64-linux-gnu/libpq.so.5 /usr/local/lib/libpq.so.5
RUN ldconfig && pg_dump --version && pg_restore --version
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ARG APP_UID=1000
ARG APP_GID=1000
WORKDIR /app
COPY --chown=${APP_UID}:${APP_GID} . /app
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir -r deploy/requirements.txt; else pip install --no-cache-dir -r deploy/requirements.txt; fi \
    && test -r /app/deploy/run_services.py \
    && python -m py_compile /app/deploy/run_services.py /app/desk/management/commands/run_platform_worker.py \
    && groupadd -g "$APP_GID" studio && useradd -u "$APP_UID" -g studio -m studio \
    && DEBUG=1 SERVE_STATIC=1 python manage.py collectstatic --noinput \
    && chown -R studio:studio /app/staticfiles \
    && chmod 755 /app/deploy/start-render
USER studio
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","2","--timeout","60","--access-logfile","-","--error-logfile","-"]
