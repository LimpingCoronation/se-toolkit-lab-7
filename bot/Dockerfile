# Bot Dockerfile - uses uv and pyproject.toml exclusively
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy bot source
COPY . .

# Sync dependencies using uv
RUN uv sync --frozen

# Run the bot
CMD ["uv", "run", "bot.py"]
