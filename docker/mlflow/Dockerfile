FROM python:3.12.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HOME=/tmp
WORKDIR /workspace
COPY requirements/ /opt/requirements/
RUN pip install -r /opt/requirements/mlflow.txt && pip check
