FROM python:3.12-alpine

WORKDIR /opt/monitor

COPY monitor.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "monitor.py"]

