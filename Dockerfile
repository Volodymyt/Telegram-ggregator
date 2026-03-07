FROM python:3.12-slim

WORKDIR /var/app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/var/app/src

CMD ["python", "-m", "telegram_aggregator"]