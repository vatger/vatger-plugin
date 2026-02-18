FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

RUN groupadd --gid 10001 app \
 && useradd  --uid 10001 --gid 10001 --create-home --shell /usr/sbin/nologin app \
 && chown -R app:app /app

COPY pyproject.toml uv.lock* ./

COPY . .

RUN uv pip install --system --no-cache .

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "src"]