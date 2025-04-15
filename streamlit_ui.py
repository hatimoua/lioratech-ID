import streamlit as st
import json
import os
from verify_all import verify_id_and_face

st.set_page_config(
    page_title="LioraTech Light — ID Verification",
    page_icon="🪪",
    layout="centered"
)

col1, col2 = st.columns([1, 4])
with col1:
    st.image("logo.png", width=80)
with col2:
    st.markdown("## **LioraTech Light**")
    st.markdown("Secure Identity Verification")

st.markdown("---")

st.markdown("### 📤 Upload or Capture ID")
id_file = st.file_uploader("Upload ID image", type=["jpg", "jpeg", "png"])
if not id_file:
    id_file = st.camera_input("Or take a photo of your ID")

st.markdown("### 🤳 Upload or Capture Selfie")
selfie_file = st.file_uploader("Upload selfie image", type=["jpg", "jpeg", "png"])
if not selfie_file:
    selfie_file = st.camera_input("Or take a selfie")

if id_file and selfie_file:
    with open("temp_id.jpg", "wb") as f:
        f.write(id_file.getbuffer())
    with open("temp_selfie.jpg", "wb") as f:
        f.write(selfie_file.getbuffer())

    with st.spinner("Running verification..."):
        try:
            result = verify_id_and_face("temp_id.jpg", "temp_selfie.jpg")

            if "error" in result:
                st.error("❌ Verification failed: " + result["error"])
            else:
                st.markdown("### ✅ Face Match Score")
                st.success(f"**{result['Face Match Score']}%**")
                verdict_color = "🟢" if result["Verdict"] == "PASS" else "🟠" if result["Verdict"] == "REVIEW" else "🔴"
                st.markdown(f"**{verdict_color} VERDICT: {result['Verdict']}**")

                st.markdown("---")
                st.markdown("### 🧾 Extracted ID Fields")
                st.write(f"**Name:** {result['Name']}")
                st.write(f"**Date of Birth:** {result['Date of Birth']}")
                st.write(f"**ID Number:** {result['ID Number']}")

                if "ID Image URL" in result:
                    st.image(result["ID Image URL"], caption="ID Image (S3)", width=200)
                if "Selfie Image URL" in result:
                    st.image(result["Selfie Image URL"], caption="Selfie Image (S3)", width=200)

                st.markdown("---")
                st.markdown("### 📁 Export JSON")
                st.download_button(
                    label="📥 Download Result as JSON",
                    data=json.dumps(result, indent=2),
                    file_name="lioratech_verification.json",
                    mime="application/json"
                )

        except Exception as e:
            st.error(f"💥 Something went wrong: {e}")
