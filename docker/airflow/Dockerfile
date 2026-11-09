FROM apache/airflow:3.3.2-python3.12
COPY --chown=airflow:root requirements/ /opt/requirements/
RUN pip install "apache-airflow==3.3.2" -r /opt/requirements/airflow.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt" && pip check
WORKDIR /workspace
ENV PYTHONPATH=/workspace/src
