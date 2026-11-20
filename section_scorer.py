import re


def score_resume_sections(resume_text):
    text = resume_text.lower()
    sections = {
        "Summary": [r"professional summary", r"career objective", r"summary", r"objective", r"profile"],
        "Skills": [r"technical skills", r"skills", r"technologies"],
        "Projects": [r"projects", r"project experience", r"academic projects"],
        "Experience": [r"experience", r"internship", r"work experience"],
        "Education": [r"education", r"academic background", r"qualifications"],
    }
    scores = {}
    for section, keywords in sections.items():
        match = re.search(r"(?im)^\\s*(?:" + "|".join(keywords) + r")\\s*:?\\s*$", text)
        if not match:
            # Also recognize headings embedded in extracted PDF text.
            match = re.search(r"(?i)(?:" + "|".join(keywords) + r")", text)
        if not match:
            scores[section] = 0
            continue
        content = text[match.end():match.end() + 1000]
        words = len(content.split())
        scores[section] = 90 if words >= 100 else 75 if words >= 60 else 60 if words >= 30 else 40
    return scores, round(sum(scores.values()) / len(scores)) if scores else 0
