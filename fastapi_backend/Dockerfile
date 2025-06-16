FROM ghcr.io/astral-sh/uv:python3.12-bookworm

ADD . /app

WORKDIR /app

# Install dependencies using uv
RUN uv sync --frozen 

ENV PATH="/app/.venv/bin:$PATH"

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["./start.sh"]