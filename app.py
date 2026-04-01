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
# Analyze CIBIL data (FIXED)
# -------------------------------
def analyze_cibil(text):
    result = {}

    text_lower = text.lower()

    # 🔥 FIX 1: Better score detection
    score_match = re.search(r"(score|cibil)[^0-9]*(\d{3})", text_lower)

    if score_match:
        result["score"] = int(score_match.group(2))
    else:
        result["score"] = None

    # 🔥 FIX 2: Smarter issue detection
    issues = []

    if "late payment" in text_lower:
        issues.append("Late payments found")

    if "utilization" in text_lower or "%" in text:
        issues.append("High credit utilization")

    loan_count = len(re.findall(r"loan", text_lower))
    if loan_count >= 2:
        issues.append("Multiple loans detected")

    result["issues"] = issues

    return result


# -------------------------------
# Advice (IMPROVED)
# -------------------------------
def generate_advice(data):
    advice = []
    score = data["score"]

    if score:
        if score < 650:
            advice.append("⚠️ Poor score: Immediate improvement needed")
        elif score < 700:
            advice.append("⚠️ Average score: Needs improvement")
        elif score < 750:
            advice.append("🙂 Good score but can improve")
        else:
            advice.append("🔥 Excellent credit score")

    if "Late payments found" in data["issues"]:
        advice.append("👉 Pay EMIs and credit bills on time")

    if "High credit utilization" in data["issues"]:
        advice.append("👉 Keep credit usage below 30%")

    if "Multiple loans detected" in data["issues"]:
        advice.append("👉 Avoid taking multiple loans")

    advice.append("👉 Monitor your credit score regularly")

    return advice


# -------------------------------
# AI Advice (optional)
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

        st.subheader("📊 Analysis")
        st.write("**Credit Score:**", data["score"])
        st.write("**Issues:**", data["issues"] if data["issues"] else "No major issues")

        ai = get_ai_advice(text)

        if ai:
            st.subheader("🤖 AI Analysis")
            st.write(ai)
        else:
            st.subheader("💡 Recommendations")
            for tip in generate_advice(data):
                st.write(tip)
