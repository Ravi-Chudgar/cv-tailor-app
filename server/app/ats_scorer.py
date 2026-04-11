"""
ATS Scorer - Comprehensive ATS scoring based on real-world ATS checker criteria
(Jobscan, ResumeWorded, Zety, Indeed best practices)

Evaluates: keyword match, formatting & structure, impact & content quality, ATS compatibility
"""

import re
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# Standard ATS section headings (case-insensitive match)
# ---------------------------------------------------------------------------
STANDARD_SECTIONS = {
    "summary": ["summary", "profile summary", "professional summary", "profile", "objective", "about"],
    "experience": ["experience", "work experience", "professional experience", "employment", "work history"],
    "skills": ["skills", "technical skills", "core competencies", "key skills", "competencies"],
    "education": ["education", "academic", "qualifications", "academic qualifications"],
    "certifications": ["certifications", "certificates", "certificates and training", "licenses"],
    "projects": ["projects", "key projects", "personal projects"],
}

# Action verbs commonly expected by ATS / hiring managers
ACTION_VERBS = {
    "achieved", "administered", "analyzed", "architected", "automated",
    "built", "championed", "collaborated", "configured", "consolidated",
    "coordinated", "created", "debugged", "defined", "delivered",
    "deployed", "designed", "developed", "directed", "documented",
    "drove", "enabled", "engineered", "ensured", "established",
    "evaluated", "executed", "expanded", "facilitated", "formulated",
    "generated", "guided", "handled", "headed", "identified",
    "implemented", "improved", "increased", "initiated", "innovated",
    "integrated", "introduced", "investigated", "launched", "led",
    "leveraged", "maintained", "managed", "mentored", "migrated",
    "modeled", "monitored", "negotiated", "operated", "optimized",
    "orchestrated", "organized", "oversaw", "partnered", "performed",
    "pioneered", "planned", "prepared", "presented", "produced",
    "programmed", "proposed", "provided", "published", "ran",
    "rebuilt", "reduced", "refactored", "reformulated", "reorganized",
    "resolved", "restored", "restructured", "reviewed", "revamped",
    "scaled", "secured", "simplified", "spearheaded", "standardized",
    "streamlined", "strengthened", "supervised", "supported", "tested",
    "trained", "transformed", "troubleshot", "upgraded", "utilized",
    "validated", "wrote",
}

# Metric patterns – numbers, percentages, currency
METRIC_PATTERN = re.compile(
    r'\b(\d{1,3}[,.]?\d*\s*%'          # percentages  20%, 3.5%
    r'|\$\s?\d[\d,]*'                   # dollar amounts  $50K
    r'|\d{2,}[+]?'                      # plain numbers >= 10
    r'|\d{1,3}[Kk]\b'                   # shorthand 100K
    r')',
    re.IGNORECASE,
)


# ===================================================================
# Component scorers
# ===================================================================

def _score_keyword_match(
    cv_text: str,
    jd_keywords: Dict[str, List[str]],
    web_keywords: Dict[str, List[str]],
) -> Tuple[int, List[str], List[str], List[str]]:
    """
    Score: what % of JD + web-searched keywords appear in the CV,
    weighted by whether their FREQUENCY in the CV approaches the JD frequency.
    Returns (score_0_100, matched_list, missing_list, recommendations)
    """
    all_kw = set()
    for key in ("skills", "soft_skills", "certifications"):
        for k in jd_keywords.get(key, []):
            all_kw.add(k.lower().strip())
    for k in web_keywords.get("trending_skills", []):
        all_kw.add(k.lower().strip())
    all_kw.discard("")

    if not all_kw:
        return 100, [], [], ["No keywords extracted from the job description."]

    cv_lower = cv_text.lower()
    keyword_freq = jd_keywords.get('keyword_freq', {})

    matched = []
    missing = []
    freq_score_sum = 0.0

    for k in sorted(all_kw):
        cv_count = len(re.findall(re.escape(k), cv_lower))
        if cv_count > 0:
            matched.append(k)
            # Score based on frequency match (JD count vs CV count)
            jd_count = keyword_freq.get(k, 1)
            ratio = min(cv_count / max(jd_count, 1), 1.0)
            freq_score_sum += ratio
        else:
            missing.append(k)

    # Overall score = weighted combination of coverage and frequency match
    coverage = len(matched) / len(all_kw)
    freq_avg = freq_score_sum / len(all_kw) if all_kw else 1.0
    # 60% weight on coverage, 40% on frequency matching
    combined = (coverage * 0.6 + freq_avg * 0.4) * 100
    score = min(round(combined), 100)

    recs: List[str] = []
    if missing:
        top_missing = [m.title() for m in missing[:8]]
        recs.append(f"Missing keywords: {', '.join(top_missing)}")

    # Check for under-represented keywords
    under_rep = []
    for k in matched:
        jd_count = keyword_freq.get(k, 1)
        cv_count = len(re.findall(re.escape(k), cv_lower))
        if cv_count < jd_count:
            under_rep.append(f"{k.title()} ({cv_count}x vs {jd_count}x in JD)")
    if under_rep:
        recs.append(f"Low frequency keywords: {', '.join(under_rep[:5])}. Use them more often.")

    if score < 60:
        recs.append("Keyword match is low — tailor your Skills and Summary sections to the job description.")
    elif score < 80:
        recs.append("Good keyword coverage — add a few more missing terms and increase keyword frequency.")
    else:
        recs.append("Strong keyword match — well aligned with the job description.")

    return score, matched, missing, recs


