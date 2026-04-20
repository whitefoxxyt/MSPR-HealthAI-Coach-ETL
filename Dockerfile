FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends tini \
    && rm -rf /var/lib/apt/lists/*

COPY etl/requirements.txt .
RUN pip install --no-cache-dir --timeout=120 --retries=5 -r requirements.txt

COPY etl/ /app/
COPY data/raw /app/data/raw

RUN mkdir -p /app/data/processed /app/data/samples \
    && useradd --no-create-home --shell /bin/false etl \
    && chown -R etl:etl /app

USER etl

HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python healthcheck.py

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "scheduler.py"]
