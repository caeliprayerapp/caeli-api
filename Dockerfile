FROM python:3.12-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY api.py /app/backend/api.py
COPY server.py /app/web-preview/server.py
COPY prayers.py /app/web-preview/prayers.py
ENV HOST=0.0.0.0
EXPOSE 10000
WORKDIR /app/backend
CMD ["python3", "api.py"]
