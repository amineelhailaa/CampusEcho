"""Editable model templates and training defaults.

Search spaces use estimator parameter names (for example C). When supplying
an existing Pipeline, prefix them with its step name (for example model__C).
No fitting happens when this module is imported.
"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

RANDOM_STATE = 42
N_SPLITS = 5
SCORING = "f1"  # Binary classification, positive label 1. Use f1_macro for multiclass.
N_ITER = 20
N_JOBS = 2

MODEL_CONFIGS = {
    "logistic_regression": {
        "model": LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
        "search_space": {"C": [0.01, 0.1, 1.0, 10.0, 100.0]},
    },
    "decision_tree": {
        "model": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "search_space": {
            "max_depth": [None, 3, 5, 10],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 5],
        },
    },
    "random_forest": {
        # CV parallelizes the fits; each forest uses one worker.
        "model": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1),
        "search_space": {
            "n_estimators": [100, 200, 300],
            "max_depth": [None, 5, 10],
            "min_samples_leaf": [1, 2, 5],
            "max_features": ["sqrt", "log2", None],
        },
    },
}
