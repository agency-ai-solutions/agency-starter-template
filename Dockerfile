# -------- Stage 1: Builder --------
FROM python:3.13-slim AS builder

# Install build tools only for building dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Only copy requirements for better layer caching
COPY requirements.txt .

# Upgrade pip and install requirements into /install
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir -r requirements.txt

# -------- Stage 2: Runtime --------
FROM python:3.13-slim

# Install e2fs-progs for chattr command required by for provisioning
RUN apt-get update && \
    apt-get install -y --no-install-recommends e2fsprogs && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy source code
COPY ./ .

EXPOSE 8080

CMD ["python", "-u", "main.py"]
    