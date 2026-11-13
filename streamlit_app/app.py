from pathlib import Path
import sys

import joblib
import pandas as pd
import streamlit as st

project_folder = Path(__file__).resolve().parent.parent
if str(project_folder / "src") not in sys.path:
    sys.path.insert(0, str(project_folder / "src"))
model_path = project_folder / "reports/models/champion.joblib"
risk_labels = {0: "Low", 1: "Medium", 2: "High"}

# st.config.set_option("theme.base", "dark")
# st.config.set_option("theme.backgroundColor", "#000000")
# st.config.set_option("theme.secondaryBackgroundColor", "#111111")
# st.config.set_option("theme.textColor", "#EEEEEE")
# st.config.set_option("theme.primaryColor", "#B8C4D4")
st.set_page_config(page_title="Champion · Model test", layout="centered")

st.title("Test a student profile")
st.divider()

values = {}
with st.form("profile"):
    st.subheader("01 · Student")
    a, b, c = st.columns(3)
    values["Age"] = a.number_input("Age", 1, 120, 21)
    values["Gender"] = b.selectbox("Gender", ["Male", "Female", "Non-binary"])
    values["Year_of_Study"] = c.number_input("Year of study", 1, 5, 2)
    st.divider()
    st.subheader("02 · Academic life")
    a, b = st.columns(2)
    values["GPA"] = a.number_input("GPA · out of 4", 0.0, 4.0, 3.0, 0.1)
    values["Study_Hours_Per_Week"] = b.number_input("Study · hours per week", 0.0, 168.0, 20.0, 1.0)
    values["Attendance_Rate"] = a.number_input("Attendance · %", 0.0, 100.0, 85.0, 1.0)
    values["Part_Time_Job"] = b.selectbox("Part-time job", ["No", "Yes"])
    st.divider()
    st.subheader("03 · Daily habits")
    a, b = st.columns(2)
    values["Sleep_Hours"] = a.number_input("Sleep · hours per day", 0.0, 24.0, 7.0, 0.5)
    values["Physical_Activity"] = b.selectbox("Physical activity", ["Low", "Moderate", "High"], index=1)
    values["Screen_Time_Hours"] = a.number_input("Screen time · hours per day", 0.0, 24.0, 5.0, 0.5)
    values["Social_Media_Hours"] = b.number_input("Social media · hours per day", 0.0, 24.0, 2.0, 0.5, help="Included in total screen time.")
    values["Diet_Quality"] = a.selectbox("Diet quality", ["Poor", "Average", "Good"], index=1)
    st.divider()
    st.subheader("04 · Personal context")
    a, b = st.columns(2)
    values["Financial_Stress"] = a.slider("Financial stress", 1, 10, 5, help="1 = lowest; 10 = highest.")
    values["Family_Support"] = b.slider("Family support", 1, 10, 7, help="1 = lowest; 10 = highest.")
    values["Previous_Mental_Health_History"] = st.selectbox("Previous mental health history", ["No", "Yes"])
    submitted = st.form_submit_button("Run prediction", type="primary", width="stretch")

if submitted:
    if values["Social_Media_Hours"] > values["Screen_Time_Hours"]:
        st.error("Social media hours cannot exceed total screen time.")
        st.stop()

    if not model_path.is_file():
        st.error("Champion model not found. Check the model volume mount.")
        st.stop()

    model = joblib.load(model_path)
    profile = pd.DataFrame([values])
    profile = profile[model.feature_names_in_]
    prediction = model.predict(profile)[0]
    probabilities = model.predict_proba(profile)[0]

    st.divider()
    st.subheader("Prediction")
    st.metric("Predicted risk category", risk_labels[prediction])

    columns = st.columns(3)
    for i in range(3):
        label = risk_labels[model.classes_[i]]
        columns[i].metric(label, f"{probabilities[i]:.1%}")
        columns[i].progress(float(probabilities[i]))
