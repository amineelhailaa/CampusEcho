from random import random

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

RANDOM_STATE = 42
N_SPLITS = 5
SCORING = "f1_macro"
N_ITER = 20
N_JOBS = 2

MODEL_CONFIGS = {
    "logistic_regression": {
        "model": LogisticRegression(max_iter=3000, random_state=RANDOM_STATE),
        "search_space": {"model__C": [0.01, 0.1, 1.0, 10.0, 100.0]},
    },
    "decision_tree": {
        "model": DecisionTreeClassifier(random_state=RANDOM_STATE),
        "search_space": {
            "model__max_depth": [None, 3, 5, 10],
            "model__min_samples_split": [2, 5, 10],
            "model__min_samples_leaf": [1, 2, 5],
        },
    },
    "random_forest": {
        "model": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1),
        "search_space": {
            "model__n_estimators": [100, 200, 300],
            "model__max_depth": [None, 5, 10],
            "model__min_samples_leaf": [1, 2, 5],
            "model__max_features": ["sqrt", "log2", None],
        },
    },
    "svc": {
        "model": SVC(kernel="rbf"),
        "search_space": {
            "model__C": [0.1, 1.0, 10.0],
            "model__gamma": ["scale", 0.01, 0.1],
        },
    },
}