def _score_formatting_structure(cv_text: str) -> Tuple[int, List[str]]:
    """
    Checks:
      - Standard section headings present (Summary, Experience, Skills, Education)
      - Bullet points used
      - Consistent date formatting
      - Reasonable word count (300-800 ideal for 1-page)
      - No all-caps content blocks
    """
    lines = cv_text.split("\n")
    recs: List[str] = []
    deductions = 0  # start from 100

    # 1. Section detection – must have at least 3 of 4 core sections
    found_sections = set()
    for line in lines:
        stripped = line.strip().lower()
        for section_key, aliases in STANDARD_SECTIONS.items():
            for alias in aliases:
                if stripped == alias or stripped.startswith(alias + " ") or stripped.endswith(alias):
                    found_sections.add(section_key)
    
    core_sections = {"summary", "experience", "skills", "education"}
    present_core = core_sections & found_sections
    missing_core = core_sections - found_sections

    if len(present_core) == 4:
        pass  # perfect
    elif len(present_core) == 3:
        deductions += 5
        recs.append(f"Missing section: {', '.join(s.title() for s in missing_core)}. Add it for better ATS parsing.")
    elif len(present_core) == 2:
        deductions += 15
        recs.append(f"Missing sections: {', '.join(s.title() for s in missing_core)}. ATS expects standard headings.")
    else:
        deductions += 25
        recs.append("Most standard sections are missing. Use headings like Summary, Experience, Skills, Education.")

    # Bonus for extra sections (certs, projects)
    bonus_sections = {"certifications", "projects"}
    bonus_found = bonus_sections & found_sections
    bonus = len(bonus_found) * 2  # up to +4

    # 2. Bullet point usage
    bullet_lines = [l for l in lines if l.strip().startswith(("•", "-", "–", "▪", "◦", "*"))]
    if len(bullet_lines) >= 10:
        pass
    elif len(bullet_lines) >= 5:
        deductions += 5
        recs.append("Use more bullet points (10+) for experience and skills — ATS parses them better.")
    else:
        deductions += 12
        recs.append("Very few bullet points detected. Bullet-formatted content improves ATS readability.")

    # 3. Word count
    words = cv_text.split()
    word_count = len(words)
    if 250 <= word_count <= 900:
        pass
    elif word_count < 250:
        deductions += 10
        recs.append(f"CV is too short ({word_count} words). Aim for 350-700 words for a strong 1-page resume.")
    elif word_count > 900:
        deductions += 5
        recs.append(f"CV is lengthy ({word_count} words). Consider trimming to 1 page for ATS compatibility.")

    # 4. Date formatting consistency
    date_patterns = re.findall(
        r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]*\d{4}'
        r'|\d{1,2}/\d{4}'
        r'|\d{4}\s*[-–]\s*(?:\d{4}|[Pp]resent|[Cc]urrent))',
        cv_text,
    )
    if len(date_patterns) >= 2:
        pass  # dates present and formatted
    elif len(date_patterns) == 1:
        deductions += 3
    else:
        deductions += 8
        recs.append("No date ranges detected in experience. Add dates for each role (e.g., Jan 2020 – Present).")

    # 5. No long all-caps blocks (> 50 chars) — tables / graphics hint
    allcaps_blocks = [l for l in lines if len(l.strip()) > 50 and l.strip() == l.strip().upper() and l.strip()]
    if allcaps_blocks:
        deductions += 5
        recs.append("Avoid large all-caps text blocks — they can confuse ATS parsing.")

    score = max(0, min(100, 100 - deductions + bonus))
    return score, recs


