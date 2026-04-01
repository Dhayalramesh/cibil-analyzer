
import streamlit as st
import pdfplumber
import re
import os

# -------------------------------
# Extract text from PDF
# -------------------------------
def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content
    return text


# -------------------------------
# Analyze CIBIL data
# -------------------------------
def analyze_cibil(text):
    result = {}

    score_match = re.search(r"\b\d{3}\b", text)
    result["score"] = int(score_match.group()) if score_match else None

    issues = []

    if "late payment" in text.lower():
        issues.append("Late payments found")

    if "utilization" in text.lower() or "credit usage" in text.lower():
        issues.append("High credit utilization")

    if "loan" in text.lower():
        issues.append("Multiple loans detected")

    result["issues"] = issues

    return result


# -------------------------------
# Rule-based advice
# -------------------------------
def generate_advice(data):
    advice = []

    score = data["score"]

    if score:
        if score < 650:
            advice.append("⚠️ Poor score")
        elif score < 700:
            advice.append("⚠️ Needs improvement")
        else:
            advice.append("✅ Good score")

    advice.append("👉 Pay EMIs on time")
    advice.append("👉 Keep usage below 30%")
    advice.append("👉 Avoid multiple loans")

    return advice


# -------------------------------
# AI Advice (Optional)
# -------------------------------
def get_ai_advice(text):
    try:
        from google import genai

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Explain this CIBIL report simply:\n{text}"
        )

        return response.text

    except:
        return None


# -------------------------------
# UI
# -------------------------------
st.set_page_config(page_title="CIBIL Analyzer", page_icon="💳")

st.title("💳 CIBIL Score Analyzer")
st.write("Upload your CIBIL report PDF and get insights instantly")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    st.success("File uploaded successfully")

    if st.button("Analyze"):
        text = extract_text(uploaded_file)
        data = analyze_cibil(text)

        st.subheader("Basic Analysis")
        st.write("Credit Score:", data["score"])
        st.write("Issues:", data["issues"] if data["issues"] else "No major issues")

        ai = get_ai_advice(text)

        if ai:
            st.subheader("AI Analysis")
            st.write(ai)
        else:
            st.subheader("Basic Advice")
            for tip in generate_advice(data):
                st.write(tip)
