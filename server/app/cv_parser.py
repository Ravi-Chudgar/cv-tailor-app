"""
CV Parser - Extract information from PDF and DOCX CV files
Parses CV files and extracts: name, email, phone, location, skills, experience, education, etc.
"""

import PyPDF2
from docx import Document
import re
from typing import Dict, List, Optional
import os


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from DOCX file"""
    try:
        doc = Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Failed to read DOCX: {str(e)}")


def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF or DOCX file"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")


def extract_email(text: str) -> Optional[str]:
    """Extract email address from text"""
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return emails[0] if emails else None


def extract_phone(text: str) -> Optional[str]:
    """Extract phone number from text"""
    phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', text)
    return phones[0] if phones else None


def extract_name(text: str) -> Optional[str]:
    """Extract name from text (usually first line or before email)"""
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and len(line) < 100 and not any(char.isdigit() for char in line[:20]):
            # Filter out lines with emails, phone numbers, or URLs
            if '@' not in line and 'http' not in line.lower():
                return line
    return None


def extract_location(text: str) -> Optional[str]:
    """Extract location/city from text"""
    # Common location patterns
    location_patterns = [
        r'(?:Location|City|Based in)[:\s]+([^,\n]+)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),?\s+([A-Z]{2})',  # City, State
    ]
    
    for pattern in location_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            return matches.group(1)
    
    return None


def extract_skills(text: str) -> List[str]:
    """Extract skills from text"""
    # Look for skills section
    skills_section = None
    
    # Find skills section
    skills_pattern = r'(?:skills?|competencies?)[:\n]+([^n][^\n]*(?:\n[^\n]*)*?)(?:\n\n|\n[A-Z]|$)'
    match = re.search(skills_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        skills_section = match.group(1)
    else:
        # If no explicit section, try to find common skills mentioned
        skills_section = text
    
    # Common technical skills to look for
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
        'FastAPI', 'Django', 'Flask', 'Spring', 'React', 'Angular', 'Vue',
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Firebase',
        'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
        'Git', 'Linux', 'REST', 'API', 'Microservices', 'Machine Learning',
        'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn',
        'HTML', 'CSS', 'XML', 'JSON', 'YAML',
        'Agile', 'SCRUM', 'CI/CD', 'Jenkins', 'GitHub', 'GitLab',
        'Testing', 'Unit Testing', 'Integration Testing', 'Pytest', 'JUnit'
    ]
    
    found_skills = []
    for skill in common_skills:
        if re.search(r'\b' + skill.lower() + r'\b', skills_section.lower()):
            found_skills.append(skill)
    
    return found_skills


def extract_experience(text: str) -> List[Dict]:
    """Extract work experience from text"""
    experiences = []
    
    # Pattern to find job entries
    # Look for: [Job Title] at [Company] | [Company], [Location]
    experience_pattern = r'(?:^|\n)([A-Z][^\n]{0,80})\n([^,\n]{2,60})[,.\n]'
    
    matches = re.finditer(experience_pattern, text, re.MULTILINE)
    
    for match in matches:
        job_title = match.group(1).strip()
        company = match.group(2).strip()
        
        # Filter to likely actual job titles
        if len(job_title) < 80 and any(keyword in job_title.lower() for keyword in 
                                       ['developer', 'engineer', 'manager', 'analyst', 'architect', 
                                        'specialist', 'lead', 'senior', 'junior', 'associate']):
            experiences.append({
                'title': job_title,
                'company': company,
                'description': 'Professional experience in this role'
            })
    
    return experiences[:5]  # Return top 5 experiences


def extract_education(text: str) -> List[Dict]:
    """Extract education from text"""
    educations = []
    
    # Patterns for education
    education_pattern = r'(?:Bachelor|Master|PhD|B\.?S\.?|M\.?S\.?|B\.?A\.?|M\.?A\.?)[^\n]{0,150}'
    
    matches = re.finditer(education_pattern, text, re.IGNORECASE)
    
    for match in matches:
        education = match.group(0).strip()
        if education and len(education) < 150:
            educations.append({
                'degree': education,
                'field': 'Computer Science or Related Field'
            })
    
    return educations[:3]  # Return top 3 educations


def parse_cv(file_path: str) -> Dict:
    """
    Parse CV file and extract all information
    Returns structured data with: name, email, phone, location, skills, experience, education
    """
    try:
        # Extract text from file
        text = extract_text_from_file(file_path)
        
        if not text or not text.strip():
            raise ValueError("CV file appears to be empty or unreadable")
        
        # Parse information
        parsed_data = {
            'raw_text': text,
            'name': extract_name(text),
            'email': extract_email(text),
            'phone': extract_phone(text),
            'location': extract_location(text),
            'skills': extract_skills(text),
            'experience': extract_experience(text),
            'education': extract_education(text),
            'summary': extract_summary(text)
        }
        
        return parsed_data
    
    except Exception as e:
        raise Exception(f"CV parsing failed: {str(e)}")


def extract_summary(text: str) -> Optional[str]:
    """Extract professional summary from text"""
    # Look for summary/objective section
    summary_pattern = r'(?:professional\s+summary|objective|about)[:\s]+([^\n]+(?:\n[^\n]+){0,2})'
    
    match = re.search(summary_pattern, text, re.IGNORECASE)
    
    if match:
        summary = match.group(1).strip()
        # Clean up
        summary = re.sub(r'\s+', ' ', summary)
        if len(summary) > 500:
            summary = summary[:500] + "..."
        return summary
    
    return None


def _join_continuation_lines(lines: list) -> list:
    """
    Join continuation lines into proper paragraphs.
    PDF/DOCX extraction often breaks paragraphs at page-width boundaries.
    This detects and merges those broken lines.
    """
    result = []
    current_para = []

    # Patterns that indicate a line is a "start" (not a continuation)
    start_patterns = re.compile(
        r'^(\•|\-\s|\*\s|Module:|Dissertation:|Project:)', re.IGNORECASE
    )
    # Job/title lines with pipe and dates
    job_pattern = re.compile(r'\|.*\d{4}')

    for raw_line in lines:
        stripped = raw_line.strip()

        if not stripped:
            # Empty line = paragraph break
            if current_para:
                result.append(' '.join(current_para))
                current_para = []
            continue

        is_start = (
            start_patterns.match(stripped) or
            job_pattern.search(stripped) or
            (stripped.startswith('•')) or
            (stripped.startswith('- '))
        )

        if is_start:
            # Flush any accumulated paragraph
            if current_para:
                result.append(' '.join(current_para))
                current_para = []
            # Start new accumulation for this line (bullet/title might also wrap)
            current_para = [stripped]
        else:
            # Check if previous line was a bullet/title that this continues
            if current_para:
                # If the current accumulated text ends mid-word or mid-sentence, join
                current_para.append(stripped)
            else:
                current_para = [stripped]

    if current_para:
        result.append(' '.join(current_para))

    # Clean up: fix spaces before punctuation, double spaces
    cleaned = []
    for line in result:
        line = re.sub(r'\s+', ' ', line)           # collapse multiple spaces
        line = re.sub(r'\s+([.,;:!?])', r'\1', line)  # remove space before punctuation
        line = re.sub(r'\s*-\s*\s', '- ', line)    # fix broken hyphens
        cleaned.append(line.strip())

    return cleaned


def _parse_sections_from_raw(raw_text: str) -> Dict[str, str]:
    """Parse raw CV text into named sections by detecting ALL-CAPS headers"""
    known_headers = [
        'PROFILE SUMMARY', 'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE',
        'TECHNICAL SKILLS', 'CORE COMPETENCIES', 'SKILLS', 'KEY SKILLS',
        'EDUCATION',
        'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EXPERIENCE', 'EMPLOYMENT',
        'CERTIFICATES AND TRAINING', 'CERTIFICATIONS', 'CERTIFICATES',
        'CERTIFICATIONS & ACHIEVEMENTS', 'CERTIFICATES AND TRANING',
        'PROJECTS', 'KEY PROJECTS', 'TECHNICAL PROJECTS',
        'HIGHLIGHT', 'HIGHLIGHTS', 'KEY ACHIEVEMENTS',
        'ADDITIONAL INFORMATION', 'ADDITIONAL',
    ]

    sections = {}
    current_section = None
    current_content = []

    for line in raw_text.split('\n'):
        stripped = line.strip()
        upper = stripped.upper()

        # Check if this line is a section header
        matched_header = None
        for header in known_headers:
            if upper == header or upper == header.replace('&', '&'):
                matched_header = header
                break

        if matched_header:
            if current_section is not None:
                sections[current_section] = '\n'.join(current_content)
            current_section = matched_header
            current_content = []
        elif current_section is not None:
            current_content.append(line)

    if current_section is not None:
        sections[current_section] = '\n'.join(current_content)

    return sections


def _limit_bullets_per_block(lines: list, max_bullets: int = 3) -> list:
    """Limit bullet points per job/project block to keep CV concise for one-page format."""
    result = []
    bullet_count = 0
    in_block = False

    for line in lines:
        is_bullet = line.startswith(('•', '- ', '* '))
        # Job/project title lines (contain | with dates, or are non-bullet non-empty)
        is_title = ('|' in line and re.search(r'\d{4}', line)) or \
                   (not is_bullet and line.strip() and '(' in line and ')' in line)

        if is_title:
            bullet_count = 0
            in_block = True
            result.append(line)
        elif is_bullet:
            bullet_count += 1
            if bullet_count <= max_bullets:
                result.append(line)
        else:
            result.append(line)

    return result


def _trim_summary(lines: list, max_sentences: int = 3) -> list:
    """Trim profile summary to a maximum number of sentences."""
    full_text = ' '.join(lines)
    sentences = re.split(r'(?<=[.!?])\s+', full_text)
    trimmed = ' '.join(sentences[:max_sentences])
    if trimmed and not trimmed.endswith('.'):
        trimmed += '.'
    return [trimmed] if trimmed.strip() else lines


def create_professional_cv(parsed_data: Dict, job_description: str = "") -> str:
    """
    Create a professional CV from parsed data.
    Preserves the original content structure from the uploaded CV.
    """
    raw_text = parsed_data.get('raw_text', '')

    # Extract header info
    name = parsed_data.get('name') or ''
    email = parsed_data.get('email') or ''
    phone = parsed_data.get('phone') or ''

    if not name:
        name = 'PROFESSIONAL'
    name = name.strip().upper()

    # Build contact line
    contact_parts = []
    raw_upper = raw_text[:600].upper() if raw_text else ''
    # Use location override if provided, otherwise detect from text
    location_override = parsed_data.get('location', '').strip()
    if location_override:
        contact_parts.append(location_override)
    else:
        first_lines = raw_text[:300] if raw_text else ''
        if re.search(r'\bUK\b', first_lines):
            contact_parts.append('UK')
        elif re.search(r'\bIndia\b', first_lines, re.IGNORECASE):
            contact_parts.append('India')
        elif re.search(r'\bLondon\b', first_lines, re.IGNORECASE):
            contact_parts.append('London')
        elif re.search(r'\bUSA?\b', first_lines):
            contact_parts.append('USA')
    if email:
        contact_parts.append(email)
    if phone:
        contact_parts.append(phone)
    # Check for LinkedIn
    linkedin_match = re.search(r'(https?://[^\s]*linkedin[^\s]*)', raw_text or '')
    if linkedin_match:
        contact_parts.append(linkedin_match.group(1))

    contact_line = '    |    '.join(contact_parts) if contact_parts else ''

    # If we have usable raw text, parse sections from it
    if raw_text and len(raw_text.strip()) > 100:
        sections = _parse_sections_from_raw(raw_text)
    else:
        sections = {}

    cv = f"{name}\n"
    if contact_line:
        cv += f"{contact_line}\n"
    cv += "\n"

    # Desired section order with aliases
    section_order = [
        ('PROFILE SUMMARY', ['PROFILE SUMMARY', 'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE']),
        ('TECHNICAL SKILLS', ['TECHNICAL SKILLS', 'CORE COMPETENCIES', 'SKILLS', 'KEY SKILLS']),
        ('EDUCATION', ['EDUCATION']),
        ('PROFESSIONAL EXPERIENCE', ['PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EXPERIENCE', 'EMPLOYMENT']),
        ('CERTIFICATES AND TRAINING', ['CERTIFICATES AND TRAINING', 'CERTIFICATES AND TRANING', 'CERTIFICATIONS', 'CERTIFICATES', 'CERTIFICATIONS & ACHIEVEMENTS']),
        ('PROJECTS', ['PROJECTS', 'KEY PROJECTS', 'TECHNICAL PROJECTS']),
        ('HIGHLIGHT', ['HIGHLIGHT', 'HIGHLIGHTS', 'KEY ACHIEVEMENTS', 'ADDITIONAL INFORMATION']),
    ]

    for display_name, aliases in section_order:
        content = None
        for alias in aliases:
            if alias in sections:
                content = sections[alias]
                break

        if content and content.strip():
            # Clean up the content - remove leading/trailing blank lines
            content_lines = content.split('\n')
            # Remove leading empty lines
            while content_lines and not content_lines[0].strip():
                content_lines.pop(0)
            # Remove trailing empty lines
            while content_lines and not content_lines[-1].strip():
                content_lines.pop()

            if content_lines:
                # Join continuation lines into proper paragraphs
                cleaned = _join_continuation_lines(content_lines)

                # --- ONE-PAGE ATS OPTIMIZATION ---
                # Keep all relevant experience, only trim non-essential sections slightly
                if display_name == 'PROJECTS':
                    cleaned = _limit_bullets_per_block(cleaned, max_bullets=3)
                elif display_name in ('HIGHLIGHT', 'HIGHLIGHTS', 'KEY ACHIEVEMENTS'):
                    # Limit highlights to 5 bullets
                    bullet_count = 0
                    trimmed = []
                    for ln in cleaned:
                        if ln.startswith(('•', '- ', '* ')):
                            bullet_count += 1
                            if bullet_count > 5:
                                continue
                        trimmed.append(ln)
                    cleaned = trimmed

                cv += f"{display_name}\n"
                cv += '\n'.join(cleaned) + "\n\n"

    # If no sections were found from raw text, build from parsed fields
    if not sections:
        cv = _build_cv_from_fields(parsed_data, job_description, name, contact_line)

    return cv.strip()


def _build_cv_from_fields(parsed_data: Dict, job_description: str, name: str = "", contact_line: str = "") -> str:
    """Fallback: build CV from individually parsed fields when raw text sections can't be found"""
    if not name:
        name = (parsed_data.get('name') or 'PROFESSIONAL').strip().upper()
    email = parsed_data.get('email') or ''
    phone = parsed_data.get('phone') or ''
    skills = parsed_data.get('skills') or []
    experience = parsed_data.get('experience') or []
    education = parsed_data.get('education') or []
    summary = parsed_data.get('summary') or ''

    cv = f"{name}\n"
    if contact_line:
        cv += f"{contact_line}\n"
    elif email or phone:
        cv += f"{email}    {phone}\n"
    cv += "\n"

    if summary:
        cv += f"PROFILE SUMMARY\n{summary.strip()}\n\n"

    if skills:
        cv += "TECHNICAL SKILLS\n"
        languages = [s for s in skills if s.lower() in ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'typescript']]
        frameworks = [s for s in skills if any(fw in s.lower() for fw in ['fastapi', 'django', 'flask', 'react', 'vue', 'angular', 'spring'])]
        databases = [s for s in skills if any(db in s.lower() for db in ['sql', 'postgresql', 'mysql', 'mongodb', 'redis'])]
        tools_other = [s for s in skills if s not in languages + frameworks + databases]
        if languages:
            cv += f"• Languages: {', '.join(languages)}\n"
        if frameworks:
            cv += f"• Frameworks & Libraries: {', '.join(frameworks)}\n"
        if databases:
            cv += f"• Databases & Data Tools: {', '.join(databases)}\n"
        if tools_other:
            cv += f"• Tools & Technologies: {', '.join(tools_other[:10])}\n"
        cv += "\n"

    if experience:
        cv += "PROFESSIONAL EXPERIENCE\n"
        for exp in experience:
            title = exp.get('title', '').strip()
            company = exp.get('company', '').strip()
            if title:
                cv += f"{title} | {company}\n"
                desc = exp.get('description', '').strip()
                if desc:
                    for bullet in desc.split('\n'):
                        bullet = bullet.strip().lstrip('•-* ')
                        if bullet:
                            cv += f"• {bullet}\n"
                cv += "\n"

    if education:
        cv += "EDUCATION\n"
        for edu in education:
            degree = edu.get('degree', '').strip()
            if degree:
                cv += f"• {degree}\n"
        cv += "\n"

    return cv
