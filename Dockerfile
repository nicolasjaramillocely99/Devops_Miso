# ECR Public mirror del Python oficial — evita rate limit de Docker Hub en CodeBuild
FROM public.ecr.aws/docker/library/python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NEW_RELIC_LOG=stdout

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY application.py .

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["newrelic-admin", "run-program", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "application:application"]
