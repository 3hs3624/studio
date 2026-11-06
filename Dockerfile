# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ARG APP_UID=1000
ARG APP_GID=1000
WORKDIR /app
COPY --chown=${APP_UID}:${APP_GID} . /app
RUN --mount=type=secret,id=proxy_ca \
    if [ -f /run/secrets/proxy_ca ]; then PIP_CERT=/run/secrets/proxy_ca pip install --no-cache-dir -r deploy/requirements.txt; else pip install --no-cache-dir -r deploy/requirements.txt; fi \
    && groupadd -g "$APP_GID" studio && useradd -u "$APP_UID" -g studio -m studio \
    && DEBUG=1 SERVE_STATIC=1 python manage.py collectstatic --noinput \
    && chown -R studio:studio /app/staticfiles \
    && chmod 755 /app/deploy/start-render
USER studio
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:8000","--workers","2","--timeout","60","--access-logfile","-","--error-logfile","-"]
