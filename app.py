import streamlit as st
import pdfplumber
import docx
import re
import csv
from io import StringIO

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Resume Parser ATS",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.stApp {
    background-color: #f6f8fa;
    font-family: 'Segoe UI', sans-serif;
}
.header {
    font-size: 32px;
    font-weight: 700;
    color: #0a66c2;
}
.subheader {
    color: #666;
    margin-bottom: 10px;
}
.quote {
    background: #ffffff;
    padding: 15px;
    border-left: 6px solid #0a66c2;
    border-radius: 8px;
    font-style: italic;
    margin-bottom: 25px;
}
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.08);
}
.rank {
    font-size: 18px;
    font-weight: 600;
    color: #0a66c2;
}
.score {
    font-size: 24px;
    font-weight: 700;
    color: #2e7d32;
}
.label {
    font-weight: 600;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================

def extract_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    else:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text


def extract_email(text):
    emails = re.findall(r'\S+@\S+', text)
    return emails[0] if emails else "Not Found"


def extract_phone(text):
    phones = re.findall(r'\b\d{10}\b', text)
    return phones[0] if phones else "Not Found"


def keywords(text):
    text = re.sub(r'[^a-zA-Z ]', ' ', text)
    return set(text.lower().split())


def match_score(resume_text, job_text):
    r = keywords(resume_text)
    j = keywords(job_text)
    matched = r & j
    missing = j - r
    score = (len(matched) / len(j)) * 100 if j else 0
    return matched, missing, round(score, 2)


def csv_export(rows):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Resume", "Email", "Phone", "Match %"])
    for r in rows:
        writer.writerow(r)
    return buffer.getvalue()

# ================= SIDEBAR =================

st.sidebar.title("📄 Resume Parser ATS")
st.sidebar.write("Upload resumes and paste job description")
st.sidebar.markdown("---")

job_desc = st.sidebar.text_area(
    "🧾 Job Description",
    height=200,
    placeholder="Paste any job description (IT / Non-IT / Govt / Private)"
)

files = st.sidebar.file_uploader(
    "📂 Upload Resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True
)

# ================= MAIN CONTENT =================

st.markdown("<div class='header'>Resume Screening Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Universal resume parser for students & recruiters</div>", unsafe_allow_html=True)

# 🌱 Motivational Quote (ADDED)
st.markdown("""
<div class="quote">
🌟 <b>“Every small step you take today is building the success you will be proud of tomorrow.”</b>
</div>
""", unsafe_allow_html=True)

results = []

if files and job_desc.strip():

    for f in files:
        text = extract_text(f)
        email = extract_email(text)
        phone = extract_phone(text)
        matched, missing, score = match_score(text, job_desc)

        results.append({
            "file": f.name,
            "email": email,
            "phone": phone,
            "matched": matched,
            "missing": missing,
            "score": score
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    csv_rows = []

    for i, r in enumerate(results, 1):
        st.markdown(f"""
        <div class="card">
            <div class="rank">Rank {i} — {r['file']}</div><br>
            <span class="label">Email:</span> {r['email']}<br>
            <span class="label">Phone:</span> {r['phone']}<br><br>
            <span class="label">Matched Keywords:</span> {", ".join(list(r['matched'])[:12])}<br>
            <span class="label">Missing Keywords:</span> {", ".join(list(r['missing'])[:12])}<br><br>
            <div class="score">Match Score: {r['score']}%</div>
        </div>
        """, unsafe_allow_html=True)

        csv_rows.append([r["file"], r["email"], r["phone"], r["score"]])

    st.download_button(
        "⬇ Download Results (CSV)",
        data=csv_export(csv_rows),
        file_name="resume_ranking.csv",
        mime="text/csv"
    )

else:
    st.info("👈 Use the sidebar to upload resumes and paste a job description.")
