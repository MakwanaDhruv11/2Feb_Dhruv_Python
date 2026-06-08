import re
import os
import json
import logging
from pypdf import PdfReader
import google.generativeai as genai

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Extracts raw text from a PDF file using pypdf.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {str(e)}")
    return text.strip()


def normalize_parsed_data(data):
    """
    Guarantees every expected key exists in the dict and matches the structured format
    required by the Django templates.
    """
    if not isinstance(data, dict):
        data = {}

    # String keys
    for key in ["name", "email", "phone", "github", "linkedin", "summary"]:
        if key not in data or data[key] is None:
            data[key] = ""
        else:
            data[key] = str(data[key]).strip()

    # Simple List keys
    for key in ["skills", "certifications"]:
        val = data.get(key, [])
        if not isinstance(val, list):
            if isinstance(val, str):
                data[key] = [item.strip() for item in re.split(r'[,;•\n]', val) if item.strip()]
            else:
                data[key] = []
        else:
            data[key] = [str(item).strip() for item in val if item]

    # Experience normalizer
    exp_list = data.get("experience", [])
    if not isinstance(exp_list, list):
        exp_list = [exp_list] if exp_list else []
    normalized_exp = []
    for exp in exp_list:
        if isinstance(exp, dict):
            normalized_exp.append({
                "title": str(exp.get("title", "Experience Detail")).strip(),
                "company": str(exp.get("company", "")).strip(),
                "duration": str(exp.get("duration", "")).strip(),
                "description": str(exp.get("description", "")).strip()
            })
        elif exp:
            normalized_exp.append({
                "title": str(exp).strip(),
                "company": "",
                "duration": "",
                "description": ""
            })
    data["experience"] = normalized_exp

    # Education normalizer
    edu_list = data.get("education", [])
    if not isinstance(edu_list, list):
        edu_list = [edu_list] if edu_list else []
    normalized_edu = []
    for edu in edu_list:
        if isinstance(edu, dict):
            normalized_edu.append({
                "degree": str(edu.get("degree", "Degree/Program")).strip(),
                "school": str(edu.get("school", "")).strip(),
                "year": str(edu.get("year", "")).strip()
            })
        elif edu:
            normalized_edu.append({
                "degree": str(edu).strip(),
                "school": "",
                "year": ""
            })
    data["education"] = normalized_edu

    # Projects normalizer
    proj_list = data.get("projects", [])
    if not isinstance(proj_list, list):
        proj_list = [proj_list] if proj_list else []
    normalized_proj = []
    for proj in proj_list:
        if isinstance(proj, dict):
            normalized_proj.append({
                "title": str(proj.get("title", "Project Detail")).strip(),
                "description": str(proj.get("description", "")).strip()
            })
        elif proj:
            normalized_proj.append({
                "title": str(proj).strip(),
                "description": ""
            })
    data["projects"] = normalized_proj

    return data


def parse_resume_heuristics(text):
    """
    Fallback parser using Regular Expressions and section heuristics.
    Extracts: name, email, phone, links, and divides text into sections.
    """
    parsed = {
        "name": "",
        "email": "",
        "phone": "",
        "github": "",
        "linkedin": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "summary": ""
    }
    
    if not text:
        return parsed

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # 1. Email extraction
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        parsed["email"] = email_match.group(0)
        
    # 2. Phone extraction
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        parsed["phone"] = phone_match.group(0)

    # 3. Social links extraction
    github_match = re.search(r'(?:https?://)?(?:www\.)?github\.com/[\w\.-]+', text, re.IGNORECASE)
    if github_match:
        parsed["github"] = github_match.group(0)
        
    linkedin_match = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w\.-]+', text, re.IGNORECASE)
    if linkedin_match:
        parsed["linkedin"] = linkedin_match.group(0)

    # 4. Name heuristic
    if lines:
        first_line = lines[0]
        if "@" not in first_line and "http" not in first_line and len(first_line) < 50:
            parsed["name"] = first_line
        elif parsed["email"]:
            parsed["name"] = parsed["email"].split('@')[0].replace('.', ' ').title()

    # 5. Section categorization based on standard keywords
    sections = {
        "summary": ["summary", "profile", "objective", "about me"],
        "skills": ["skills", "technical skills", "technologies", "expertise", "core competencies"],
        "education": ["education", "academic", "university", "school", "degree"],
        "experience": ["experience", "work experience", "employment", "history", "professional experience", "work history"],
        "projects": ["projects", "personal projects", "academic projects"],
        "certifications": ["certifications", "certificates", "awards", "courses"]
    }

    current_section = None
    section_buffer = []

    for line in lines:
        lower_line = line.lower()
        
        # Check if line is a header
        header_found = False
        for sec, keywords in sections.items():
            for kw in keywords:
                if re.match(rf'^\s*({kw})\s*$', lower_line) or (len(line) < 30 and lower_line.startswith(kw)):
                    if current_section:
                        save_section_data(parsed, current_section, section_buffer)
                    current_section = sec
                    section_buffer = []
                    header_found = True
                    break
            if header_found:
                break
                
        if not header_found and current_section:
            section_buffer.append(line)

    if current_section and section_buffer:
        save_section_data(parsed, current_section, section_buffer)

    return normalize_parsed_data(parsed)


def save_section_data(parsed_dict, section_name, lines):
    content = "\n".join(lines).strip()
    if section_name in ["skills", "education", "experience", "projects", "certifications"]:
        items = [item.strip() for item in re.split(r'[\n•\-\*]', content) if item.strip()]
        parsed_dict[section_name] = items
    else:
        parsed_dict[section_name] = content


def parse_resume_ai(text, api_key=None):
    """
    Parses resume text using Gemini AI model to extract structured data.
    Falls back to heuristic parser if API fails or API key is not configured.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        
    if not api_key:
        logger.info("GEMINI_API_KEY not found. Using regex heuristic parser fallback.")
        return parse_resume_heuristics(text)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are an expert AI recruiter. Parse the following resume text and structure it into a strict JSON payload.
        Do not add any markdown formatting (like ```json), commentary, or extra text. Output only a single valid JSON object.
        
        JSON Schema fields required:
        - name (string)
        - email (string)
        - phone (string)
        - skills (array of strings)
        - education (array of dictionaries describing degree, school, year)
        - experience (array of dictionaries describing title, company, duration, description)
        - projects (array of dictionaries describing title, description)
        - certifications (array of strings)
        - github (string url)
        - linkedin (string url)
        - summary (string overview of the candidate)

        Resume Text:
        {text}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = re.sub(r'^```(?:json)?\n', '', response_text)
            response_text = re.sub(r'\n```$', '', response_text)
            
        data = json.loads(response_text)
        return normalize_parsed_data(data)
        
    except Exception as e:
        logger.error(f"Gemini AI resume parsing failed: {str(e)}. Falling back to heuristic parser.")
        return parse_resume_heuristics(text)
