import pandas as pd


def invalid_number(series, minimum, maximum, integer=False):
    numbers = pd.to_numeric(series, errors="coerce")
    valid = numbers.between(minimum, maximum)
    if integer:
        valid = valid & (numbers % 1 == 0)
    return series.notna() & ~valid




def invalid_category(series, values):
    return series.notna() & ~series.isin(values)


def get_invalid_masks(df):
    student_id = df["Student_ID"]
    return {
        "Student_ID": student_id.notna() & (
            student_id.astype("string").str.strip().eq("")
            | ~student_id.map(lambda value: isinstance(value, str))
            | student_id.duplicated(keep=False)
        ),
        "Age": invalid_number(df["Age"], 1, 120, integer=True),
        "Gender": invalid_category(df["Gender"], ["Male", "Female", "Non-binary"]),
        "Year_of_Study": invalid_number(df["Year_of_Study"], 1, 5, integer=True),
        "Sleep_Hours": invalid_number(df["Sleep_Hours"], 0, 24),
        "Study_Hours_Per_Week": invalid_number(df["Study_Hours_Per_Week"], 0, 168),
        "GPA": invalid_number(df["GPA"], 0, 4),
        "Social_Media_Hours": invalid_number(df["Social_Media_Hours"], 0, 24),
        "Screen_Time_Hours": invalid_number(df["Screen_Time_Hours"], 0, 24),
        "Physical_Activity": invalid_category(
            df["Physical_Activity"], ["Low", "Moderate", "High"]
        ),
        "Financial_Stress": invalid_number(df["Financial_Stress"], 1, 10),
        "Family_Support": invalid_number(df["Family_Support"], 1, 10),
        "Attendance_Rate": invalid_number(df["Attendance_Rate"], 0, 100),
        "Part_Time_Job": invalid_category(df["Part_Time_Job"], ["Yes", "No"]),
        "Diet_Quality": invalid_category(df["Diet_Quality"], ["Poor", "Average", "Good"]),
        "Previous_Mental_Health_History": invalid_category(
            df["Previous_Mental_Health_History"], ["Yes", "No"]
        ),
        "Mental_Health_Risk": invalid_category(
            df["Mental_Health_Risk"], ["Low", "Medium", "High"]
        ),
    }
