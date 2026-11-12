import pandas as pd


def invalid_number(series, minimum, maximum, integer=False):
    numbers = pd.to_numeric(series, errors="coerce")
    valid = numbers.between(minimum, maximum)
    if integer:
        valid = valid & (numbers % 1 == 0)
    return series.notna() & ~valid




def invalid_category(series, values):
    return series.notna() & ~series.isin(values)


NUMERIC_RULES = {
    "Age": (1, 120, True),
    "Year_of_Study": (1, 5, True),
    "Sleep_Hours": (0, 24, False),
    "Study_Hours_Per_Week": (0, 168, False),
    "GPA": (0, 4, False),
    "Social_Media_Hours": (0, 24, False),
    "Screen_Time_Hours": (0, 24, False),
    "Financial_Stress": (1, 10, False),
    "Family_Support": (1, 10, False),
    "Attendance_Rate": (0, 100, False),
}

CATEGORY_RULES = {
    "Gender": ["Male", "Female", "Non-binary"],
    "Physical_Activity": ["Low", "Moderate", "High"],
    "Part_Time_Job": ["Yes", "No"],
    "Diet_Quality": ["Poor", "Average", "Good"],
    "Previous_Mental_Health_History": ["Yes", "No"],
    "Mental_Health_Risk": ["Low", "Medium", "High"],
}


def get_contradiction_mask(df):
    columns = ["Social_Media_Hours", "Screen_Time_Hours"]

    social = pd.to_numeric(df[columns[0]], errors="coerce")
    screen = pd.to_numeric(df[columns[1]], errors="coerce")
    return (
        social.between(0, 24)
        & screen.between(0, 24)
        & (social > screen)
    ).fillna(False)


def get_invalid_masks(df):
    masks = {}
    for column, (minimum, maximum, integer) in NUMERIC_RULES.items():
            masks[column] = invalid_number(df[column], minimum, maximum, integer)

    for column, values in CATEGORY_RULES.items():
        if column in df.columns:
            masks[column] = invalid_category(df[column], values)
    contradiction = get_contradiction_mask(df)
    for column in ["Social_Media_Hours", "Screen_Time_Hours"]:
            masks[column] = masks[column] | contradiction

    return masks
