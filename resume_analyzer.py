import re
import PyPDF2
from sentence_transformers import util


# Keep this list extensible for your target roles.
SKILLS = [
    "python", "java", "sql", "mysql", "html", "css", "javascript",
    "flask", "fastapi", "rest api", "api", "git", "github", "docker",
    "machine learning", "deep learning", "nlp", "genai", "llm",
    "langchain", "rag", "prompt engineering", "pytorch", "tensorflow",
    "pandas", "numpy", "scikit-learn", "data analysis", "communication",
    "problem solving", "aws", "azure", "linux", "langgraph", "agentic ai", "mcp", "a2a", "chromadb", "chroma", "vector database", "hugging face", "groq", "streamlit", "ollama"
]


def extract_resume_text(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise ValueError("Could not extract text. Please upload a text-based PDF.")
    return text


def extract_skills(text):
    lower = text.lower()
    found = []
    for skill in SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            found.append(skill)
    return sorted(set(found))


def compare_skills(resume_skills, job_skills):
    resume_set, job_set = set(resume_skills), set(job_skills)
    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)
    score = round(len(matched) / len(job_set) * 100) if job_set else 0
    return matched, missing, score


def semantic_match(model, resume_text, job_description):
    embeddings = model.encode([resume_text, job_description], convert_to_tensor=True)
    score = float(util.cos_sim(embeddings[0], embeddings[1]).item()) * 100
    return max(0, min(100, round(score)))
