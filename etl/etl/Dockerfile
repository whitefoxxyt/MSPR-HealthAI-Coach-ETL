FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --no-create-home --shell /bin/false etl \
    && chown -R etl:etl /app

USER etl

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python healthcheck.py

CMD ["python", "scheduler.py"]
