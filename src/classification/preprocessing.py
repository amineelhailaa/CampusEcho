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
            ("imputer", imputing_missing_values()),
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





def imputing_missing_values():
    numerical_pipeline = Pipeline([
        ("scaler", StandardScaler()),
        # ("imputer", KNNImputer(n_neighbors=5)),
        ("imputer", SimpleImputer(strategy="median")),
    ])

    return ColumnTransformer(transformers=[
        ("numerical", numerical_pipeline, list(NUMERIC_RULES)),
        ("categorical", SimpleImputer(strategy="most_frequent"),
         list(filter(lambda x: x != "Mental_Health_Risk", CATEGORY_RULES)),)
    ],
        verbose_feature_names_out=False).set_output(transform="pandas")  # false for getting same features without alias and out put to get same column name order


def remove_invalid_targets(df):
    valid_target = (df["Mental_Health_Risk"].notna()) & ~invalid_category(df["Mental_Health_Risk"], CATEGORY_RULES["Mental_Health_Risk"])
    return df.loc[valid_target].copy()

# def preprocessing(df):
#
#     cleaned_df = remove_invalid_targets(df)
#     X = cleaned_df.drop(columns=["Student_ID", "Mental_Health_Risk"])
#     y = cleaned_df["Mental_Health_Risk"]
#
#
#     X_train, X_test, y_train, y_test = train_test_split(
#         X,
#         y,
#         test_size = 0.2,
#         stratify=y,
#         random_state = RANDOM_STATE
#     )
#
#     pip = build_preprocessor()
#     processed_data = pip.fit_transform(X_train)
#     pd.load_csv
#     return