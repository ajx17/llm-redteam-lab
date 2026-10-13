FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /bin/uv
WORKDIR /app
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project
COPY app ./app
COPY data ./data
EXPOSE 8000
CMD ["uv", "run", "--no-dev", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
