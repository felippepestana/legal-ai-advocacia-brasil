FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY packages/ packages/
COPY services/ services/
COPY advocacia-brasil-hub/ advocacia-brasil-hub/
COPY config/ config/
RUN mkdir -p data/analytics/charts data/audit

EXPOSE 8080

CMD ["uvicorn", "services.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
