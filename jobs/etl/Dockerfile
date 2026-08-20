FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app \
    ETL_COMMAND=run-all \
    ETL_WINDOW=latest \
    STORAGE_BACKEND=azure

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jobs ./jobs
COPY packages ./packages
COPY sql ./sql
COPY src ./src

CMD if [ "$ETL_COMMAND" = "normalize" ]; then \
        python -m jobs.etl.main normalize --raw-file "$RAW_FILE"; \
    elif [ "$ETL_COMMAND" = "smoke-adls" ]; then \
        python -m jobs.etl.main smoke-adls --storage "$STORAGE_BACKEND"; \
    elif [ -n "$ETL_TIMESTAMP" ]; then \
        python -m jobs.etl.main "$ETL_COMMAND" --timestamp "$ETL_TIMESTAMP" --storage "$STORAGE_BACKEND"; \
    else \
        python -m jobs.etl.main "$ETL_COMMAND" --window "$ETL_WINDOW" --storage "$STORAGE_BACKEND"; \
    fi
