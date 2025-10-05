# syntax=docker/dockerfile:1.6

FROM python:3.11-slim-bookworm AS builder
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim-bookworm AS runtime
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONUNBUFFERED=1

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
