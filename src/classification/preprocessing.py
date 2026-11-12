import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    FunctionTransformer, OneHotEncoder, OrdinalEncoder, StandardScaler,
)

from classification.model_config import RANDOM_STATE
from classification.validation import CATEGORY_RULES, NUMERIC_RULES, get_invalid_masks, invalid_category


def cast_columns(X):
    transformed = X.copy()
    for column in NUMERIC_RULES:
        transformed[column] = pd.to_numeric(
            transformed[column], errors="coerce"
        ).astype("float64")

    for column in ["Student_ID", *CATEGORY_RULES]:
        if column in transformed.columns:
            text = transformed[column].astype("string")
            transformed[column] = text.astype(object).where(text.notna(), np.nan)
    return transformed


def invalid_values_to_nan(X):
    transformed = X.copy()
    for column, invalid in get_invalid_masks(X).items():
        transformed[column] = transformed[column].mask(invalid, np.nan)
    return transformed


def build_preprocessor():

    return Pipeline(
        steps=[
            ("cast_columns", FunctionTransformer(
                cast_columns,
                validate=False,
                feature_names_out="one-to-one"
            )),
            ("invalid_to_nan", FunctionTransformer(
                invalid_values_to_nan,
                validate=False,
                feature_names_out="one-to-one"
            )),
            ("imputer", impute_missing_values()),
            ("scaler", scale_numeric_columns()),
            ("encode", categorical_encode()),

        ]
    )


def categorical_encode():
    return ColumnTransformer(
        transformers=[
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ["Gender"],
            ),
            (
                "ordinal",
                OrdinalEncoder(categories=[
                    ["Low", "Moderate", "High"],
                    ["Poor", "Average", "Good"],
                ]),
                ["Physical_Activity", "Diet_Quality"],
            ),
            (
                "binary",
                OrdinalEncoder(categories=[
                    ["No", "Yes"],
                    ["No", "Yes"],
                ]),
                ["Part_Time_Job", "Previous_Mental_Health_History"],
            ),
        ],
        remainder="passthrough"
    )







def impute_missing_values():
    categorical_columns = list(
        filter(lambda column: column != "Mental_Health_Risk", CATEGORY_RULES)
    )

    return ColumnTransformer(
        transformers=[
            ("numerical", SimpleImputer(strategy="median"), list(NUMERIC_RULES)),
            ("categorical", SimpleImputer(strategy="most_frequent"), categorical_columns),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")


def scale_numeric_columns():
    return ColumnTransformer(
        transformers=[
            ("numerical", StandardScaler(), list(NUMERIC_RULES)),
        ],
        remainder="passthrough",
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")


def remove_invalid_targets(df):
    valid_target = (df["Mental_Health_Risk"].notna()) & ~invalid_category(df["Mental_Health_Risk"], CATEGORY_RULES["Mental_Health_Risk"])
    return df.loc[valid_target].copy()