def _score_impact_content(cv_text: str) -> Tuple[int, List[str]]:
    """
    Checks:
      - Measurable achievements (numbers, %, $)
      - Action verbs starting bullets
      - Professional summary present and substantial
      - No first-person pronouns (I, me, my)
    """
    lines = cv_text.split("\n")
    recs: List[str] = []
    deductions = 0

    # 1. Measurable metrics in experience
    bullet_lines = [l.strip() for l in lines if l.strip().startswith(("•", "-", "–", "*"))]
    bullets_with_metrics = [l for l in bullet_lines if METRIC_PATTERN.search(l)]

    if bullet_lines:
        metric_ratio = len(bullets_with_metrics) / len(bullet_lines)
    else:
        metric_ratio = 0

    if metric_ratio >= 0.3:
        pass  # 30%+ bullets have metrics — strong
    elif metric_ratio >= 0.15:
        deductions += 8
        recs.append("Add more quantifiable results (numbers, %, $) to experience bullets — aim for 30%+ with metrics.")
    else:
        deductions += 18
        recs.append("Very few measurable achievements. Add metrics like 'Improved performance by 40%' or 'Managed team of 8'.")

    # 2. Action verbs
    verbs_found = 0
    for bl in bullet_lines:
        # strip bullet char and spaces
        text = re.sub(r'^[•\-–*▪◦]\s*', '', bl).strip()
        first_word = text.split()[0].lower().rstrip("ed,s") if text.split() else ""
        # Check the actual first word and its stem
        actual_first = text.split()[0].lower() if text.split() else ""
        if actual_first in ACTION_VERBS or first_word in ACTION_VERBS:
            verbs_found += 1

    if bullet_lines:
        verb_ratio = verbs_found / len(bullet_lines)
    else:
        verb_ratio = 0

    if verb_ratio >= 0.5:
        pass
    elif verb_ratio >= 0.25:
        deductions += 8
        recs.append("Start more bullet points with strong action verbs (Developed, Optimized, Led, Delivered).")
    else:
        deductions += 15
        recs.append("Most bullets lack action verbs. Begin each with a strong verb like Designed, Implemented, Achieved.")

    # 3. Summary quality
    summary_text = ""
    in_summary = False
    for line in lines:
        stripped = line.strip().lower()
        if any(stripped == alias or stripped.startswith(alias) for alias in STANDARD_SECTIONS["summary"]):
            in_summary = True
            continue
        if in_summary:
            if any(
                stripped == alias or stripped.startswith(alias)
                for aliases in STANDARD_SECTIONS.values()
                for alias in aliases
                if alias not in STANDARD_SECTIONS["summary"]
            ):
                break
            summary_text += line + " "

    summary_words = len(summary_text.split())
    if summary_words >= 30:
        pass
    elif summary_words >= 15:
        deductions += 5
        recs.append("Expand your professional summary to 30-50 words for strongest ATS impact.")
    else:
        deductions += 12
        recs.append("Professional summary is missing or too short. Add a 2-3 sentence summary targeting the role.")

    # 4. First-person pronouns
    pronoun_count = len(re.findall(r'\b(?:I|me|my|myself)\b', cv_text))
    if pronoun_count > 3:
        deductions += 5
        recs.append("Avoid first-person pronouns (I, me, my) — use implied subject style for ATS resumes.")
    elif pronoun_count > 0:
        deductions += 2

    score = max(0, min(100, 100 - deductions))
    return score, recs


def _score_ats_compatibility(cv_text: str) -> Tuple[int, List[str]]:
    """
    Checks:
      - Contact info present (email, phone, location, LinkedIn)
      - No special characters that break ATS (©, ®, ™, emoji)
      - Standard ASCII-safe content
      - No tables/columns hint (multiple tab chars)
      - File parsability (text-based, not image-based)
    """
    recs: List[str] = []
    deductions = 0

    # 1. Contact info
    has_email = bool(re.search(r'[\w.+-]+@[\w-]+\.[\w.]+', cv_text))
    has_phone = bool(re.search(r'[\+]?\d[\d\s\-().]{7,}', cv_text))
    has_linkedin = bool(re.search(r'linkedin\.com|linkedin', cv_text, re.IGNORECASE))
    has_location = bool(re.search(
        r'\b(?:London|Manchester|Birmingham|Bristol|Leeds|Glasgow|Edinburgh|Liverpool|'
        r'New York|San Francisco|Seattle|Chicago|Austin|Remote|UK|US|USA|India|'
        r'[A-Z][a-z]+,\s*[A-Z]{2}\b)',
        cv_text,
    ))

    contact_count = sum([has_email, has_phone, has_linkedin, has_location])
    if contact_count == 4:
        pass
    elif contact_count == 3:
        deductions += 3
        missing = []
        if not has_email: missing.append("email")
        if not has_phone: missing.append("phone")
        if not has_linkedin: missing.append("LinkedIn")
        if not has_location: missing.append("location")
        recs.append(f"Add {', '.join(missing)} to contact info for complete ATS profile.")
    elif contact_count == 2:
        deductions += 8
        recs.append("Include email, phone, location, and LinkedIn for best ATS results.")
    else:
        deductions += 15
        recs.append("Contact information is incomplete. ATS requires at minimum email and phone.")

    # 2. Special characters that confuse ATS
    special_chars = re.findall(r'[©®™☆★✦✧❖◆◇■□►▶◀▷◁♦♣♠♥✔✘✗✓✕❌❎⚡⭐🔥💡🏆🎯📧📞📍🌐→←↑↓↔]', cv_text)
    emoji_count = len(special_chars)
    if emoji_count == 0:
        pass
    elif emoji_count <= 3:
        deductions += 3
        recs.append("Remove special symbols/emojis — some ATS systems cannot parse them.")
    else:
        deductions += 10
        recs.append("Multiple special characters detected. Remove all emojis and symbols for ATS safety.")

    # 3. Tab characters (hint at tables/columns)
    tab_count = cv_text.count('\t')
    if tab_count > 10:
        deductions += 8
        recs.append("Tab characters detected (possible table/column layout). Use simple single-column format.")
    elif tab_count > 3:
        deductions += 3

    # 4. Very long lines (>150 chars) — might be merged columns
    long_lines = [l for l in cv_text.split("\n") if len(l.strip()) > 150]
    if len(long_lines) > 5:
        deductions += 5
        recs.append("Some lines are very long. Ensure single-column layout for reliable ATS parsing.")

    # 5. Email is parseable (not obfuscated)
    if has_email:
        pass
    else:
        recs.append("Ensure your email is in standard format (name@domain.com) for ATS extraction.")

    # 6. No header/footer content (page numbers, "Page 1 of 2")
    page_refs = re.findall(r'[Pp]age\s+\d+\s+of\s+\d+', cv_text)
    if page_refs:
        deductions += 3
        recs.append("Remove 'Page X of Y' — ATS may misparse header/footer content.")

    score = max(0, min(100, 100 - deductions))
    return score, recs


