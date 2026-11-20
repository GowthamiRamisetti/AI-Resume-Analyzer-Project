import requests


def generate_suggestions(resume_text, job_description):
    prompt = f"""You are an expert ATS Resume Optimization AI.
Analyze the candidate's resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Provide:
1. ATS keyword analysis (important and missing keywords; natural additions)
2. Resume section quality (Summary, Skills, Projects, Experience, Education)
3. Rewrite 5 resume bullets professionally; do not invent metrics or achievements
4. Project improvements and relevant technologies
5. ATS formatting and keyword optimization
6. Estimated improvement score out of 100 with explanation
7. Five practical next steps

Be specific and professional. Never invent candidate experience.
"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "qwen2.5:3b", "prompt": prompt, "stream": False},
            timeout=180,
        )
        response.raise_for_status()
        return response.json().get("response", "No response returned by Ollama.")
    except requests.exceptions.RequestException as exc:
        return f"AI Suggestion Error: {exc}. Check that Ollama is running and the model is installed."
