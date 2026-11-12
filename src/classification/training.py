import pandas as pd
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.model_selection import (
    GridSearchCV,
    ParameterGrid,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
)

from classification.model_config import N_ITER, N_JOBS, N_SPLITS, RANDOM_STATE, SCORING
from classification.preprocessing import build_preprocessor


def create_models(model_configs):
    return {name: Pipeline([
        ("preprocessing", build_preprocessor()),
        ("model", clone(config["model"])),
    ]) for name, config in model_configs.items()}


def create_cross_validation(n_splits=N_SPLITS, random_state=RANDOM_STATE):
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)


def compare_models(models, X_train, y_train, cv, scoring=SCORING, n_jobs=N_JOBS):
    if not models:
        raise ValueError("Provide at least one model to compare.")

    rows = []
    for name, model in models.items():
        result = cross_validate(
            model, X_train, y_train, cv=cv, scoring=scoring,
            n_jobs=n_jobs, error_score="raise",
        )
        rows.append({
            "model": name,
            "mean_score": result["test_score"].mean(),
            "std_score": result["test_score"].std(),
            "mean_fit_time": result["fit_time"].mean(),
        })
    return pd.DataFrame(rows).sort_values(
        "mean_score", ascending=False,
    )


def tune_model(model, search_space, X_train, y_train, cv, *, method="random",
               scoring=SCORING, n_iter=N_ITER, n_jobs=N_JOBS,
               random_state=RANDOM_STATE):


    options = dict(
        estimator=clone(model), cv=cv, scoring=scoring,
        n_jobs=n_jobs, refit=True, error_score="raise",
    )


    if method == "grid":
        search = GridSearchCV(param_grid=search_space, **options)
    elif method == "random":
        spaces = [search_space]
        n_iter = min(n_iter, len(ParameterGrid(search_space)))
        search = RandomizedSearchCV(
            param_distributions=search_space, n_iter=n_iter,
            random_state=random_state, **options,
        )
    else:
        raise ValueError("method must be 'grid' or 'random'.")
    search.fit(X_train, y_train)
    return search
