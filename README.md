# Classification project

Start with JupyterLab for data inspection and EDA. Open `notebooks/01_data_inspection.ipynb` after placing your dataset in `data/raw/`.

## Start JupyterLab

From the project directory, run:

```bash
./scripts/bootstrap.sh
docker compose up -d --build jupyter
```

Bootstrap creates your local `.env` and folders. Open [JupyterLab](http://localhost:8889/lab) and enter the `JUPYTER_TOKEN` from `.env`. Your notebook edits are saved in the project's `notebooks/` folder.

```bash
docker compose stop jupyter
```

## Start other services when you need them

| What you need | Command | Where to open it |
|---|---|---|
| MLflow and PostgreSQL | `docker compose up -d mlflow` | [MLflow](http://localhost:5000), PostgreSQL on port 5433 |
| Streamlit and FastAPI | `docker compose up -d streamlit` | [Streamlit](http://localhost:8501), [API docs](http://localhost:8000/docs) |
| The full stack, including Airflow | `docker compose --profile notebook --profile orchestration up -d --build` | [Airflow](http://localhost:8080) |

Use `AIRFLOW_ADMIN_USER` and `AIRFLOW_ADMIN_PASSWORD` from `.env` for Airflow. A successful exit from `airflow-init` is expected after database setup.

To stop the whole stack:

```bash
docker compose --profile notebook --profile orchestration down
```

## How services connect

```text
Jupyter / Airflow ───► PostgreSQL: classification database (future dataset tables)
        │
        └───────────► MLflow ───► PostgreSQL: mlflow metadata
                         └────► runtime/mlflow/artifacts

Airflow components ─► PostgreSQL: airflow metadata

Streamlit ──────────► FastAPI ──► future registered preprocessing + model
```

Inside Docker use service names: `postgres:5432`, `mlflow:5000`, `api:8000`.
`localhost` inside a container refers to that container, not your computer.

One PostgreSQL instance contains separate `classification`, `mlflow`, and `airflow`
databases with separate login roles. No dataset-specific tables exist yet. PostgreSQL's
initialization script creates these only when `runtime/postgres` is empty. Changing a
password in `.env` does not change an existing database role's password; update the role
as well, then recreate dependent containers. Generated database credentials use URL-safe
hex strings. Keep custom database credentials URL-safe because connection URIs are
assembled through Compose interpolation.

MLflow stores parameters, metrics, experiment and registry metadata in PostgreSQL. Model
files and other artifacts go through the MLflow HTTP server into the mounted artifact
folder. No MinIO, Redis, Celery worker, or Docker socket mount is required.

## Project layout

- `src/classification/`: shared Python code. Docker adds `src/` to Python’s search path.
- `api/`: FastAPI shell. `streamlit_app/`: interface shell that calls FastAPI.
- `notebooks/`: inspection, detailed EDA, features/preprocessing, and training outlines.
- `dags/`: Airflow workflows.
- `requirements/`: separate pinned direct dependencies per environment. Shared ML
  versions live in `ml.txt`. The Airflow build downloads the official constraints from
  https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt.
- `docker/`: per-service images and PostgreSQL initialization.
- `configs/`: future dataset and training configuration.
- `data/raw`, `data/interim`, `data/processed`: future dataset files.
- `reports/figures`: future visualizations and evaluation outputs.
- `runtime/`: ignored persistent service state, never included in image build contexts.

Every persistent mount is a **host bind mount**. There are no named Docker volumes.
Application and configuration mounts are read-only where possible; Jupyter can edit
notebooks, shared source, configuration, data, and reports. Airflow can write data and
reports. Jupyter state, Airflow logs/authentication, model cache, MLflow artifacts, and
PostgreSQL storage all persist on the host. Container temporary files remain disposable.

Bootstrap uses your UID/GID for Jupyter and application processes. Airflow uses your UID
with group 0, as supported by its image. PostgreSQL manages ownership of its private data
directory; do not recursively change its ownership. Avoid `sudo` for bootstrap and do not
use `chmod 777`. If moving the project to another Linux account, adjust `LOCAL_UID` and
`LOCAL_GID` and grant that account ownership of writable application directories.

## API contract before training

| Endpoint | Behavior |
|---|---|
| `GET /health` | HTTP 200: `{"status":"ok"}` |
| `GET /ready` | HTTP 503 until model loading is implemented |
| `GET /model-info` | Reports configuration and loaded state; `loaded` is currently false |
| `POST /predict` | HTTP 503 with `MODEL_NOT_CONFIGURED` when `MODEL_URI` is empty |

Setting `MODEL_URI` records configuration only; it does not load a model in this phase.
Readiness and prediction then return HTTP 503 with `MODEL_LOADING_NOT_IMPLEMENTED`.
Streamlit displays API availability and the pending-model state. Prediction fields will
be defined after dataset selection.

## Development and later workflow

Source, notebook, and DAG edits appear through bind mounts. Restart FastAPI after changing
its source; Streamlit detects application changes. Rebuild images after changing requirements. Dependencies install at image build time, not every startup.

Once a labeled dataset is selected: establish feature availability and a holdout split;
explore training data; build preprocessing inside a scikit-learn Pipeline; compare
baselines; tune with cross-validation; evaluate on the untouched test set; track and
register the complete pipeline in MLflow; then implement model loading, validated
prediction schemas, and Streamlit inputs. Airflow will orchestrate reusable shared code.

## Backup and reset

Back up `.env`, notebooks, source, datasets, reports, and artifacts. For PostgreSQL, use
`pg_dump`/`pg_dumpall`, or stop the full stack before copying `runtime/postgres`; do not
copy live PostgreSQL files as a backup. Back up MLflow database metadata together with
its artifacts. Airflow authentication secrets and logs live under `runtime/airflow`.

`docker compose down` preserves bind-mounted data. Even `down -v` does not erase host
bind directories. A reset requires an explicit host-side action. To start fresh while
retaining a recoverable copy, stop the complete stack, rename `runtime` to a dated backup,
rerun bootstrap, then start the stack. This resets service metadata and experiment history
in the active stack; existing dataset, report, and notebook directories remain in place.

Reference: https://airflow.apache.org/docs/apache-airflow/3.3.2/howto/docker-compose/index.html
and https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/.
