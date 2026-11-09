import os

import httpx
import streamlit as st

st.set_page_config(page_title="Classification", page_icon="📊")
st.title("Classification project")
st.write("Dataset selection and model training are pending.")
if st.button("Refresh status"):
    st.rerun()

try:
    with httpx.Client(
        base_url=os.environ.get("API_BASE_URL", "http://api:8000"), timeout=5.0
    ) as client:
        health = client.get("/health")
        health.raise_for_status()
        response = client.get("/model-info")
        response.raise_for_status()
        info = response.json()
    st.success("API connected")
    st.info("No model is loaded. Predictions will become available after training.")
    st.write({"Model configured": info["configured"], "Model loaded": info["loaded"]})
except (httpx.HTTPError, ValueError, KeyError):
    st.error("The prediction service is unavailable. Start FastAPI and refresh this page.")
