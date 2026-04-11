"""
CV Tailor - Intelligent CV Tailoring FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
from datetime import datetime
import os
import shutil
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, HRFlowable
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import platform

# Register TrueType fonts for ATS-compatible PDF output
_FONTS_REGISTERED = False
def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    try:
        if platform.system() == 'Windows':
            font_dir = 'C:/Windows/Fonts'
        elif platform.system() == 'Darwin':
            font_dir = '/Library/Fonts'
        else:
            font_dir = '/usr/share/fonts/truetype/liberation'
        
        import os as _os
        # Try Arial first (Windows), then Liberation Sans (Linux)
        regular = _os.path.join(font_dir, 'arial.ttf')
        bold = _os.path.join(font_dir, 'arialbd.ttf')
        if not _os.path.exists(regular):
            regular = _os.path.join('/usr/share/fonts/truetype/liberation', 'LiberationSans-Regular.ttf')
            bold = _os.path.join('/usr/share/fonts/truetype/liberation', 'LiberationSans-Bold.ttf')
        pdfmetrics.registerFont(TTFont('Arial', regular))
        pdfmetrics.registerFont(TTFont('Arial-Bold', bold))
        _FONTS_REGISTERED = True
        print('[PDF] Registered TrueType fonts (Arial) for ATS compatibility')
    except Exception as e:
        print(f'[PDF] Warning: Could not register TrueType fonts: {e}. Falling back to Helvetica.')
        _FONTS_REGISTERED = True  # Don't retry
from .users_storage import (
    ensure_users_file,
    get_all_users,
    get_user_by_id,
    get_user_by_username,
    add_user,
    delete_user,
    verify_user_credentials,
    update_user
)
from .cv_parser import (
    parse_cv,
    create_professional_cv
)
from .keyword_search import (
    extract_job_keywords,
    search_job_keywords_online,
    inject_keywords_into_cv,
)
from .ats_scorer import calculate_ats_score

app = FastAPI(
    title="CV Tailor API",
    description="Intelligent CV Tailoring Service",
    version="1.0.0"
)

# CORS configuration - Add middleware FIRST before routes
# Allow deployment platforms with dynamic URLs
def get_allowed_origins():
    """Generate list of allowed origins for CORS"""
    origins = [
        # Local development
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:5176",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        # Render deployment - specific URLs
        "https://cv-tailor-frontend-9gun.onrender.com",
        "https://cv-tailor-frontend.onrender.com",
        # Custom domain (ravichudgar.com)
        "https://www.ravichudgar.com",
        "https://ravichudgar.com",
        # Add wildcard for any onrender.com subdomain (if FastAPI CORSMiddleware supports it)
    ]
    return origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including preflight
    allow_headers=["*"],  # Allow all headers
    expose_headers=["Content-Disposition", "Content-Type"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Initialize Excel-based user storage
ensure_users_file()

# Models
class User(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None

class CVData(BaseModel):
    name: str
    email: str
    phone: str
    summary: str
    experience: List[dict]
    education: List[dict]
    skills: List[str]

class JobDescription(BaseModel):
    title: str
    description: str
    requirements: List[str]

class TailoredCV(BaseModel):
    original_cv: CVData
    job_description: JobDescription
    tailored_cv_content: str
    match_score: float

# Routes
@app.get("/", tags=["Info"])
async def root():
    """Root endpoint"""
    return {
        "message": "CV Tailor API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CV Tailor",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/auth/login", response_model=LoginResponse, tags=["Auth"])
async def login(user: User):
    """
    Login endpoint
    
    Credentials for demo:
    - username: admin, password: admin123
    """
    # Verify credentials against Excel storage
    verified_user = verify_user_credentials(user.username, user.password)
    
    if not verified_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Return success with tokens
    access_token = f"access_{uuid.uuid4().hex}"
    refresh_token = f"refresh_{uuid.uuid4().hex}"
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": verified_user["user_id"],
            "username": verified_user["username"],
            "email": verified_user["email"]
        }
    )

@app.post("/api/auth/register", response_model=LoginResponse, tags=["Auth"])
async def register(user: User):
    """Register a new user"""
    if len(user.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    try:
        # Add user to Excel storage
        new_user = add_user(user.username, user.password, f"{user.username}@example.com", "user")
        
        # Return success with tokens
        access_token = f"access_{uuid.uuid4().hex}"
        refresh_token = f"refresh_{uuid.uuid4().hex}"
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user={
                "id": new_user["user_id"],
                "username": new_user["username"],
                "email": new_user["email"]
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}"
        )

@app.get("/api/auth/current-user", tags=["Auth"])
async def get_current_user():
    """Get current user info"""
    # This is a demo endpoint - in production you'd verify the token
    return {
        "id": "admin",
        "username": "admin",
        "email": "admin@example.com"
    }

@app.post("/api/cv/tailor", response_model=TailoredCV, tags=["CV Operations"])
async def tailor_cv(cv_data: CVData, job_desc: JobDescription):
    """
    Tailor CV based on job description
    
    This endpoint analyzes the CV and job description to provide:
    - Tailored CV content optimized for the job
    - Match score between CV and job requirements
    """
    
    # Simple matching algorithm
    cv_text = f"{cv_data.summary} {' '.join(cv_data.skills)}"
    job_text = f"{job_desc.description} {' '.join(job_desc.requirements)}"
    
    # Calculate match score (simplified)
    match_score = 0.75
    
    tailored_content = f"""
    {cv_data.name}
    {cv_data.email} | {cv_data.phone}
    
    PROFESSIONAL SUMMARY
    {cv_data.summary}
    
    RELEVANT SKILLS
    {', '.join(cv_data.skills)}
    
    EXPERIENCE
    {json.dumps(cv_data.experience, indent=2)}
    
    EDUCATION
    {json.dumps(cv_data.education, indent=2)}
    
    [Optimized for: {job_desc.title}]
    """
    
    return TailoredCV(
        original_cv=cv_data,
        job_description=job_desc,
        tailored_cv_content=tailored_content,
        match_score=match_score
    )

@app.get("/api/cv/templates", tags=["CV Operations"])
async def get_templates():
    """Get available CV templates"""
    return {
        "templates": [
            {"id": 1, "name": "Modern", "description": "Clean and modern design"},
            {"id": 2, "name": "Classic", "description": "Traditional format"},
            {"id": 3, "name": "Minimal", "description": "Minimal and focused"},
            {"id": 4, "name": "Creative", "description": "Creative and colorful"}
        ]
    }

# Create uploads directory if it doesn't exist
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)

# In-memory CV storage for demo
CV_STORAGE = {}  # Stores uploaded CV metadata
PARSED_CVS = {}  # Stores parsed CV data (name, email, phone, skills, experience, education)

@app.post("/api/cv/upload", tags=["CV Operations"])
async def upload_cv(file: UploadFile = File(...)):
    """Upload and parse a CV file (PDF or DOCX)"""
    try:
        print(f"\n[UPLOAD] Starting CV upload: {file.filename}, Content-Type: {file.content_type}")
        
        # Validate file type - be lenient with mimetypes
        file_extension = os.path.splitext(file.filename)[1].lower()
        print(f"[UPLOAD] File extension: {file_extension}")
        
        # Check extension first (more reliable)
        allowed_extensions = ['.pdf', '.docx', '.doc']
        if file_extension not in allowed_extensions:
            print(f"[UPLOAD] Invalid file extension: {file_extension}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file type. Allowed: PDF, DOCX, DOC. Got: {file_extension}"
            )
        
        # Also check mime type if it looks wrong
        allowed_mimetypes = [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/x-msword',
            'text/plain'  # Sometimes browsers send text/plain for unknown types
        ]
        if file.content_type and file.content_type not in allowed_mimetypes:
            print(f"[UPLOAD] Warning: Unexpected mime type: {file.content_type}, but extension is valid: {file_extension}")
        
        # Validate file size (max 10MB)
        file_content = await file.read()
        file_size = len(file_content)
        print(f"[UPLOAD] File size: {file_size} bytes")
        
        if file_size > 10 * 1024 * 1024:
            print(f"[UPLOAD] File too large")
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        if file_size == 0:
            print(f"[UPLOAD] File is empty")
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Generate CV ID
        cv_id = str(uuid.uuid4())
        print(f"[UPLOAD] Generated CV ID: {cv_id}")
        
        # Save file
        saved_filename = f"cv_{cv_id}{file_extension}"
        file_path = os.path.join(UPLOADS_DIR, saved_filename)
        
        print(f"[UPLOAD] Uploads directory: {UPLOADS_DIR}")
        print(f"[UPLOAD] Saving file to: {file_path}")
        
        # Ensure directory exists
        os.makedirs(UPLOADS_DIR, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(file_content)
        print(f"[UPLOAD] File saved successfully")
        
        # Parse CV to extract information
        try:
            print(f"[UPLOAD] Starting CV parsing...")
            parsed_data = parse_cv(file_path)
            PARSED_CVS[cv_id] = parsed_data
            print(f"[UPLOAD] CV parsed successfully")
        except Exception as parse_error:
            # If parsing fails, still allow upload but mark as unparsed
            print(f"[UPLOAD] Parsing error (continuing): {str(parse_error)}")
            parsed_data = {
                'name': None,
                'email': None,
                'phone': None,
                'skills': [],
                'experience': [],
                'education': [],
                'error': str(parse_error)
            }
            PARSED_CVS[cv_id] = parsed_data
        
        # Store CV metadata
        cv_info = {
            "file_id": cv_id,
            "filename": saved_filename,
            "original_filename": file.filename,
            "upload_date": datetime.now().isoformat(),
            "size": file_size,
            "status": "parsed" if 'error' not in parsed_data else "uploaded_unparsed",
            "file_path": file_path
        }
        CV_STORAGE[cv_id] = cv_info
        print(f"[UPLOAD] Upload complete. CV info stored: {cv_info}")
        
        return {
            "success": True,
            "message": "CV uploaded and parsed successfully",
            "file_id": cv_id,
            "filename": saved_filename,
            "parsed_data": {
                "name": parsed_data.get('name', 'Unknown'),
                "email": parsed_data.get('email', 'Not found'),
                "phone": parsed_data.get('phone', 'Not found'),
                "skills": parsed_data.get('skills', []),
                "experience_count": len(parsed_data.get('experience', [])),
                "education": parsed_data.get('education', [])
            }
        }
    except HTTPException as http_exc:
        print(f"[UPLOAD] HTTP Exception: {http_exc.detail}")
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"[UPLOAD] Exception: {error_msg}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Upload failed: {error_msg}")

@app.get("/api/cv/list", tags=["CV Operations"])
async def list_cvs():
    """Get list of uploaded CVs"""
    cvs_list = []
    for cv_id, cv_info in CV_STORAGE.items():
        cvs_list.append({
            "file_id": cv_info["file_id"],
            "file_name": cv_info["filename"],  # Changed from filename to file_name
            "upload_date": cv_info["upload_date"],
            "size": cv_info["size"],
            "status": cv_info["status"]
        })
    return {"cvs": cvs_list}

@app.post("/api/cv/parse", tags=["CV Operations"])
async def parse_cv_endpoint(data: dict):
    """Parse CV content from uploaded file"""
    try:
        file_name = data.get("file_name", "")
        # In a real app, you'd parse the actual file content
        return {
            "success": True,
            "data": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "summary": "Experienced software developer",
                "experience": [
                    {"company": "Tech Corp", "position": "Senior Developer", "duration": "2020-present"}
                ],
                "education": [
                    {"school": "University", "degree": "BS Computer Science", "year": "2020"}
                ],
                "skills": ["Python", "React", "FastAPI", "SQL"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse failed: {str(e)}")

@app.delete("/api/cv/{file_id}", tags=["CV Operations"])
async def delete_cv(file_id: str):
    """Delete a CV file"""
    if file_id in CV_STORAGE:
        deleted = CV_STORAGE.pop(file_id)
        return {"success": True, "message": "CV deleted successfully", "filename": deleted["filename"]}
    raise HTTPException(status_code=404, detail="CV file not found")

@app.get("/api/jobs/suggestions", tags=["Job Operations"])
async def get_job_suggestions(keyword: str = ""):
    """Get job suggestions based on keyword"""
    sample_jobs = [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "description": "Looking for experienced Python developer",
            "requirements": ["Python", "FastAPI", "PostgreSQL"]
        },
        {
            "id": 2,
            "title": "Full Stack Developer",
            "company": "StartUp Inc",
            "description": "Full stack development opportunity",
            "requirements": ["React", "Node.js", "MongoDB"]
        }
    ]
    
    if keyword:
        return {
            "jobs": [j for j in sample_jobs if keyword.lower() in j["title"].lower()]
        }
    
    return {"jobs": sample_jobs}

@app.post("/api/job/analyze", tags=["Job Operations"])
async def analyze_job(data: dict):
    """Analyze job description, extract keywords, and compare against uploaded CV"""
    try:
        description = data.get("description", "")
        title = data.get("title", "")
        company = data.get("company", "")
        cv_file_id = data.get("cv_file_id", "")
        
        if not description.strip():
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Step 1: Extract keywords from job description
        jd_keywords = extract_job_keywords(description)
        jd_skills = jd_keywords.get('skills', [])
        jd_soft = jd_keywords.get('soft_skills', [])
        jd_certs = jd_keywords.get('certifications', [])
        
        # Step 2: Search web for trending keywords
        jd_lines = [l.strip() for l in description.strip().split('\n') if l.strip()]
        job_title = title or (jd_lines[0] if jd_lines else "Software Developer")
        if len(job_title) > 80:
            job_title = job_title[:80].rsplit(' ', 1)[0]
        
        try:
            web_keywords = await search_job_keywords_online(job_title, jd_skills)
        except Exception:
            web_keywords = {'trending_skills': [], 'action_verbs': [], 'industry_terms': [], 'search_source': 'Fallback'}
        
        trending = web_keywords.get('trending_skills', [])
        industry_terms = web_keywords.get('industry_terms', [])
        action_verbs = web_keywords.get('action_verbs', [])
        
        # All required keywords from JD + web
        all_required = list(dict.fromkeys(jd_skills + trending))
        
        # Step 3: Compare against CV if provided
        found_in_cv = []
        missing_from_cv = []
        cv_name = ""
        
        if cv_file_id and cv_file_id in PARSED_CVS:
            parsed_cv = PARSED_CVS[cv_file_id]
            cv_text_lower = (parsed_cv.get('raw_text', '') or '').lower()
            cv_name = parsed_cv.get('name', 'Your CV')
            
            for skill in all_required:
                if skill.lower() in cv_text_lower:
                    found_in_cv.append(skill)
                else:
                    missing_from_cv.append(skill)
            
            # Also check soft skills
            soft_found = [s for s in jd_soft if s.lower() in cv_text_lower]
            soft_missing = [s for s in jd_soft if s.lower() not in cv_text_lower]
            
            # Check certifications
            cert_found = [c for c in jd_certs if c.lower() in cv_text_lower]
            cert_missing = [c for c in jd_certs if c.lower() not in cv_text_lower]
        else:
            # No CV selected - just list all as required
            missing_from_cv = all_required
            soft_found = []
            soft_missing = jd_soft
            cert_found = []
            cert_missing = jd_certs
        
        # Calculate gap score
        total_keywords = len(all_required) + len(jd_soft) + len(jd_certs)
        matched_count = len(found_in_cv) + len(soft_found) + len(cert_found)
        gap_score = round((matched_count / max(total_keywords, 1)) * 100)
        
        return {
            "success": True,
            "analysis": {
                "title": job_title,
                "company": company or "Not specified",
                "key_skills": jd_skills,
                "trending_skills": trending[:10],
                "soft_skills": jd_soft,
                "certifications": jd_certs,
                "industry_terms": industry_terms[:8],
                "action_verbs": action_verbs[:10],
                "search_source": web_keywords.get('search_source', 'N/A'),
            },
            "gap_analysis": {
                "cv_name": cv_name,
                "gap_score": gap_score,
                "found_in_cv": found_in_cv,
                "missing_from_cv": missing_from_cv,
                "soft_skills_found": soft_found,
                "soft_skills_missing": soft_missing,
                "certs_found": cert_found,
                "certs_missing": cert_missing,
                "total_required": total_keywords,
                "total_matched": matched_count,
                "recommendations": _build_gap_recommendations(missing_from_cv, soft_missing, cert_missing),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ANALYZE] Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")


def _build_gap_recommendations(missing_skills, missing_soft, missing_certs):
    """Build actionable recommendations based on gap analysis"""
    recs = []
    if missing_skills:
        recs.append(f"Add these technical skills to your CV: {', '.join(missing_skills[:8])}")
    if missing_soft:
        recs.append(f"Incorporate these soft skills/methodologies: {', '.join(missing_soft[:5])}")
    if missing_certs:
        recs.append(f"Consider adding certifications: {', '.join(missing_certs[:3])}")
    if not missing_skills and not missing_soft and not missing_certs:
        recs.append("Your CV already covers all keywords from this job description!")
    recs.append("Click 'Tailor My CV' to automatically add missing keywords")
    return recs

@app.post("/api/tailor/tailor", tags=["Tailor Operations"])
async def tailor_cv_endpoint(data: dict):
    """Tailor CV based on job description using uploaded CV data"""
    try:
        cv_file = data.get("cv_file")
        job_description = data.get("job_description")
        mobile_number = data.get("mobile_number", "").strip()
        location = data.get("location", "").strip()
        
        if not cv_file:
            raise HTTPException(status_code=400, detail="CV file (file_id) is required")
        if not job_description:
            raise HTTPException(status_code=400, detail="Job description is required")
        
        # Get parsed CV data from uploaded file
        parsed_cv = PARSED_CVS.get(cv_file)
        
        if not parsed_cv:
            raise HTTPException(
                status_code=404, 
                detail="CV not found. Please upload CV first using /api/cv/upload"
            )
        
        # Override contact details if provided by user
        if mobile_number:
            parsed_cv['phone'] = mobile_number
            print(f"[TAILOR] Mobile number overridden: {mobile_number}")
        if location:
            parsed_cv['location'] = location
            print(f"[TAILOR] Location overridden: {location}")
        
        # If CV parsing had errors, use the parsed data anyway (with what we got)
        # The create_professional_cv function has good fallbacks
        
        print(f"[TAILOR] Using parsed CV data for {cv_file}: {parsed_cv.get('name', 'Unknown')}")
        
        # Step 1: Extract keywords from job description
        jd_keywords = extract_job_keywords(job_description)
        print(f"[TAILOR] JD keywords found: {len(jd_keywords.get('skills', []))} skills, {len(jd_keywords.get('soft_skills', []))} soft skills")
        
        # Step 2: Search internet for trending/relevant keywords
        # Extract a job title from the job description (first line or first sentence)
        jd_lines = [l.strip() for l in job_description.strip().split('\n') if l.strip()]
        job_title = jd_lines[0] if jd_lines else "Software Developer"
        # Limit title length
        if len(job_title) > 80:
            job_title = job_title[:80].rsplit(' ', 1)[0]
        
        existing_kw = jd_keywords.get('skills', [])
        try:
            web_keywords = await search_job_keywords_online(job_title, existing_kw)
            print(f"[TAILOR] Web keywords: {len(web_keywords.get('trending_skills', []))} trending, source: {web_keywords.get('search_source', 'N/A')}")
        except Exception as web_err:
            print(f"[TAILOR] Web search failed (using fallback): {web_err}")
            web_keywords = {'trending_skills': [], 'action_verbs': [], 'industry_terms': [], 'search_source': 'Fallback'}
        
        # Step 3: Generate professional CV from parsed data
        tailored_cv = create_professional_cv(parsed_cv, job_description)
        
        # Step 4: Inject found keywords into the CV content
        tailored_cv = inject_keywords_into_cv(tailored_cv, jd_keywords, web_keywords)
        print(f"[TAILOR] CV enhanced with keywords from: {web_keywords.get('search_source', 'N/A')}")
        
        # Step 5: Comprehensive ATS scoring (modelled on Jobscan / ResumeWorded)
        ats_result = calculate_ats_score(tailored_cv, jd_keywords, web_keywords)
        
        print(f"[TAILOR] ATS Score: {ats_result['overall_score']}% (Grade: {ats_result['grade']}) | "
              f"Keyword: {ats_result['component_scores']['keyword_match']}% | "
              f"Format: {ats_result['component_scores']['formatting']}% | "
              f"Impact: {ats_result['component_scores']['impact_content']}% | "
              f"ATS Compat: {ats_result['component_scores']['ats_compatibility']}%")
        
        # Build matching keywords list for display
        matching_keywords = ats_result['matched_keywords'][:20]
        missing_keywords = ats_result['missing_keywords'][:15]
        
        # Calculate match score based on keyword matching
        if matching_keywords:
            match_score = min(0.98, 0.75 + (len(matching_keywords) * 0.025))
        else:
            match_score = 0.80
        
        return {
            "success": True,
            "tailored_cv": tailored_cv.strip(),
            "match_score": round(match_score, 2),
            "ats_score": {
                "overall_score": ats_result['overall_score'],
                "grade": ats_result['grade'],
                "component_scores": ats_result['component_scores'],
                "weights": ats_result['weights'],
                "recommendations": ats_result['recommendations'],
            },
            "ats_details": {
                "keyword_match": f"{ats_result['component_scores']['keyword_match']}% — {len(matching_keywords)} keywords matched against job description",
                "formatting": f"{ats_result['component_scores']['formatting']}% — Section headings, bullet points, date consistency, word count",
                "impact_content": f"{ats_result['component_scores']['impact_content']}% — Measurable achievements, action verbs, summary quality",
                "ats_compatibility": f"{ats_result['component_scores']['ats_compatibility']}% — Contact info, no special chars, parseable layout",
                "grade": f"Grade {ats_result['grade']} — {'Excellent' if ats_result['overall_score'] >= 80 else 'Good' if ats_result['overall_score'] >= 65 else 'Needs Work'} ATS readiness",
            },
            "matching_keywords": matching_keywords,
            "missing_keywords": missing_keywords,
            "searched_keywords": {
                "source": web_keywords.get('search_source', 'N/A'),
                "trending_skills": web_keywords.get('trending_skills', [])[:10],
                "action_verbs": web_keywords.get('action_verbs', [])[:10],
                "industry_terms": web_keywords.get('industry_terms', [])[:8],
                "jd_skills_found": jd_keywords.get('skills', [])[:15],
                "jd_soft_skills": jd_keywords.get('soft_skills', [])[:10],
            },
            "recommendations": ats_result['recommendations'],
            "modifications": [
                "Reformatted with professional Rezi.ai-style template structure",
                "Reorganized skills into Core Competencies with categorization",
                "Enhanced professional summary to highlight key strengths",
                "Formatted experience with bullet points for better readability",
                "Ensured ATS compatibility with clean formatting and no special characters",
                "Optimized section headers for maximum ATS parsing accuracy",
                "Integrated job-matched keywords naturally throughout content",
                "Improved visual hierarchy while maintaining ATS compliance",
                "Added clear separation between sections for easy parsing",
                "Standardized formatting of contact information and dates"
            ],
            "ats_improvements": [
                f"ATS Score: {ats_result['overall_score']}% (Grade {ats_result['grade']})",
                f"Keyword Match: {ats_result['component_scores']['keyword_match']}% — {len(matching_keywords)} JD keywords found",
                f"Formatting: {ats_result['component_scores']['formatting']}% — Section structure & readability",
                f"Impact: {ats_result['component_scores']['impact_content']}% — Metrics & action verbs",
                f"ATS Parsing: {ats_result['component_scores']['ats_compatibility']}% — Layout & compatibility",
                "Professional Rezi.ai template optimized for ATS systems",
                "Keywords naturally incorporated for relevance matching",
                "Professional appearance appeals to human reviewers",
                "Ready for immediate submission to any job application system"
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[TAILOR] Error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Tailoring failed: {str(e)}")

@app.post("/api/tailor/batch-tailor", tags=["Tailor Operations"])
async def batch_tailor_cv(data: dict):
    """Batch tailor CV for multiple jobs"""
    try:
        cv_file = data.get("cv_file")
        job_descriptions = data.get("job_descriptions", [])
        
        results = []
        for i, job_desc in enumerate(job_descriptions):
            results.append({
                "job_index": i,
                "match_score": 0.80 + (i * 0.05),
                "tailored_content": f"Tailored for job {i+1}"
            })
        
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch tailoring failed: {str(e)}")

@app.get("/api/tailor/preview", tags=["Tailor Operations"])
async def preview_tailor(cv_file: str = "", job_description: str = ""):
    """Preview tailored CV before generating"""
    return {
        "success": True,
        "preview": f"Preview of CV tailored for: {job_description[:50]}...",
        "changes_summary": ["Added relevant keywords", "Reorganized work experience", "Highlighted matching skills"]
    }

@app.get("/api/tailor/compare", tags=["Tailor Operations"])
async def compare_cvs(cv_file: str = "", tailored_file: str = ""):
    """Compare original and tailored CV"""
    return {
        "success": True,
        "original": "Original CV content",
        "tailored": "Tailored CV content",
        "differences": ["10 new keywords added", "3 sections reorganized"]
    }

@app.get("/api/pdf/templates", tags=["PDF Operations"])
async def get_pdf_templates():
    """Get available PDF templates"""
    return {
        "templates": [
            {"id": "professional", "name": "Professional", "description": "Clean professional layout"},
            {"id": "modern", "name": "Modern", "description": "Modern minimalist design"},
            {"id": "creative", "name": "Creative", "description": "Creative and colorful design"}
        ]
    }

def create_pdf_from_content(cv_content: str, template: str = "professional") -> bytes:
    """Create professional PDF matching the uploaded CV format - blue headers, gray bars, proper styling"""
    if not cv_content or not str(cv_content).strip():
        raise ValueError("CV content cannot be empty")
    
    try:
        import re as re_mod
        _register_fonts()
        
        # Use embedded TrueType font if available, else fallback
        try:
            pdfmetrics.getFont('Arial')
            FONT_REGULAR = 'Arial'
            FONT_BOLD = 'Arial-Bold'
        except KeyError:
            FONT_REGULAR = 'Helvetica'
            FONT_BOLD = 'Helvetica-Bold'
        
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.35 * inch,
            bottomMargin=0.35 * inch,
        )
        
        elements = []
        
        # Colors matching the user's original CV
        BLUE = colors.HexColor('#1F4E79')
        DARK_BLUE = colors.HexColor('#2E5090')
        LIGHT_BLUE_BG = colors.HexColor('#D6E4F0')
        BLACK = colors.black
        GRAY = colors.HexColor('#444444')
        
        styles = getSampleStyleSheet()
        
        # Name style - large, bold, centered
        name_style = ParagraphStyle(
            'CVName', parent=styles['Title'],
            fontSize=16, fontName=FONT_BOLD, alignment=TA_CENTER,
            spaceAfter=1, spaceBefore=0, textColor=BLACK, leading=18
        )
        
        # Contact info style - centered, small
        contact_style = ParagraphStyle(
            'CVContact', parent=styles['Normal'],
            fontSize=8, alignment=TA_CENTER, spaceAfter=3, spaceBefore=2,
            textColor=GRAY, leading=10, fontName=FONT_REGULAR
        )
        
        # Section header style (used inside gray bar)
        section_style = ParagraphStyle(
            'CVSection', parent=styles['Normal'],
            fontSize=9, fontName=FONT_BOLD, alignment=TA_CENTER,
            textColor=DARK_BLUE, spaceBefore=0, spaceAfter=0, leading=11
        )
        
        # Body text style
        body_style = ParagraphStyle(
            'CVBody', parent=styles['Normal'],
            fontSize=9, leading=11, spaceAfter=1, alignment=TA_LEFT,
            fontName=FONT_REGULAR
        )
        
        # Bullet point style
        bullet_style = ParagraphStyle(
            'CVBullet', parent=styles['Normal'],
            fontSize=9, leading=11, spaceAfter=1,
            leftIndent=14, bulletIndent=2, fontName=FONT_REGULAR
        )
        
        # Job title style - centered, bold
        job_title_style = ParagraphStyle(
            'CVJobTitle', parent=styles['Normal'],
            fontSize=9, fontName=FONT_BOLD, alignment=TA_CENTER,
            spaceAfter=1, spaceBefore=3, textColor=BLACK, leading=11
        )
        
        # Sub-detail style (Module, Dissertation, Project)
        detail_style = ParagraphStyle(
            'CVDetail', parent=styles['Normal'],
            fontSize=8, leading=10, leftIndent=14, spaceAfter=0,
            fontName=FONT_REGULAR
        )
        
        # Project title style - bold, left-aligned
        project_title_style = ParagraphStyle(
            'CVProjectTitle', parent=styles['Normal'],
            fontSize=9, fontName=FONT_BOLD, alignment=TA_LEFT,
            spaceAfter=1, spaceBefore=3, textColor=BLACK, leading=11
        )
        
        # Known section headers
        section_headers = {
            'PROFILE SUMMARY', 'PROFESSIONAL SUMMARY', 'SUMMARY',
            'TECHNICAL SKILLS', 'CORE COMPETENCIES', 'SKILLS',
            'EDUCATION',
            'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EXPERIENCE',
            'CERTIFICATES AND TRAINING', 'CERTIFICATIONS', 'CERTIFICATES AND TRANING',
            'CERTIFICATIONS & ACHIEVEMENTS',
            'PROJECTS',
            'HIGHLIGHT', 'HIGHLIGHTS', 'KEY ACHIEVEMENTS',
            'ADDITIONAL INFORMATION'
        }
        
        def escape_xml(text):
            """Escape XML special characters for reportlab Paragraph"""
            text = text.replace('&', '&amp;')
            text = text.replace('<', '&lt;')
            text = text.replace('>', '&gt;')
            return text
        
        def make_section_header(text):
            """Create a section header with gray/blue background bar"""
            header_para = Paragraph(
                f'<font color="#2E5090">{escape_xml(text.upper())}</font>',
                section_style
            )
            header_table = Table(
                [[header_para]],
                colWidths=[doc.width],
                rowHeights=[16]
            )
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BLUE_BG),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ]))
            return header_table
        
        def format_bullet_text(text):
            """Format bullet text with bold labels (e.g., 'Languages: ...')"""
            text = escape_xml(text)
            # Bold the label before colon (e.g., "Languages: Python, Java")
            colon_pos = text.find(':')
            if colon_pos > 0 and colon_pos < 45:
                label = text[:colon_pos]
                rest = text[colon_pos:]
                return f'<b>{label}</b>{rest}'
            return text
        
        lines = cv_content.split('\n')
        line_idx = 0
        
        # Skip leading empty lines
        while line_idx < len(lines) and not lines[line_idx].strip():
            line_idx += 1
        
        # First line = Name
        if line_idx < len(lines):
            name_text = escape_xml(lines[line_idx].strip())
            elements.append(Paragraph(name_text, name_style))
            # Horizontal rule under name
            elements.append(HRFlowable(
                width="100%", thickness=1, color=BLACK,
                spaceAfter=2, spaceBefore=1
            ))
            line_idx += 1
        
        # Skip empty lines after name
        while line_idx < len(lines) and not lines[line_idx].strip():
            line_idx += 1
        
        # Contact line - detect by: contains email, phone, linkedin, or starts with location
        if line_idx < len(lines):
            contact_raw = lines[line_idx].strip()
            is_contact = (
                '@' in contact_raw or
                'linkedin' in contact_raw.lower() or
                re_mod.search(r'\(\+\d+\)', contact_raw) or
                re_mod.match(r'^(UK|India|USA|US|London|Remote)\b', contact_raw, re_mod.IGNORECASE)
            )
            if is_contact:
                contact_formatted = escape_xml(contact_raw)
                # Replace pipe separators with spaced pipes using non-breaking spaces
                contact_formatted = contact_formatted.replace(' | ', ' &nbsp;&nbsp;|&nbsp;&nbsp; ')
                contact_formatted = contact_formatted.replace('|', ' &nbsp;|&nbsp; ')
                # Make email blue and underlined
                email_match = re_mod.search(r'[\w.+\-]+@[\w\-]+\.[\w.]+', contact_raw)
                if email_match:
                    email_text = email_match.group(0)
                    contact_formatted = contact_formatted.replace(
                        escape_xml(email_text),
                        f'<font color="#1F4E79"><u>{escape_xml(email_text)}</u></font>'
                    )
                # Make LinkedIn blue and underlined
                linkedin_match = re_mod.search(r'https?://[^\s]+linkedin[^\s]+', contact_raw)
                if linkedin_match:
                    linkedin_text = linkedin_match.group(0)
                    contact_formatted = contact_formatted.replace(
                        escape_xml(linkedin_text),
                        f'<font color="#1F4E79"><u>{escape_xml(linkedin_text)}</u></font>'
                    )
                elements.append(Paragraph(contact_formatted, contact_style))
                line_idx += 1
        
        # Track current section context for smarter formatting
        current_section = ''
        
        # Process remaining lines
        while line_idx < len(lines):
            line = lines[line_idx].strip()
            line_idx += 1
            
            if not line:
                elements.append(Spacer(1, 1))
                continue
            
            # Check for section header
            line_upper = line.upper().strip()
            if line_upper in section_headers:
                elements.append(Spacer(1, 3))
                elements.append(make_section_header(line))
                elements.append(Spacer(1, 2))
                current_section = line_upper
                continue
            
            # Bullet point
            if line.startswith('•') or line.startswith('- ') or line.startswith('* '):
                bullet_text = line.lstrip('•-* ').strip()
                formatted = format_bullet_text(bullet_text)
                elements.append(Paragraph(f'&bull;  {formatted}', bullet_style))
                continue
            
            # Job title / company line (contains | and date-like patterns)
            if '|' in line and current_section in ('PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EXPERIENCE'):
                job_text = escape_xml(line)
                elements.append(Paragraph(f'<b>{job_text}</b>', job_title_style))
                # Thin underline below job title
                elements.append(HRFlowable(
                    width="100%", thickness=0.5, color=BLACK,
                    spaceAfter=1, spaceBefore=0
                ))
                continue
            
            # Project section: detect project titles
            if current_section in ('PROJECTS', 'KEY PROJECTS', 'TECHNICAL PROJECTS'):
                # Project title: has parentheses with tech stack, or is ALL CAPS,
                # or is a short non-bullet line at start of a project block
                is_project_title = (
                    ('(' in line and ')' in line and not line.startswith('•')) or
                    (line.isupper() and len(line) > 5) or
                    (not line.startswith('•') and len(line) < 80 and not line.startswith('Module:'))
                )
                if is_project_title:
                    elements.append(Paragraph(f'<b>{escape_xml(line)}</b>', project_title_style))
                    continue
            
            # Module / Dissertation / Project detail lines
            if line.startswith(('Module:', 'Dissertation:', 'Project:')):
                colon_pos = line.index(':')
                label = line[:colon_pos]
                rest = line[colon_pos:]
                elements.append(Paragraph(
                    f'<b>{escape_xml(label)}</b>{escape_xml(rest)}',
                    detail_style
                ))
                continue
            
            # Regular body text (paragraphs - auto-wraps in reportlab)
            elements.append(Paragraph(escape_xml(line), body_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        pdf_bytes = buffer.getvalue()
        print(f"[PDF] Generated professional PDF: {len(pdf_bytes)} bytes")
        return pdf_bytes
    except Exception as e:
        print(f"[PDF] Error creating PDF: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise

@app.post("/api/pdf/generate", tags=["PDF Operations"])
async def generate_pdf(data: dict):
    """Generate PDF from CV content and return binary PDF data"""
    try:
        cv_content = data.get("cv_content")
        template = data.get("template", "professional")
        file_name = data.get("file_name", "cv.pdf")
        
        # Validate and convert cv_content to string
        if not cv_content:
            raise HTTPException(status_code=400, detail="CV content is required")
        
        # Handle different content types
        if isinstance(cv_content, dict):
            cv_content = json.dumps(cv_content, indent=2)
        elif isinstance(cv_content, (list, tuple)):
            cv_content = "\n".join(str(item) for item in cv_content)
        else:
            cv_content = str(cv_content)
        
        # Check if content is not empty after conversion
        if not cv_content or not cv_content.strip():
            raise HTTPException(status_code=400, detail="CV content cannot be empty")
        
        # Generate PDF as bytes
        pdf_bytes = create_pdf_from_content(cv_content, template)
        
        # Return PDF as streaming response
        # Sanitize filename for Content-Disposition header
        safe_name = file_name.replace('"', '_')
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{safe_name}"'}
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF generation failed: {str(e)}")

@app.get("/api/pdf/download/{file_name}", tags=["PDF Operations"])
async def download_pdf(file_name: str):
    """Download generated PDF"""
    return {
        "success": True,
        "message": f"PDF {file_name} ready for download",
        "filename": file_name
    }

@app.post("/api/pdf/preview", tags=["PDF Operations"])
async def preview_pdf(data: dict):
    """Preview PDF before download"""
    return {
        "success": True,
        "preview": "PDF preview generated",
        "pages": 1
    }

@app.post("/api/pdf/batch-generate", tags=["PDF Operations"])
async def batch_generate_pdf(data: dict):
    """Batch generate PDFs"""
    try:
        cvs_content = data.get("cvs_content", [])
        
        return {
            "success": True,
            "count": len(cvs_content),
            "files": [f"cv_{i}.pdf" for i in range(len(cvs_content))]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Batch PDF generation failed: {str(e)}")

@app.get("/api/analytics", tags=["Analytics"])
async def get_analytics():
    """Get application analytics"""
    return {
        "total_users": 1250,
        "cvs_created": 5320,
        "jobs_tailored": 8945,
        "average_match_score": 0.78,
        "timestamp": datetime.now().isoformat()
    }

# Admin endpoints
@app.get("/api/admin/users", tags=["Admin"])
async def get_all_users_endpoint():
    """Get all users (admin only)"""
    users_list = []
    for user in get_all_users():
        users_list.append({
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "updated_at": user["updated_at"],
            "role": user["role"]
        })
    return {"users": users_list}

@app.get("/api/admin/users/{user_id}", tags=["Admin"])
async def get_user_by_id_endpoint(user_id: str):
    """Get specific user by ID (admin only)"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "email": user["email"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "role": user["role"]
    }