# ===================================================================
# Main Scoring Function
# ===================================================================

def calculate_ats_score(
    cv_text: str,
    jd_keywords: Dict[str, List[str]],
    web_keywords: Dict[str, List[str]],
) -> Dict:
    """
    Comprehensive ATS scoring modelled on Jobscan / ResumeWorded criteria.

    Returns dict with:
      - overall_score (0-100)
      - component_scores (4 components)
      - matched_keywords, missing_keywords
      - recommendations (prioritised list)
      - grade (A/B/C/D/F)
    """

    # Weights
    W_KEYWORD = 0.35
    W_FORMAT  = 0.25
    W_IMPACT  = 0.20
    W_ATS     = 0.20

    kw_score, matched, missing, kw_recs = _score_keyword_match(cv_text, jd_keywords, web_keywords)
    fmt_score, fmt_recs = _score_formatting_structure(cv_text)
    imp_score, imp_recs = _score_impact_content(cv_text)
    ats_score, ats_recs = _score_ats_compatibility(cv_text)

    # Bonus/penalty for job title match (Jobscan checks this explicitly)
    job_title = jd_keywords.get('job_title', '')
    if job_title and job_title.lower() in cv_text.lower():
        kw_score = min(100, kw_score + 5)   # bonus
    elif job_title:
        kw_score = max(0, kw_score - 5)     # penalty
        kw_recs.append(f"Include the exact job title '{job_title}' in your summary or experience.")

    overall = round(
        kw_score  * W_KEYWORD +
        fmt_score * W_FORMAT  +
        imp_score * W_IMPACT  +
        ats_score * W_ATS
    )
    overall = min(overall, 100)

    # Grade
    if overall >= 90:
        grade = "A+"
    elif overall >= 80:
        grade = "A"
    elif overall >= 70:
        grade = "B"
    elif overall >= 60:
        grade = "C"
    elif overall >= 50:
        grade = "D"
    else:
        grade = "F"

    # Merge recommendations – prioritise by impact
    all_recs = []
    for r in kw_recs:
        all_recs.append(("keyword", r))
    for r in imp_recs:
        all_recs.append(("impact", r))
    for r in fmt_recs:
        all_recs.append(("format", r))
    for r in ats_recs:
        all_recs.append(("compat", r))

    # Take top recommendations (max 8)
    recommendations = [r[1] for r in all_recs[:8]]

    return {
        "overall_score": overall,
        "grade": grade,
        "component_scores": {
            "keyword_match": kw_score,
            "formatting": fmt_score,
            "impact_content": imp_score,
            "ats_compatibility": ats_score,
        },
        "weights": {
            "keyword_match": f"{int(W_KEYWORD*100)}%",
            "formatting": f"{int(W_FORMAT*100)}%",
            "impact_content": f"{int(W_IMPACT*100)}%",
            "ats_compatibility": f"{int(W_ATS*100)}%",
        },
        "matched_keywords": [k.title() for k in matched],
        "missing_keywords": [k.title() for k in missing[:15]],
        "recommendations": recommendations,
    }
