"""
Keyword Search Module - Searches the internet for relevant job keywords
and integrates them into tailored CV content.
"""

import re
import httpx
from typing import List, Dict, Set
from html import unescape


def extract_job_keywords(job_description: str) -> Dict[str, List[str]]:
    """
    Extract structured keywords from a job description text.
    Returns categories: skills, tools, soft_skills, certifications
    """
    jd_lower = job_description.lower()

    # Technical skills / languages
    tech_patterns = [
        'python', 'java', 'javascript', 'typescript', 'c#', 'c\\+\\+', 'ruby',
        'go', 'golang', 'rust', 'php', 'scala', 'kotlin', 'swift', 'r\\b',
        'react', 'angular', 'vue', 'next\\.js', 'nuxt', 'svelte',
        'node\\.js', 'express', 'fastapi', 'django', 'flask', 'spring',
        'rails', 'laravel', '.net', 'asp\\.net',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
        'dynamodb', 'cassandra', 'sqlite', 'oracle',
        'aws', 'azure', 'gcp', 'google cloud',
        'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins',
        'ci/cd', 'git', 'github', 'gitlab', 'bitbucket',
        'rest', 'graphql', 'grpc', 'soap', 'websocket',
        'html', 'css', 'sass', 'less', 'tailwind',
        'webpack', 'vite', 'babel', 'eslint', 'prettier',
        'jest', 'mocha', 'pytest', 'rspec', 'selenium', 'cypress',
        'kafka', 'rabbitmq', 'celery', 'sidekiq',
        'linux', 'unix', 'bash', 'powershell',
        'nginx', 'apache', 'caddy',
        'redis', 'memcached',
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'data science', 'big data', 'spark', 'hadoop', 'airflow',
        'microservices', 'serverless', 'event-driven',
        'figma', 'sketch', 'adobe xd',
    ]

    found_skills = []
    for pattern in tech_patterns:
        if re.search(r'\b' + pattern + r'\b', jd_lower):
            # Clean up the pattern for display
            skill = pattern.replace('\\b', '').replace('\\.', '.').replace('\\+', '+')
            found_skills.append(skill)

    # Soft skills & methodologies
    soft_patterns = [
        'agile', 'scrum', 'kanban', 'lean',
        'leadership', 'mentoring', 'collaboration',
        'communication', 'problem-solving', 'analytical',
        'tdd', 'bdd', 'pair programming', 'code review',
        'remote', 'cross-functional', 'stakeholder',
        'accessibility', 'wcag', 'performance',
        'security', 'compliance', 'gdpr',
        'documentation', 'architecture', 'design patterns',
        'scalability', 'reliability', 'observability',
        'monitoring', 'logging', 'debugging',
    ]

    found_soft = []
    for pattern in soft_patterns:
        if re.search(r'\b' + pattern + r'\b', jd_lower):
            found_soft.append(pattern)

    # Certifications
    cert_patterns = [
        'aws certified', 'azure certified', 'gcp certified',
        'pmp', 'scrum master', 'kubernetes certified',
        'cissp', 'comptia', 'oracle certified',
    ]

    found_certs = []
    for pattern in cert_patterns:
        if pattern in jd_lower:
            found_certs.append(pattern)

    return {
        'skills': found_skills,
        'soft_skills': found_soft,
        'certifications': found_certs,
    }


async def search_job_keywords_online(job_title: str, existing_keywords: List[str] = None) -> Dict:
    """
    Search the internet for trending/relevant keywords for a job title.
    Uses Google search to find job-related skills and keywords.
    Returns a dict with: trending_skills, action_verbs, industry_terms
    """
    if existing_keywords is None:
        existing_keywords = []

    existing_lower = {kw.lower() for kw in existing_keywords}
    results = {
        'trending_skills': [],
        'action_verbs': [],
        'industry_terms': [],
        'search_source': '',
    }

    # Normalize job title for search
    clean_title = re.sub(r'[^\w\s]', '', job_title).strip()
    if not clean_title:
        clean_title = "software developer"

    search_queries = [
        f"{clean_title} required skills 2025 2026",
        f"{clean_title} resume keywords ATS",
    ]

    all_page_text = ""

    for query in search_queries:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                # Use Google search
                url = "https://www.google.com/search"
                params = {"q": query, "num": 5}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    page_text = _extract_text_from_html(response.text)
                    all_page_text += " " + page_text
                    results['search_source'] = 'Google Search'
                    print(f"[KEYWORD_SEARCH] Fetched results for: {query}")
        except Exception as e:
            print(f"[KEYWORD_SEARCH] Search failed for '{query}': {e}")
            continue

    if not all_page_text.strip():
        # Fallback: use curated keyword database
        print("[KEYWORD_SEARCH] Online search failed, using curated keywords")
        return _get_curated_keywords(clean_title, existing_lower)

    # Extract skills from search results
    found_skills = _extract_skills_from_text(all_page_text, existing_lower)
    results['trending_skills'] = found_skills[:15]

    # Get relevant action verbs
    results['action_verbs'] = _get_action_verbs_for_role(clean_title)

    # Extract industry terms
    results['industry_terms'] = _extract_industry_terms(all_page_text, existing_lower)[:10]

    return results


