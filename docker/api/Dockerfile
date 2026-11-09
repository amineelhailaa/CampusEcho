FROM python:3.12.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 HOME=/tmp
WORKDIR /workspace
ENV PYTHONPATH=/workspace/src
COPY requirements/ /opt/requirements/
RUN pip install -r /opt/requirements/api.txt && pip check
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
