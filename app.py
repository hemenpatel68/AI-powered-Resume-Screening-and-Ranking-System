import streamlit as st
import os
import fitz  # PyMuPDF
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Create 'resumes' folder if it doesn't exist
os.makedirs("resumes", exist_ok=True)

st.set_page_config(page_title="Resume Screening System", layout="wide")
st.title("📄 AI-powered Resume Screening and Ranking System")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Function to calculate similarity score
def calculate_score(resume_text, jd_text):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

# Job Description input
st.subheader("📝 Enter Job Description")
job_description = st.text_area("Paste the job description here", height=200)

# Upload resumes
st.subheader("📤 Upload Resumes (PDF only)")
uploaded_files = st.file_uploader("Upload one or more resumes", type=["pdf"], accept_multiple_files=True)

if uploaded_files and job_description.strip() != "":
    with st.spinner("Processing resumes..."):
        results = []

        for file in uploaded_files:
            file_path = os.path.join("resumes", file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())

            resume_text = extract_text_from_pdf(file_path)
            score = calculate_score(resume_text, job_description)

            results.append({
                "File Name": file.name,
                "Match Score": round(score * 100, 2),
                "Resume Snippet": resume_text[:250] + "..."
            })

        # Sort by score
        results = sorted(results, key=lambda x: x["Match Score"], reverse=True)

        st.subheader("🏆 Ranked Resumes")
        df = pd.DataFrame(results)
        st.dataframe(df[["File Name", "Match Score", "Resume Snippet"]], use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", data=csv, file_name="ranked_resumes.csv", mime="text/csv")

elif uploaded_files and job_description.strip() == "":
    st.warning("Please enter a job description before uploading resumes.")
