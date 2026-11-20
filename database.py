"""Local SQLite storage: no MySQL server or credentials required."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'resume_history.sqlite3'


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_name TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            job_description TEXT,
            skill_score INTEGER,
            semantic_score INTEGER,
            matched_skills TEXT,
            missing_skills TEXT
        )''')


def save_analysis(resume_name, job_description, skill_score,
                  semantic_score, matched_skills, missing_skills):
    initialize_database()
    with get_connection() as conn:
        conn.execute('''INSERT INTO analysis_history
            (resume_name, job_description, skill_score, semantic_score,
             matched_skills, missing_skills) VALUES (?, ?, ?, ?, ?, ?)''',
             (resume_name, job_description, skill_score, semantic_score,
              ', '.join(matched_skills), ', '.join(missing_skills)))


def get_analysis_history():
    initialize_database()
    with get_connection() as conn:
        return [dict(row) for row in conn.execute('''SELECT id, resume_name,
            created_at, job_description, skill_score, semantic_score,
            matched_skills, missing_skills FROM analysis_history
            ORDER BY created_at DESC''').fetchall()]
