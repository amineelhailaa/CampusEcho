import json

from airflow.sdk import dag, task
from datetime import datetime
from pathlib import  Path
import pandas as pd

from classification.validation import NUMERIC_RULES, CATEGORY_RULES


@dag(
    dag_id="student_risk_training",
    start_date=datetime(2026, 11, 11),
    end_date=datetime(2026, 12, 1),
    schedule=None,
    catchup=False,
)
def student_risk_training():

    @task
    def validate():
        import pandas as pd
        from classification.validation import NUMERIC_RULES, CATEGORY_RULES

        path = Path("/workspace/data/raw/student_mental_health.csv")
        df = pd.read_csv(path)

        required = {"Student_ID", *NUMERIC_RULES, *CATEGORY_RULES}
        missing = required - set(df.columns)

        if df.empty:
            raise ValueError("Dataset is empty")
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        print(f"Validated {len(df)} rows")
        return str(path)


    @task
    def prepare(raw_path):
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from classification.model_config import RANDOM_STATE
        from classification.preprocessing import remove_invalid_targets

        df = remove_invalid_targets(pd.read_csv(raw_path))
        risk_codes = {"Low": 0, "Medium": 1, "High": 2}


        X = df.drop(columns=["Student_ID", "Mental_Health_Risk"])
        y = df["Mental_Health_Risk"].map(risk_codes)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
        )

        folder = Path("/workspace/data/processed")
        folder.mkdir(parents=True, exist_ok=True)
        train_path = folder / "train.csv"
        test_path = folder / "test.csv"

        X_train.assign(target=y_train).to_csv(train_path, index=False)
        X_test.assign(target=y_test).to_csv(test_path, index=False)

        return {"train": str(train_path), "test": str(test_path)}

    @task
    def train(paths):
        import joblib
        import pandas as pd
        from classification.model_config import MODEL_CONFIGS
        from classification.training import (
            create_models, create_cross_validation,
            compare_models, tune_model,
        )

        train_df = pd.read_csv(paths["train"])
        y_train = train_df.pop("target")
        X_train = train_df

        models = create_models(MODEL_CONFIGS)
        cv = create_cross_validation()
        scores = compare_models(models, X_train, y_train, cv)

        best_name = scores.iloc[0]["model"]
        search = tune_model(
            models[best_name],
            MODEL_CONFIGS[best_name]["search_space"],
            X_train, y_train, cv,
            method="grid",
        )

        model_path = Path("/workspace/reports/models/champion.joblib")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(search.best_estimator_, model_path)

        print(f"Selected {best_name}; CV F1 macro: {search.best_score_:.3f}")
        return str(model_path)

    @task
    def evaluate(paths, model_path):
        import joblib
        import pandas as pd
        from sklearn.metrics import (
            accuracy_score, classification_report,
            confusion_matrix, roc_auc_score,
        )

        test_df = pd.read_csv(paths["test"])
        y_test = test_df.pop("target")
        model = joblib.load(model_path)
        y_pred = model.predict(test_df)

        labels = list(model.classes_)
        names = [{0: "Low", 1: "Medium", 2: "High"}[x] for x in labels]

        results = {
            "accuracy": accuracy_score(y_test, y_pred),
            "classification_report": classification_report(
                y_test, y_pred, labels=labels,
                target_names=names, output_dict=True
            ),
            "confusion_matrix": confusion_matrix(
                y_test, y_pred, labels=labels
            ).tolist(),
        }

        if hasattr(model, "predict_proba"):
            results["roc_auc_macro_ovr"] = roc_auc_score(
                y_test, model.predict_proba(test_df),
                labels=labels, multi_class="ovr", average="macro"
            )

        output = Path("/workspace/reports/evaluation.json")
        output.write_text(json.dumps(results, indent=2))
        print(f"Evaluation saved to {output}")

    paths = prepare(validate())
    training = train(paths)
    evaluate(paths, training)


student_risk_training()

