# syntax=docker/dockerfile:1.6

FROM python:3.11-slim AS builder
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# System packages required to build Pillow wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim AS runtime
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies for Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libopenjp2-7 \
    libtiff5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder "$VIRTUAL_ENV" "$VIRTUAL_ENV"

# Non-root user for runtime
RUN useradd --create-home --uid 1000 iss
RUN install -d -o iss -g iss /var/lib/iss

WORKDIR /app
COPY iss.py ./
COPY example.env ./

USER iss
EXPOSE 8000
ENV ISS_HOST=0.0.0.0
ENV ISS_DATA=/var/lib/iss

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request, sys;\n\nurl='http://127.0.0.1:8000/health';\ntry:\n    urllib.request.urlopen(url)\nexcept Exception as exc:\n    print(exc, file=sys.stderr);\n    sys.exit(1)"

VOLUME ["/var/lib/iss"]

CMD ["uvicorn", "iss:app", "--host", "0.0.0.0", "--port", "8000"]
