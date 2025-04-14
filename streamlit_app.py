import streamlit as st
from verify import compare_faces, extract_text

st.set_page_config(page_title="ID Verification", page_icon="🪪")

st.title("🪪 Identity Verification Demo")
st.markdown("Upload your government ID and a selfie to validate your identity.")

col1, col2 = st.columns(2)

with col1:
    id_img = st.file_uploader("Upload ID Image", type=["jpg", "jpeg", "png"])

with col2:
    selfie_img = st.file_uploader("Upload Selfie", type=["jpg", "jpeg", "png"])

if id_img and selfie_img:
    with open("temp_id.jpg", "wb") as f:
        f.write(id_img.read())
    with open("temp_selfie.jpg", "wb") as f:
        f.write(selfie_img.read())

    st.subheader("🔍 Face Match")
    matches = compare_faces("temp_id.jpg", "temp_selfie.jpg")
    if matches:
        score = matches[0]["Similarity"]
        st.success(f"✅ Match: {score:.2f}%")
        if score > 90:
            st.markdown("🟢 **VERDICT: PASS**")
        elif score > 80:
            st.markdown("🟠 **VERDICT: REVIEW**")
        else:
            st.markdown("🔴 **VERDICT: FAIL**")
    else:
        st.error("❌ No face match found.")

    import re

st.subheader("🧾 Extracted Info from ID")
text_lines = extract_text("temp_id.jpg")
seen = set()
cleaned = []

# Remove duplicates and empty lines
for line in text_lines:
    line = line.strip()
    if line and line not in seen:
        cleaned.append(line)
        seen.add(line)

# Display cleaned output
for line in cleaned:
    st.markdown(f"- {line}")

# Try to extract specific fields
def find_field(pattern, lines):
    for line in lines:
        match = re.search(pattern, line)
        if match:
            return match.group(1)
    return "Not found"

st.markdown("### 🧠 Parsed Fields:")
def extract_name(lines):
    for i in range(len(lines) - 1):
        line1 = lines[i].strip()
        line2 = lines[i + 1].strip()
        if re.fullmatch(r"[A-Z]{3,}", line1) and re.fullmatch(r"[A-Z]{3,}", line2):
            return f"{line1} {line2}"
    return "Not found"

name = extract_name(cleaned)

dob = find_field(r"(\d{4}-\d{2}-\d{2})", cleaned)
id_number = find_field(r"(T\d{4}-\d{6}-\d{2})", cleaned)
sex = find_field(r"Sexe\s*:\s*(\w)", cleaned)

st.write(f"**Name:** {name}")
st.write(f"**Date of Birth:** {dob}")
st.write(f"**ID Number:** {id_number}")
st.write(f"**Sex:** {sex}")

