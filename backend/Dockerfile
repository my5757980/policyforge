FROM python:3.13-slim

WORKDIR /app

# Install exactly what uv.lock pins. The lock must be copied before `uv sync`: without it uv
# re-resolves to the newest releases (SQLModel 0.0.47 breaks this app's naive datetimes).
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY . .

EXPOSE 8000
# --no-sync: run the environment built above; a plain `uv run` would install the dev group at start.
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
