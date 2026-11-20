import requests


def chat_with_resume(resume_text, job_description, question, chat_history=None):
    history = ""
    for item in (chat_history or [])[-8:]:
        role = item.get("role", "user")
        content = item.get("content", "")
        history += f"\n{role.upper()}: {content}\n"
    prompt = f"""You are a helpful resume and career assistant.
Answer using the resume and job description context. Do not fabricate facts.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

CONVERSATION:
{history}

USER QUESTION:
{question}
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:3b", "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        return response.json().get("response", "No response returned.")
    except requests.exceptions.RequestException as exc:
        return f"Chat error: {exc}. Check that Ollama is running."
