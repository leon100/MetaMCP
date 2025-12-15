FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir hatchling

# Copy project files
COPY pyproject.toml README.md ./
COPY src ./src

# Build wheel
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels .

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -U -u 1000 mcp && \
    chown -R mcp:mcp /app

# Copy wheels and install
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl && \
    rm -rf /wheels

# Copy source code
COPY --chown=mcp:mcp src ./src

USER mcp

# Run the MCP server
CMD ["python", "-m", "src"]
