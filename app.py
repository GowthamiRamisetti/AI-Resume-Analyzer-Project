import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from resume_analyzer import extract_resume_text, extract_skills, compare_skills, semantic_match
from database import save_analysis, get_analysis_history
from resume_chat import chat_with_resume
from ai_suggestions import generate_suggestions
from section_scorer import score_resume_sections
from sentence_transformers import SentenceTransformer


@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


def generate_pdf_report(resume_name, skill_score, semantic_score,
                        matched_skills, missing_skills, ai_suggestions,
                        section_scores=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40,
                            leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("AI RESUME ANALYSIS REPORT", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Resume: {escape(resume_name)}", styles["Normal"]),
        Spacer(1, 14),
    ]
    total = len(matched_skills) + len(missing_skills)
    coverage = round(len(matched_skills) / total * 100) if total else 0
    data = [
        ["Metric", "Score"],
        ["Skill Match", f"{skill_score}/100"],
        ["Semantic Similarity", f"{semantic_score}/100"],
        ["Skill Coverage", f"{coverage}%"],
    ]
    table = Table(data, colWidths=[260, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243B55")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story += [table, Spacer(1, 14)]
    if section_scores:
        story.append(Paragraph("Section-wise Scores", styles["Heading2"]))
        for name, score in section_scores.items():
            story.append(Paragraph(f"{escape(name)}: {score}/100", styles["Normal"]))
        story.append(Spacer(1, 10))
    story += [
        Paragraph("Matched Skills", styles["Heading2"]),
        Paragraph(escape(", ".join(matched_skills) or "None"), styles["Normal"]),
        Spacer(1, 8),
        Paragraph("Missing Skills", styles["Heading2"]),
        Paragraph(escape(", ".join(missing_skills) or "None"), styles["Normal"]),
        Spacer(1, 12),
        Paragraph("AI Improvement Suggestions", styles["Heading2"]),
    ]
    for line in (ai_suggestions or "Generate AI suggestions in the app first.").splitlines():
        if line.strip():
            story.append(Paragraph(escape(line), styles["Normal"]))
            story.append(Spacer(1, 3))
    doc.build(story)
    buffer.seek(0)
    return buffer


st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")
st.title("📄 AI Resume Analyzer")
st.caption("Estimate resume-to-job match; scores are heuristics, not official employer ATS scores. AI features require local Ollama.")

if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
for key, default in {
    "resume_text": "", "resume_name": "Resume", "job_description": "",
    "matched_skills": [], "missing_skills": [], "score": 0,
    "semantic_score": 0, "chat_history": [], "ai_suggestions": "",
}.items():
    st.session_state.setdefault(key, default)

uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste the job description", height=180)

if st.button("🔍 Analyze Resume", type="primary"):
    if not uploaded_file or not job_description.strip():
        st.warning("Please upload a PDF resume and paste a job description.")
    else:
        try:
            with st.spinner("Analyzing resume..."):
                resume_text = extract_resume_text(uploaded_file)
                resume_skills = extract_skills(resume_text)
                job_skills = extract_skills(job_description)
                matched, missing, skill_score = compare_skills(resume_skills, job_skills)
                try:
                    model = load_embedding_model()
                    semantic_score = semantic_match(model, resume_text, job_description)
                except Exception as model_error:
                    st.warning(f"Semantic model unavailable: {model_error}. Skill matching still works.")
                    semantic_score = 0
                save_analysis(uploaded_file.name, job_description, skill_score,
                              semantic_score, matched, missing)
                st.session_state.update({
                    "analysis_done": True, "resume_text": resume_text,
                    "resume_name": uploaded_file.name, "job_description": job_description,
                    "matched_skills": matched, "missing_skills": missing,
                    "score": skill_score, "semantic_score": semantic_score,
                    "chat_history": [], "ai_suggestions": "",
                })
            st.success("Resume analyzed successfully!")
        except Exception as e:
            st.error(f"Analysis failed: {e}")

if st.session_state.analysis_done:
    matched = st.session_state.matched_skills
    missing = st.session_state.missing_skills
    st.divider()
    st.header("📈 Resume Analysis Results")
    c1, c2 = st.columns(2)
    c1.metric("Skill Match Score", f"{st.session_state.score}/100")
    c2.metric("Semantic Similarity", f"{st.session_state.semantic_score}/100")
    c1.subheader("✅ Matched Skills")
    c1.write(", ".join(matched) if matched else "No matched skills found.")
    c2.subheader("❌ Missing Skills")
    c2.write(", ".join(missing) if missing else "No missing skills found.")

    total = len(matched) + len(missing)
    coverage = round(len(matched) / total * 100) if total else 0
    st.subheader("Skill Gap Analysis")
    st.metric("Skill Coverage", f"{coverage}%")
    gap_df = pd.DataFrame({"Category": ["Matched", "Missing"],
                           "Count": [len(matched), len(missing)]})
    fig = px.pie(gap_df, names="Category", values="Count", hole=0.5,
                 title="Skills Breakdown")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.header("📊 Section-Wise ATS Analysis")
    section_scores, overall_section_score = score_resume_sections(st.session_state.resume_text)
    st.metric("Overall Resume Section Score", f"{overall_section_score}/100")
    section_df = pd.DataFrame({"Section": list(section_scores.keys()),
                               "Score": list(section_scores.values())})
    section_fig = px.bar(section_df, x="Section", y="Score", color="Score",
                         range_y=[0, 100], title="Resume Section Quality", text="Score")
    section_fig.update_traces(texttemplate="%{text}/100", textposition="outside")
    section_fig.update_layout(template="plotly_dark")
    st.plotly_chart(section_fig, use_container_width=True)
    for section, score in section_scores.items():
        if score >= 80:
            st.success(f"{section}: {score}/100")
        elif score >= 60:
            st.warning(f"{section}: {score}/100")
        else:
            st.error(f"{section}: {score}/100")

    st.divider()
    st.header("🤖 AI Resume Improvement Suggestions")
    if st.button("Generate AI Suggestions"):
        with st.spinner("Generating recommendations with Ollama..."):
            st.session_state.ai_suggestions = generate_suggestions(
                st.session_state.resume_text, st.session_state.job_description)
    if st.session_state.ai_suggestions:
        st.markdown(st.session_state.ai_suggestions)

    st.divider()
    st.header("📥 Download PDF Report")
    if st.button("Prepare PDF Report"):
        pdf_file = generate_pdf_report(
            st.session_state.resume_name, st.session_state.score,
            st.session_state.semantic_score, matched, missing,
            st.session_state.ai_suggestions, section_scores)
        st.download_button("Download Resume Analysis Report", data=pdf_file,
                           file_name="Resume_Analysis_Report.pdf",
                           mime="application/pdf")

    st.divider()
    st.header("💬 Chat with Your Resume")
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    question = st.chat_input("Ask something about your resume...")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.spinner("Thinking..."):
            answer = chat_with_resume(
                st.session_state.resume_text, st.session_state.job_description,
                question, st.session_state.chat_history[:-1])
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    st.divider()
    st.header("🗂️ Resume Analysis History")
    if st.button("Load Analysis History"):
        try:
            history = get_analysis_history()
            if history:
                st.dataframe(pd.DataFrame(history), use_container_width=True)
            else:
                st.info("No history found.")
        except Exception as e:
            st.error(f"Could not load history: {e}")

    st.divider()
    st.header("📊 Professional Dashboard")
    if st.button("Load Dashboard"):
        try:
            history = get_analysis_history()
            if not history:
                st.info("No analysis history available yet.")
            else:
                df = pd.DataFrame(history)
                if "created_at" in df:
                    df["created_at"] = pd.to_datetime(df["created_at"])
                    df = df.sort_values("created_at")
                a, b, c = st.columns(3)
                a.metric("Total Analyses", len(df))
                b.metric("Average Skill Score", f"{df['skill_score'].mean():.1f}/100")
                c.metric("Average Semantic Score", f"{df['semantic_score'].mean():.1f}/100")
                st.plotly_chart(px.bar(df, x="resume_name", y="skill_score",
                                      title="Skill Match Score by Resume",
                                      template="plotly_dark"), use_container_width=True)
                if "created_at" in df:
                    st.plotly_chart(px.line(df, x="created_at", y="semantic_score",
                                           color="resume_name", markers=True,
                                           title="Semantic Score Over Time",
                                           template="plotly_dark"), use_container_width=True)
                latest = float(df.iloc[-1]["semantic_score"])
                gauge = px.bar(x=["Latest Semantic Score"], y=[latest],
                               range_y=[0, 100], title="Latest Semantic Score")
                st.plotly_chart(gauge, use_container_width=True)
        except Exception as e:
            st.error(f"Dashboard error: {e}")