def _extract_text_from_html(html: str) -> str:
    """Strip HTML tags and return plain text"""
    # Remove script and style elements
    text = re.sub(r'<(script|style)[^>]*>.*?</(script|style)>', '', html, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Decode HTML entities
    text = unescape(text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text


def _extract_skills_from_text(text: str, exclude: Set[str]) -> List[str]:
    """Extract technical skills mentioned in search results text"""
    text_lower = text.lower()

    skills_database = [
        # Languages
        'Python', 'Java', 'JavaScript', 'TypeScript', 'C#', 'C++', 'Ruby', 'Go',
        'Rust', 'PHP', 'Scala', 'Kotlin', 'Swift', 'R',
        # Frontend
        'React', 'Angular', 'Vue.js', 'Next.js', 'Svelte', 'Redux', 'HTML5', 'CSS3',
        'SASS', 'Tailwind CSS', 'Bootstrap', 'Material UI', 'Webpack', 'Vite',
        # Backend
        'Node.js', 'Express', 'FastAPI', 'Django', 'Flask', 'Spring Boot',
        'Ruby on Rails', 'ASP.NET', 'Laravel', 'NestJS',
        # Databases
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'DynamoDB', 'Cassandra', 'SQLite', 'Oracle',
        # Cloud & DevOps
        'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
        'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI',
        'Ansible', 'Chef', 'Puppet',
        # Testing
        'Jest', 'Mocha', 'Pytest', 'RSpec', 'Selenium', 'Cypress',
        'Playwright', 'JUnit', 'TestNG',
        # Messaging / Queues
        'Kafka', 'RabbitMQ', 'SQS', 'Celery', 'Sidekiq',
        # Data / ML
        'TensorFlow', 'PyTorch', 'Pandas', 'NumPy', 'Scikit-learn',
        'Spark', 'Hadoop', 'Airflow', 'Tableau', 'Power BI',
        # API / Architecture
        'REST API', 'GraphQL', 'gRPC', 'Microservices', 'Serverless',
        'Event-driven', 'CQRS', 'Domain-Driven Design',
        # Other
        'Git', 'Linux', 'Nginx', 'CI/CD', 'Agile', 'Scrum',
        'JIRA', 'Confluence', 'Figma', 'Storybook',
        'OAuth', 'JWT', 'SAML', 'RBAC',
        'Responsive Design', 'Accessibility', 'WCAG',
        'Performance Optimization', 'SEO',
        'WebSocket', 'Socket.io', 'Server-Sent Events',
    ]

    found = []
    for skill in skills_database:
        if skill.lower() not in exclude and skill.lower() in text_lower:
            found.append(skill)

    return found


def _extract_industry_terms(text: str, exclude: Set[str]) -> List[str]:
    """Extract industry-specific terms from search result text"""
    text_lower = text.lower()

    industry_terms = [
        'scalability', 'high availability', 'load balancing', 'caching',
        'distributed systems', 'fault tolerance', 'resilience',
        'observability', 'monitoring', 'SLOs', 'SLIs',
        'infrastructure as code', 'containerisation',
        'continuous integration', 'continuous deployment',
        'code review', 'pair programming', 'test-driven development',
        'behaviour-driven development',
        'design patterns', 'SOLID principles', 'clean architecture',
        'cross-functional teams', 'stakeholder management',
        'technical debt', 'refactoring',
        'data pipeline', 'ETL', 'data warehouse',
        'service mesh', 'API gateway', 'rate limiting',
        'blue-green deployment', 'canary releases',
        'feature flags', 'A/B testing',
    ]

    found = []
    for term in industry_terms:
        if term.lower() not in exclude and term.lower() in text_lower:
            found.append(term)

    return found


def _get_action_verbs_for_role(job_title: str) -> List[str]:
    """Return role-appropriate action verbs for CV bullet points"""
    title_lower = job_title.lower()

    common_verbs = [
        'Developed', 'Designed', 'Implemented', 'Optimized', 'Delivered',
        'Collaborated', 'Built', 'Led', 'Architected', 'Automated',
    ]

    if any(w in title_lower for w in ['frontend', 'front-end', 'ui', 'react']):
        return common_verbs + [
            'Converted', 'Styled', 'Rendered', 'Integrated', 'Refactored',
            'Tested', 'Improved', 'Enhanced', 'Modernized', 'Migrated',
        ]
    elif any(w in title_lower for w in ['backend', 'back-end', 'server', 'api']):
        return common_verbs + [
            'Deployed', 'Scaled', 'Containerised', 'Secured', 'Monitored',
            'Provisioned', 'Configured', 'Maintained', 'Troubleshot', 'Resolved',
        ]
    elif any(w in title_lower for w in ['full stack', 'fullstack']):
        return common_verbs + [
            'Engineered', 'Deployed', 'Integrated', 'Tested', 'Debugged',
            'Refactored', 'Maintained', 'Scaled', 'Secured', 'Mentored',
        ]
    elif any(w in title_lower for w in ['devops', 'sre', 'infrastructure']):
        return common_verbs + [
            'Provisioned', 'Containerised', 'Orchestrated', 'Monitored',
            'Automated', 'Configured', 'Secured', 'Scaled', 'Troubleshot',
        ]
    elif any(w in title_lower for w in ['data', 'ml', 'machine learning', 'analyst']):
        return common_verbs + [
            'Analyzed', 'Modeled', 'Trained', 'Evaluated', 'Visualized',
            'Extracted', 'Transformed', 'Predicted', 'Clustered', 'Classified',
        ]
    else:
        return common_verbs + [
            'Engineered', 'Maintained', 'Tested', 'Deployed', 'Integrated',
            'Resolved', 'Refactored', 'Scaled', 'Documented', 'Mentored',
        ]


def _get_curated_keywords(job_title: str, exclude: Set[str]) -> Dict:
    """Fallback curated keywords when online search is unavailable"""
    title_lower = job_title.lower()

    role_keywords = {
        'frontend': {
            'trending_skills': [
                'React', 'TypeScript', 'Next.js', 'Redux', 'Tailwind CSS',
                'Webpack', 'Vite', 'Storybook', 'Jest', 'Cypress',
                'Performance Optimization', 'Accessibility', 'WCAG',
                'Responsive Design', 'CSS3', 'HTML5',
            ],
            'industry_terms': [
                'component architecture', 'design systems', 'state management',
                'server-side rendering', 'progressive web apps', 'web vitals',
                'code splitting', 'lazy loading', 'tree shaking',
            ],
        },
        'backend': {
            'trending_skills': [
                'Node.js', 'Python', 'PostgreSQL', 'Docker', 'Kubernetes',
                'REST API', 'GraphQL', 'Redis', 'Kafka', 'Microservices',
                'CI/CD', 'AWS', 'Terraform', 'Monitoring',
            ],
            'industry_terms': [
                'distributed systems', 'event-driven architecture', 'caching strategies',
                'database optimization', 'API gateway', 'load balancing',
                'containerisation', 'infrastructure as code',
            ],
        },
        'fullstack': {
            'trending_skills': [
                'React', 'Node.js', 'TypeScript', 'PostgreSQL', 'Docker',
                'REST API', 'Redux', 'Jest', 'CI/CD', 'AWS',
                'Git', 'Agile', 'MongoDB', 'Redis',
            ],
            'industry_terms': [
                'full-stack architecture', 'API design', 'database design',
                'responsive design', 'authentication', 'authorization',
                'automated testing', 'continuous deployment',
            ],
        },
        'devops': {
            'trending_skills': [
                'Docker', 'Kubernetes', 'Terraform', 'AWS', 'Azure',
                'Jenkins', 'GitHub Actions', 'Ansible', 'Linux',
                'Prometheus', 'Grafana', 'ELK Stack',
            ],
            'industry_terms': [
                'infrastructure as code', 'GitOps', 'observability',
                'blue-green deployment', 'canary releases', 'chaos engineering',
                'service mesh', 'container orchestration',
            ],
        },
        'data': {
            'trending_skills': [
                'Python', 'SQL', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch',
                'Spark', 'Airflow', 'Tableau', 'Power BI', 'Scikit-learn',
                'PostgreSQL', 'MongoDB', 'AWS', 'Docker',
            ],
            'industry_terms': [
                'data pipeline', 'ETL', 'data warehouse', 'feature engineering',
                'model deployment', 'A/B testing', 'statistical analysis',
            ],
        },
    }

    # Determine which role matches best
    matched_role = 'fullstack'  # default
    for role_key in role_keywords:
        if role_key in title_lower:
            matched_role = role_key
            break
    if 'front' in title_lower:
        matched_role = 'frontend'
    elif 'back' in title_lower:
        matched_role = 'backend'

    role_data = role_keywords.get(matched_role, role_keywords['fullstack'])

    # Filter out already-present keywords
    trending = [s for s in role_data['trending_skills'] if s.lower() not in exclude]
    industry = [s for s in role_data['industry_terms'] if s.lower() not in exclude]

    return {
        'trending_skills': trending[:15],
        'action_verbs': _get_action_verbs_for_role(job_title),
        'industry_terms': industry[:10],
        'search_source': 'Curated Database',
    }


def inject_keywords_into_cv(cv_text: str, jd_keywords: Dict, web_keywords: Dict) -> str:
    """
    Aggressively inject ALL missing keywords from job description and web search
    into the tailored CV content. Adds to skills, summary, and experience sections.
    """
    lines = cv_text.split('\n')
    cv_lower = cv_text.lower()

    # Collect ALL keywords not already in the CV
    new_skills = []
    for skill in jd_keywords.get('skills', []) + web_keywords.get('trending_skills', []):
        if skill.lower() not in cv_lower:
            new_skills.append(skill)
    new_skills = list(dict.fromkeys(new_skills))  # deduplicate, keep all

    new_soft = []
    for ss in jd_keywords.get('soft_skills', []):
        if ss.lower() not in cv_lower:
            new_soft.append(ss)
    new_soft = list(dict.fromkeys(new_soft))

    new_industry = []
    for term in web_keywords.get('industry_terms', []):
        if term.lower() not in cv_lower:
            new_industry.append(term)
    new_industry = list(dict.fromkeys(new_industry))

    new_certs = []
    for cert in jd_keywords.get('certifications', []):
        if cert.lower() not in cv_lower:
            new_certs.append(cert)
    new_certs = list(dict.fromkeys(new_certs))

    action_verbs = web_keywords.get('action_verbs', [])

    if not new_skills and not new_soft and not new_industry and not new_certs:
        return cv_text  # Nothing new to add

    # Group new skills into categories for proper display
    def _categorize_skills(skills_list):
        categories = {
            'Languages': [], 'Frameworks': [], 'Databases': [],
            'Cloud & DevOps': [], 'Tools & Platforms': [], 'Other': []
        }
        lang_kw = {'python', 'java', 'javascript', 'typescript', 'c#', 'c++', 'php', 'ruby', 'go', 'golang', 'rust', 'scala', 'kotlin', 'swift', 'r', 'html', 'css', 'sass', 'less'}
        fw_kw = {'react', 'angular', 'vue', 'next.js', 'nuxt', 'svelte', 'django', 'flask', 'fastapi', 'spring', 'express', 'node.js', 'rails', 'laravel', '.net', 'asp.net', 'tailwind', 'bootstrap'}
        db_kw = {'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'dynamodb', 'cassandra', 'sqlite', 'oracle', 'firebase'}
        cloud_kw = {'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform', 'ansible', 'jenkins', 'ci/cd', 'serverless', 'cloudflare', 'heroku', 'vercel', 'netlify'}
        for s in skills_list:
            sl = s.lower()
            if sl in lang_kw:
                categories['Languages'].append(s)
            elif sl in fw_kw:
                categories['Frameworks'].append(s)
            elif sl in db_kw:
                categories['Databases'].append(s)
            elif sl in cloud_kw:
                categories['Cloud & DevOps'].append(s)
            else:
                categories['Other'].append(s)
        return {k: v for k, v in categories.items() if v}

    skill_cats = _categorize_skills(new_skills)

    result_lines = []
    in_skills_section = False
    skills_section_done = False
    in_summary_section = False
    in_experience_section = False
    summary_lines = []
    experience_bullet_count = 0

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        upper = stripped.upper()

        # Detect section transitions
        is_section_header = upper in (
            'TECHNICAL SKILLS', 'CORE COMPETENCIES', 'SKILLS', 'KEY SKILLS',
            'PROFILE SUMMARY', 'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE',
            'EDUCATION', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EXPERIENCE',
            'PROJECTS', 'CERTIFICATES AND TRAINING', 'CERTIFICATIONS',
            'HIGHLIGHT', 'HIGHLIGHTS', 'ADDITIONAL INFORMATION',
        )

        if is_section_header:
            # Flush pending state before entering new section
            if in_skills_section and not skills_section_done:
                _inject_skills_lines(result_lines, skill_cats, new_soft, new_industry)
                skills_section_done = True
            if in_summary_section and summary_lines:
                _flush_summary(result_lines, summary_lines, new_soft, new_industry)
                summary_lines = []

            in_skills_section = upper in ('TECHNICAL SKILLS', 'CORE COMPETENCIES', 'SKILLS', 'KEY SKILLS')
            in_summary_section = upper in ('PROFILE SUMMARY', 'PROFESSIONAL SUMMARY', 'SUMMARY', 'OBJECTIVE')
            in_experience_section = upper in ('PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EXPERIENCE')
            if not in_skills_section:
                experience_bullet_count = 0

            result_lines.append(line)
            i += 1
            continue

        # Collect summary content for enhancement
        if in_summary_section:
            if stripped:
                summary_lines.append(stripped)
            else:
                if summary_lines:
                    _flush_summary(result_lines, summary_lines, new_soft, new_industry)
                    summary_lines = []
                result_lines.append(line)
                in_summary_section = False
            i += 1
            continue

        # Enhance experience bullets with action verbs
        if in_experience_section and stripped.startswith(('•', '- ', '* ')) and action_verbs:
            bullet_text = stripped.lstrip('•-* ').strip()
            # If bullet doesn't start with an action verb, prepend one
            first_word = bullet_text.split()[0].lower() if bullet_text.split() else ''
            known_verbs = {v.lower() for v in action_verbs}
            common_verbs = {'developed', 'designed', 'implemented', 'built', 'created', 'managed',
                           'led', 'improved', 'optimized', 'delivered', 'architected', 'deployed',
                           'maintained', 'configured', 'automated', 'integrated', 'established',
                           'collaborated', 'mentored', 'spearheaded', 'streamlined', 'enhanced'}
            if first_word not in known_verbs and first_word not in common_verbs:
                if action_verbs:
                    verb = action_verbs[experience_bullet_count % len(action_verbs)]
                    bullet_text = f"{verb} {bullet_text[0].lower()}{bullet_text[1:]}" if bullet_text else bullet_text
            experience_bullet_count += 1
            result_lines.append(f"• {bullet_text}")
            i += 1
            continue

        # Pass through all other lines
        result_lines.append(line)
        i += 1

    # Handle case where summary or skills was the last section
    if summary_lines:
        _flush_summary(result_lines, summary_lines, new_soft, new_industry)
    if in_skills_section and not skills_section_done:
        _inject_skills_lines(result_lines, skill_cats, new_soft, new_industry)

    # If there are certifications to add and no CERTIFICATES section exists
    enhanced = '\n'.join(result_lines)
    if new_certs and 'CERTIFICATES' not in enhanced.upper():
        enhanced += '\n\nCERTIFICATES AND TRAINING\n'
        for cert in new_certs:
            enhanced += f'• {cert}\n'

    return enhanced


def _inject_skills_lines(result_lines: list, skill_cats: dict, new_soft: list, new_industry: list):
    """Add categorized skill lines into the skills section."""
    for cat_name, cat_skills in skill_cats.items():
        result_lines.append(f"• {cat_name}: {', '.join(cat_skills)}")
    # Add soft skills and methodologies as a line
    extras = []
    if new_soft:
        extras.extend(new_soft)
    if new_industry:
        extras.extend(new_industry)
    if extras:
        result_lines.append(f"• Methodologies & Skills: {', '.join(extras)}")


def _flush_summary(result_lines: list, summary_lines: list, new_soft: list, new_industry: list):
    """Flush enhanced summary with injected keywords."""
    summary_text = ' '.join(summary_lines)
    additions = []
    if new_soft:
        additions.extend(new_soft[:5])
    if new_industry:
        additions.extend(new_industry[:5])
    if additions:
        summary_text += f" Demonstrated expertise in {', '.join(additions)}."
    result_lines.append(summary_text)
