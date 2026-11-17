# Student Mental Health Risk Classification

A machine learning learning project that predicts the dataset's student mental health risk category: **Low**, **Medium**, or **High**. It uses academic, lifestyle, and personal-context features.

The project includes data inspection, EDA, preprocessing, model comparison and tuning, an Airflow training workflow, and a Streamlit prediction interface.

## Tools

Python, Pandas, scikit-learn, Matplotlib, JupyterLab, Streamlit, Airflow, and Docker Compose.

## Run locally

Install Docker with Docker Compose. Run commands from the project directory.

Use your existing `.env`. For a new checkout, copy `.env.example` to `.env`, replace the `CHANGE_ME` values, and set `LOCAL_UID` / `LOCAL_GID` to your user IDs. Airflow requires a valid Fernet key and a JWT secret.

Place the dataset at:

```text
data/raw/student_mental_health.csv
```

Start JupyterLab:

```bash
docker compose --profile notebook up -d --build jupyter
```

Open [localhost:8889](http://localhost:8889) and enter `JUPYTER_TOKEN` from `.env` in the **Password or token** field. Run notebooks using the Docker Jupyter server; `/workspace` paths refer to files inside the container.

## Notebook workflow

Run the notebooks in order:

1. `01_data_inspection.ipynb` — inspect columns, missing values, and invalid values.
2. `02_eda.ipynb` — explore distributions and relationships.
3. `03_preprocessing_features.ipynb` — prepare features and preprocessing.
4. `04_training_evaluation.ipynb` — compare models, tune candidates, evaluate, and save pipelines.

Models include Logistic Regression, Decision Tree, Random Forest, and SVC. Comparison uses five-fold stratified cross-validation with macro F1. Preprocessing is included in each model pipeline.

Saved models are written to `reports/models/`; figures go to `reports/figures/`.

## Prediction interface

After saving `reports/models/champion.joblib`, start Streamlit:

```bash
docker compose up -d --build streamlit
```

Open [localhost:8501](http://localhost:8501), enter a student profile, and run a prediction to see the predicted category and class probabilities.

## Airflow workflow

```bash
docker compose --profile orchestration up -d --build airflow
```

Open [localhost:8080](http://localhost:8080). The username comes from `AIRFLOW_ADMIN_USER` in `.env`; the password is stored in `runtime/airflow/auth/passwords.json`. The current Compose setup does not use `AIRFLOW_ADMIN_PASSWORD`.

Manually trigger the `student_risk_training` DAG. It validates the dataset, creates train/test splits, compares and tunes models, saves `champion.joblib`, and writes test metrics to `reports/evaluation.json`.

## Project structure

```text
notebooks/           Data exploration and training
src/classification/  Shared validation, preprocessing, training, and plotting
streamlit_app/       Prediction interface
dags/                Airflow workflow
data/                Raw and processed datasets
reports/             Models, evaluation results, and figures
docker/              Service Dockerfiles
requirements/        Python dependencies
runtime/             Airflow state, authentication, and logs
```

## Stop services

```bash
docker compose --profile notebook --profile orchestration down
```

Project files and service state persist through host bind mounts.
