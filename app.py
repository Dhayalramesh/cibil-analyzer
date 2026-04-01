# ==========================================
# AI CIBIL ANALYZER (FINAL PREMIUM VERSION)
# ==========================================

import streamlit as st
import pdfplumber
import re
import os
import pandas as pd

# -------------------------------
# Extract text
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
# Analyze data (SMART)
# -------------------------------
def analyze_cibil(text):
    result = {}
    text_lower = text.lower()

    # Score detection (fixed)
    score_match = re.search(r"(score|cibil)[^0-9]*(\d{3})", text_lower)

    if score_match:
        result["score"] = int(score_match.group(2))
    else:
        result["score"] = None

    # Issue detection
    issues = []

    if "late payment" in text_lower:
        issues.append("Late payments")

    if "utilization" in text_lower or "%" in text:
        issues.append("High utilization")

    loan_count = len(re.findall(r"loan", text_lower))
    if loan_count >= 2:
        issues.append("Multiple loans")

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
        elif score < 750:
            advice.append("🙂 Good but can improve")
        else:
            advice.append("🔥 Excellent score")

    advice.append("👉 Pay EMIs on time")
    advice.append("👉 Keep usage below 30%")
    advice.append("👉 Avoid multiple loans")

    return advice


# -------------------------------
# AI advice (optional)
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
st.set_page_config(page_title="AI CIBIL Analyzer", page_icon="💳")

st.title("💳 AI CIBIL Analyzer")
st.markdown("### Upload your credit report and get instant insights")
st.markdown("---")

uploaded_file = st.file_uploader("📂 Upload CIBIL PDF", type="pdf")

if uploaded_file:
    st.success("File uploaded successfully")

    if st.button("🔍 Analyze Report"):
        text = extract_text(uploaded_file)
        data = analyze_cibil(text)

        # -------------------------------
        # SUMMARY
        # -------------------------------
        st.subheader("📊 Credit Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Credit Score", data["score"] if data["score"] else "N/A")

        with col2:
            st.metric("Issues Found", len(data["issues"]))

        # -------------------------------
        # SCORE METER
        # -------------------------------
        if data["score"]:
            st.progress(data["score"] / 900)

            if data["score"] < 650:
                st.error("Poor Credit Score")
            elif data["score"] < 700:
                st.warning("Average Score")
            else:
                st.success("Good Credit Score")

        # -------------------------------
        # ISSUE CHART
        # -------------------------------
        if data["issues"]:
            df = pd.DataFrame({
                "Issue": data["issues"],
                "Count": [1] * len(data["issues"])
            })

            st.subheader("📊 Issue Breakdown")
            st.bar_chart(df.set_index("Issue"))

        # -------------------------------
        # AI / FALLBACK
        # -------------------------------
        ai = get_ai_advice(text)

        if ai:
            st.subheader("🤖 AI Analysis")
            st.write(ai)
        else:
            st.subheader("💡 Recommendations")
            for tip in generate_advice(data):
                st.write(tip)
