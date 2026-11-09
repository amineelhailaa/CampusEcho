"""Training only: compare baseline models, shortlist, then tune and refit.

Inputs are X_train (features) and y_train (labels). Keep the test set outside
these functions. They do not clean, encode, scale, split, save, or log data.
Learned preprocessing must be inside an externally built Pipeline so CV fits
it on each training fold, not on all data before CV. Such pipelines can be
passed wherever a model is accepted here.

Notebook example (X_train/y_train and untouched X_test/y_test already exist)::

    from classification.model_config import MODEL_CONFIGS
    from classification.training import (
        create_models, create_cross_validation, compare_models, tune_model,
    )

    models = create_models(MODEL_CONFIGS)
    cv = create_cross_validation()
    scores = compare_models(models, X_train, y_train, cv)
    print(scores)

    # Inspect scores and variation; you may shortlist the top two instead.
    name = scores.iloc[0]["model"]
    search = tune_model(
        models[name], MODEL_CONFIGS[name]["search_space"],
        X_train, y_train, cv, method="random",
    )
    print(search.best_params_, search.best_score_)
    final_model = search.best_estimator_  # Already fitted on ALL X_train.
    predictions = final_model.predict(X_test)
    # Evaluate once on y_test after selection; never use it to choose a model.

Use the same scoring argument for comparison and tuning. "f1" assumes positive
label 1; use a custom sklearn scorer for another positive label, or "f1_macro"
for multiclass. CV scores used for model selection are not final test scores.
API reference: https://scikit-learn.org/stable/modules/grid_search.html
"""

import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import (
    GridSearchCV,
    ParameterGrid,
    RandomizedSearchCV,
    StratifiedKFold,
    cross_validate,
)

from classification.model_config import N_ITER, N_JOBS, N_SPLITS, RANDOM_STATE, SCORING


def create_models(model_configs):
    """Return name -> fresh unfitted estimator, preserving config templates."""
    return {name: clone(config["model"]) for name, config in model_configs.items()}


def create_cross_validation(n_splits=N_SPLITS, random_state=RANDOM_STATE):
    """Return reproducible shuffled folds with similar class proportions.

    For independent rows only; grouped/time-series data need a different
    splitter. Each class must contain at least n_splits training examples.
    """
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)


def compare_models(models, X_train, y_train, cv, scoring=SCORING, n_jobs=N_JOBS):
    """Fit baseline clones in identical folds and return a ranked DataFrame.

    Columns: model, mean_score, std_score, mean_fit_time (seconds).
    Higher sklearn scorer values rank first. Original models stay unfitted.
    This returns scores, not fitted baseline models. Failures raise immediately.
    """
    if not models:
        raise ValueError("Provide at least one model to compare.")
    # Materialize once so every model uses exactly the same train/validation rows.
    folds = list(cv.split(X_train, y_train))
    rows = []
    for name, model in models.items():
        result = cross_validate(
            model, X_train, y_train, cv=folds, scoring=scoring,
            n_jobs=n_jobs, error_score="raise",
        )
        rows.append({
            "model": name,
            "mean_score": result["test_score"].mean(),
            "std_score": result["test_score"].std(),
            "mean_fit_time": result["fit_time"].mean(),
        })
    return pd.DataFrame(rows).sort_values(
        "mean_score", ascending=False, kind="stable", ignore_index=True,
    )


def tune_model(model, search_space, X_train, y_train, cv, *, method="random",
               scoring=SCORING, n_iter=N_ITER, n_jobs=N_JOBS,
               random_state=RANDOM_STATE):
    """Tune ONE shortlisted estimator and return the fitted sklearn search.

    method='grid' tries every combination; 'random' samples n_iter combinations
    (capped at the total for list-based spaces). Random search also accepts
    scipy distributions. n_iter/random_state apply only to random search.

    refit=True fits the winning configuration on all supplied training rows.
    Access best_estimator_ for prediction, best_params_ for the configuration,
    best_score_ for its mean CV score, and cv_results_ for all candidates.
    The input estimator is not modified. No preliminary fit is necessary.
    Include baseline parameter values in the space if you want them considered;
    tuning does not guarantee an improvement over the baseline.
    """
    options = dict(
        estimator=clone(model), cv=cv, scoring=scoring,
        n_jobs=n_jobs, refit=True, error_score="raise",
    )
    if method == "grid":
        search = GridSearchCV(param_grid=search_space, **options)
    elif method == "random":
        spaces = [search_space] if isinstance(search_space, dict) else search_space
        if all(not hasattr(value, "rvs") for space in spaces for value in space.values()):
            n_iter = min(n_iter, len(ParameterGrid(search_space)))
        search = RandomizedSearchCV(
            param_distributions=search_space, n_iter=n_iter,
            random_state=random_state, **options,
        )
    else:
        raise ValueError("method must be 'grid' or 'random'.")
    search.fit(X_train, y_train)
    return search
