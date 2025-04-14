import streamlit as st
import json
import os
from verify_all import verify_id_and_face

# App config
st.set_page_config(
    page_title="LioraTech Light — ID Verification",
    page_icon="🪪",
    layout="centered"
)

# Logo + Title
col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown("## **LioraTech Light**")
    st.markdown("Secure Identity Verification")

st.markdown("---")

# Upload section
st.markdown("### 📤 Upload ID + Selfie")
id_file = st.file_uploader("Upload ID image", type=["jpg", "jpeg", "png"])
selfie_file = st.file_uploader("Upload selfie image", type=["jpg", "jpeg", "png"])

if id_file and selfie_file:
    with open("temp_id.jpg", "wb") as f:
        f.write(id_file.read())
    with open("temp_selfie.jpg", "wb") as f:
        f.write(selfie_file.read())

    with st.spinner("Running verification..."):
        result = verify_id_and_face("temp_id.jpg", "temp_selfie.jpg")

    st.markdown("### ✅ Face Match Score")
    st.success(f"**{result['Face Match Score']}%**")
    verdict_color = "🟢" if result["Verdict"] == "PASS" else "🟠" if result["Verdict"] == "REVIEW" else "🔴"
    st.markdown(f"**{verdict_color} VERDICT: {result['Verdict']}**")

    st.markdown("---")
    st.markdown("### 🧾 Extracted ID Fields")
    st.write(f"**Name:** {result['Name']}")
    st.write(f"**Date of Birth:** {result['Date of Birth']}")
    st.write(f"**ID Number:** {result['ID Number']}")

    st.markdown("---")
    st.markdown("### 📁 Export JSON")
    st.download_button(
        label="📥 Download Result as JSON",
        data=json.dumps(result, indent=2),
        file_name="lioratech_verification.json",
        mime="application/json"
    )
