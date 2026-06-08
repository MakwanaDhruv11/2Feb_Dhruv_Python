import os
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

def generate_cover_letter_heuristics(resume, job):
    """
    Fallback cover letter generator using templates and parsed details.
    """
    parsed = resume.parsed_data
    name = parsed.get("name", resume.user.username)
    email = parsed.get("email", resume.user.email)
    phone = parsed.get("phone", "")
    linkedin = parsed.get("linkedin", "")
    
    # Skills list
    skills = parsed.get("skills", [])
    skills_str = ", ".join(skills[:4]) if skills else "software development, problem solving, and backend systems engineering"
    
    # Work Experience
    experience = parsed.get("experience", [])
    recent_role = ""
    if experience and isinstance(experience, list):
        first_exp = experience[0]
        if isinstance(first_exp, dict):
            recent_role = f"my role as {first_exp.get('title', 'Engineer')} at {first_exp.get('company', 'my previous firm')}"
        else:
            recent_role = f"my previous work experience: {first_exp}"
            
    # Compile template
    letter = f"""[Candidate Name: {name}]
[Contact: {email} | {phone}]
[LinkedIn: {linkedin}]

Date: May 19, 2026

Hiring Manager
{job.company}
{job.location|default("Remote Office")}

Subject: Application for {job.title}

Dear Hiring Manager,

I am writing to express my strong interest in the {job.title} position at {job.company}. With a solid foundation in software engineering and hands-on experience, I am confident that my skills and background make me an excellent candidate for this opportunity.

Recently, in {recent_role if recent_role else 'my professional projects'}, I have refined my expertise in key technical areas, specifically focusing on {skills_str}. I pride myself on writing clean, maintainable code and solving complex technical bottlenecks.

What excites me most about {job.company} is your focus on technology innovation and operational excellence. I am eager to apply my technical capacity to your active engineering pipelines and contribute to your team's upcoming milestones.

Thank you for your time and consideration. I welcome the opportunity to discuss my qualifications further in an interview.

Sincerely,

{name}"""
    return letter.strip()


def generate_cover_letter_ai(resume, job, api_key=None):
    """
    Generates cover letter using Gemini AI, matching resume attributes with job requirements.
    """
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        logger.info("GEMINI_API_KEY not configured. Using template cover letter fallback.")
        return generate_cover_letter_heuristics(resume, job)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        parsed_resume = resume.parsed_data
        
        prompt = f"""
        You are an expert recruiter and career coach. Write a highly tailored, professional cover letter 
        for a candidate applying to a specific job listing. Make sure to reference matching skills 
        from the candidate's resume and describe how they align with the job description.
        
        Candidate Details:
        - Name: {parsed_resume.get('name', resume.user.username)}
        - Email: {parsed_resume.get('email', resume.user.email)}
        - Phone: {parsed_resume.get('phone', '')}
        - Professional Links: LinkedIn ({parsed_resume.get('linkedin', '')}), GitHub ({parsed_resume.get('github', '')})
        - Core Skills: {parsed_resume.get('skills', [])}
        - Experience summary: {parsed_resume.get('experience', [])}
        - Education summary: {parsed_resume.get('education', [])}
        - Summary: {parsed_resume.get('summary', '')}
        
        Job Details:
        - Position Title: {job.title}
        - Company: {job.company}
        - Location: {job.location}
        - Description: {job.description}
        
        Write a professional, compelling, and customized cover letter. Do not include markdown brackets, annotations, or extra text outside the cover letter itself.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"AI Cover letter generation failed: {str(e)}. Falling back to templates.")
        return generate_cover_letter_heuristics(resume, job)


def generate_assisted_apply_data(resume, job, api_key=None):
    """
    Assembles a cheat sheet of customized answers for screening questions, pre-filling details.
    """
    parsed = resume.parsed_data
    name = parsed.get("name", resume.user.username)
    email = parsed.get("email", resume.user.email)
    phone = parsed.get("phone", "")
    linkedin = parsed.get("linkedin", "")
    github = parsed.get("github", "")
    skills = parsed.get("skills", [])
    skills_str = ", ".join(skills[:5]) if skills else "Python, Django, databases"

    # Default heuristic answers
    answers = [
        {
            "question": "Why are you interested in this role?",
            "answer": f"I am highly interested in the {job.title} position at {job.company} because my background in engineering aligns with your technical requirements. I want to bring my software development expertise to solve your engineering bottlenecks and work with your active team."
        },
        {
            "question": "Describe your experience with the primary technologies listed in our job post.",
            "answer": f"I have strong hands-on experience in software development, particularly using technologies like {skills_str}. In my past projects, I have implemented scalable backend architectures, designed schemas, and managed API integrations."
        },
        {
            "question": "What is your target compensation/salary range?",
            "answer": f"My target compensation is flexible depending on benefits, equity, and overall career development. I am seeking market-rate competitive compensation for a {job.title} role."
        }
    ]

    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")

    if not api_key:
        return {
            "name": name, "email": email, "phone": phone, "linkedin": linkedin, "github": github,
            "skills": skills, "answers": answers
        }

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        You are a job application helper. Tailor short, compelling, and professional responses (2-3 sentences max) 
        for a candidate applying to a job. Respond in raw text with three sections separating:
        1. Why do you want to work at {job.company} as a {job.title}?
        2. Describe your experience with software development and core tech ({skills_str}).
        3. What is your relevant project experience?
        
        Candidate Resume: {parsed}
        Job Listing: Title: {job.title}, Company: {job.company}, Desc: {job.description}
        """
        
        response = model.generate_content(prompt)
        text = response.text.strip().split("\n\n")
        
        # Build answers array
        if len(text) >= 3:
            answers[0]["answer"] = text[0].replace("1.", "").strip()
            answers[1]["answer"] = text[1].replace("2.", "").strip()
            # Replace target salary or add project answer
            answers.append({
                "question": "Tell us about a relevant project you completed.",
                "answer": text[2].replace("3.", "").strip()
            })
    except Exception as e:
        logger.error(f"Failed to generate AI assisted apply responses: {str(e)}")
        
    return {
        "name": name, "email": email, "phone": phone, "linkedin": linkedin, "github": github,
        "skills": skills, "answers": answers
    }
