FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY web-preview /app/web-preview
COPY backend /app/backend
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080
WORKDIR /app/backend
CMD ["python3", "api.py"]
