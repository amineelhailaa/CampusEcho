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
| Streamlit | `docker compose up -d --build streamlit` | [Streamlit](http://localhost:8501) |
| The full stack, including Airflow | `docker compose --profile notebook --profile orchestration up -d --build` | [Airflow](http://localhost:8080) |

Use `AIRFLOW_ADMIN_USER` and `AIRFLOW_ADMIN_PASSWORD` from `.env` for Airflow. Airflow runs in a single standalone container and initializes its local SQLite metadata automatically.

To stop the whole stack:

```bash
docker compose --profile notebook --profile orchestration down
```

## How services connect

Jupyter reads and writes project files directly. Streamlit is a standalone interface shell.
Airflow runs with SQLite metadata stored in `runtime/airflow/state/airflow.db`.
This standalone configuration is for local development, not production.

## Project layout

- `src/classification/`: shared Python code. Docker adds `src/` to Python’s search path.
- `streamlit_app/`: standalone interface shell.
- `notebooks/`: inspection, detailed EDA, features/preprocessing, and training outlines.
- `dags/`: Airflow workflows.
- `requirements/`: separate pinned direct dependencies per environment. Shared ML
  versions live in `ml.txt`. The Airflow build downloads the official constraints from
  https://raw.githubusercontent.com/apache/airflow/constraints-3.3.2/constraints-3.12.txt.
- `docker/`: per-service images.
- `configs/`: future dataset and training configuration.
- `data/raw`, `data/interim`, `data/processed`: future dataset files.
- `reports/figures`: future visualizations and evaluation outputs.
- `runtime/`: ignored persistent service state, never included in image build contexts.

Every persistent mount is a **host bind mount**. There are no named Docker volumes.
Application and configuration mounts are read-only where possible; Jupyter can edit
notebooks, shared source, configuration, data, and reports. Airflow can write data and
reports. Jupyter state and Airflow logs, authentication, and SQLite metadata all persist on the host. Container temporary files remain disposable.

Bootstrap uses your UID/GID for Jupyter and application processes. Airflow uses your UID
with group 0, as supported by its image. Avoid `sudo` for bootstrap and do not
use `chmod 777`. If moving the project to another Linux account, adjust `LOCAL_UID` and
`LOCAL_GID` and grant that account ownership of writable application directories.

## Development and later workflow

Source, notebook, and DAG edits appear through bind mounts. Streamlit detects application changes. Rebuild images after changing requirements. Dependencies install at image build time, not every startup.

Once a labeled dataset is selected: establish feature availability and a holdout split;
explore training data; build preprocessing inside a scikit-learn Pipeline; compare
baselines; tune with cross-validation; evaluate on the untouched test set; save the
complete pipeline; then implement model loading and Streamlit inputs. Airflow will orchestrate reusable shared code.

## Backup and reset

Back up `.env`, notebooks, source, datasets, reports, and artifacts.
Stop Airflow before copying `runtime/airflow`, which contains its SQLite metadata,
authentication secrets, and logs.

`docker compose down` preserves bind-mounted data. Even `down -v` does not erase host
bind directories. A reset requires an explicit host-side action. To start fresh while
retaining a recoverable copy, stop the complete stack, rename `runtime` to a dated backup,
rerun bootstrap, then start the stack. This resets service metadata
in the active stack; existing dataset, report, and notebook directories remain in place.

Reference: https://airflow.apache.org/docs/apache-airflow/3.3.2/howto/docker-compose/index.html.
