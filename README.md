# AI Resume Analyzer — runnable local version

Based on your uploaded AI Resume Analyzer project. This version uses **SQLite** for analysis history (no MySQL installation needed). Resume analysis, charts, PDF report, and local history are available in Streamlit. **Ollama is optional** for AI suggestions and resume chat.

## Windows PowerShell: quick start

Use **Python 3.11 or 3.12**. Extract the ZIP, open PowerShell inside the `AI_Resume_Analyzer` folder, then run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

If `py -3.12` isn't available, use `py -3.11`. If PowerShell blocks activation, you can skip it and use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe -m streamlit run app.py` instead.

Open the local address shown in PowerShell (usually `http://localhost:8501`). Upload a **text-based PDF resume**, paste a job description, and click **Analyze Resume**.

The first semantic analysis may download a Sentence Transformers model (`all-MiniLM-L6-v2`) and needs internet. If it cannot download, skill matching and other features can still work, but semantic similarity is shown as 0. Internet may also be needed to install Python packages.

## Optional: AI suggestions and chat

Install Ollama separately, then run in a PowerShell terminal:

```powershell
ollama pull qwen2.5:3b
```

Make sure Ollama is running locally (desktop app or `ollama serve` in a separate terminal). AI suggestions and chat call `http://localhost:11434` and require this model. Other features do not need Ollama.

## Storage and privacy

History is stored locally in `resume_history.sqlite3`. The uploaded resume and job description are processed on your computer; the optional Sentence Transformers model is downloaded from Hugging Face, and Ollama calls are local. Do not upload private resume data to public repositories. The score is an **estimate**, not a certified ATS result.

## Troubleshooting

- `py -3.12` not found: install Python 3.12 or try `py -3.11`.
- PDF text extraction error: use a text-selectable PDF, not a scanned image.
- Semantic model error: verify internet access on first use, then retry.
- Ollama error: start Ollama and ensure `qwen2.5:3b` was downloaded.
- Port in use: run `python -m streamlit run app.py --server.port 8502`.