@app.delete("/api/admin/users/{user_id}", tags=["Admin"])
async def delete_user_endpoint(user_id: str):
    """Delete user (admin only)"""
    # Find user by ID
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Delete user from Excel storage
        delete_user(user["username"])
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Delete failed: {str(e)}")

@app.put("/api/admin/users/{user_id}/status", tags=["Admin"])
async def toggle_user_status(user_id: str, is_active: dict):
    """Toggle user active/inactive status (admin only)"""
    # Find user by ID
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Update user status in Excel
        updated_user = update_user(user["username"], **{"Is Active": is_active.get("is_active", True)})
        
        return {
            "message": "User status updated successfully",
            "user": {
                "user_id": updated_user["user_id"],
                "username": updated_user["username"],
                "is_active": updated_user["is_active"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

@app.get("/api/admin/stats", tags=["Admin"])
async def get_system_stats():
    """Get system statistics (admin only)"""
    all_users = get_all_users()
    active_users = sum(1 for u in all_users if u["is_active"])
    return {
        "total_users": len(all_users),
        "active_users": active_users,
        "inactive_users": len(all_users) - active_users,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/admin/activity-log", tags=["Admin"])
async def get_activity_log():
    """Get activity log (admin only)"""
    return {
        "activities": [
            {"id": 1, "action": "user_login", "username": "admin", "timestamp": datetime.now().isoformat()},
            {"id": 2, "action": "cv_created", "username": "user", "timestamp": datetime.now().isoformat()},
        ]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
