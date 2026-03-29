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
    Uses BOTH a known-skill list AND NLP n-gram extraction to catch
    domain-specific terms the static list would miss (e.g. "regulatory compliance",
    "task automation", "Microsoft Certified").
    Returns categories: skills, tools, soft_skills, certifications
    """
    jd_lower = job_description.lower()

    # ---- 1. Static pattern matching (existing behaviour) ----
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
        'linux', 'unix', 'bash', 'powershell', 'shell scripting',
        'nginx', 'apache', 'caddy',
        'redis', 'memcached',
        'machine learning', 'deep learning', 'nlp', 'computer vision',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
        'data science', 'big data', 'spark', 'hadoop', 'airflow',
        'microservices', 'serverless', 'event-driven',
        'figma', 'sketch', 'adobe xd',
        # Automation / admin specific
        'scripting', 'task automation', 'process automation', 'workflow automation',
        'active directory', 'sccm', 'intune', 'group policy',
        'siem', 'splunk', 'servicenow', 'jira', 'confluence',
        'vmware', 'hyper-v', 'virtualisation', 'virtualization',
        'networking', 'tcp/ip', 'dns', 'dhcp', 'vpn', 'firewall',
        'itil', 'itsm', 'change management',
        'regulatory compliance', 'data governance', 'risk management',
        'power automate', 'power bi', 'sharepoint', 'exchange',
        'office 365', 'microsoft 365', 'm365',
    ]

    found_skills = []
    for pattern in tech_patterns:
        if re.search(r'\b' + pattern + r'\b', jd_lower):
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
        'troubleshooting', 'incident management', 'root cause analysis',
        'project management', 'time management', 'attention to detail',
        'critical thinking', 'decision making', 'teamwork',
        'adaptability', 'continuous improvement',
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
        'microsoft certified', 'itil certified', 'itil foundation',
        'ccna', 'ccnp', 'az-900', 'az-104', 'az-500',
        'aws solutions architect', 'aws developer',
        'certified ethical hacker', 'ceh',
        'security\\+', 'network\\+', 'a\\+',
    ]

    found_certs = []
    for pattern in cert_patterns:
        if re.search(r'\b' + pattern + r'\b', jd_lower):
            cert = pattern.replace('\\+', '+')
            found_certs.append(cert)

    # ---- 2. NLP n-gram extraction to catch JD-specific phrases ----
    # Extract meaningful 1-3 word phrases that appear multiple times or
    # match "skill-like" patterns in the JD but aren't in our static list.
    nlp_keywords = _extract_nlp_keywords(job_description)

    # Merge NLP-found keywords that aren't already captured
    # Filter out NLP n-grams that are just combinations of static skills or
    # fragments of the job title  —  these add noise, not value.
    all_found_lower = {s.lower() for s in found_skills + found_soft + found_certs}
    job_title_lower = _extract_job_title(job_description).lower()
    # Normalize job title (strip special chars + collapse spaces) for substring comparison
    job_title_norm = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', job_title_lower)).strip()
    for kw in nlp_keywords:
        kw_l = kw.lower()
        if kw_l in all_found_lower:
            continue
        # Skip if every word in the n-gram is already a standalone skill
        words = kw_l.split()
        if all(any(w in sk for sk in all_found_lower) for w in words):
            continue
        # Skip if the n-gram is a substring of the job title (normalized)
        kw_norm = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', '', kw_l)).strip()
        if kw_norm in job_title_norm:
            continue
        # Skip single tokens that look like truncated words (< 5 chars after title removal)
        if len(words) == 1 and len(words[0]) < 5:
            continue
        found_skills.append(kw)
        all_found_lower.add(kw_l)

    # ---- 3. Count keyword frequency in JD for smart injection later ----
    keyword_freq = {}
    for kw in found_skills + found_soft + found_certs:
        count = len(re.findall(re.escape(kw.lower()), jd_lower))
        if count > 0:
            keyword_freq[kw.lower()] = count

    # ---- 4. Extract job title from JD ----
    job_title = _extract_job_title(job_description)

    return {
        'skills': found_skills,
        'soft_skills': found_soft,
        'certifications': found_certs,
        'keyword_freq': keyword_freq,
        'job_title': job_title,
    }


def _extract_job_title(job_description: str) -> str:
    """
    Extract the job title from a job description.
    Looks for common patterns like 'Job Title: ...', 'Position: ...',
    or treats the first short meaningful line as the title.
    """
    lines = [l.strip() for l in job_description.strip().split('\n') if l.strip()]
    if not lines:
        return ''

    # Pattern 1: explicit label  (e.g.  "Job Title: Tools & Automation Admin")
    for line in lines[:10]:
        m = re.match(
            r'^(?:job\s*title|position|role|title)\s*[:\-–]\s*(.+)',
            line, re.IGNORECASE,
        )
        if m:
            return m.group(1).strip().rstrip('.')

    # Pattern 2: first line that looks like a title (short, no sentence punctuation)
    first = lines[0]
    if len(first) < 100 and not first.endswith('.') and not first.lower().startswith(('we ', 'our ', 'the ', 'a ', 'an ')):
        return first.strip()

    # Pattern 3: look for "hiring ... <title>" or "looking for ... <title>"
    full = ' '.join(lines[:5])
    m = re.search(
        r'(?:hiring|looking\s+for|seeking|recruit)\s+(?:a\s+|an\s+)?(.+?)(?:\.|,|to\s+join| who| with)',
        full, re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()

    return lines[0][:80] if lines else ''


# Stop words for NLP extraction
_STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'may', 'might', 'can', 'shall', 'must',
    'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
    'we', 'our', 'you', 'your', 'he', 'she', 'his', 'her', 'i', 'me', 'my',
    'not', 'no', 'if', 'then', 'than', 'so', 'up', 'out', 'about', 'into',
    'over', 'after', 'before', 'between', 'under', 'such', 'each', 'every',
    'all', 'both', 'few', 'more', 'most', 'other', 'some', 'any', 'only',
    'same', 'also', 'very', 'just', 'because', 'through', 'during', 'where',
    'when', 'which', 'who', 'whom', 'what', 'how', 'why', 'here', 'there',
    # Job-description filler words
    'role', 'position', 'candidate', 'ability', 'experience', 'work',
    'working', 'team', 'company', 'required', 'requirements', 'preferred',
    'responsibilities', 'responsible', 'including', 'including', 'ensure',
    'support', 'within', 'across', 'using', 'strong', 'good', 'excellent',
    'years', 'year', 'minimum', 'least', 'well', 'new', 'etc', 'e.g',
    'knowledge', 'understanding', 'join', 'looking', 'seeking', 'apply',
    'qualification', 'qualifications', 'opportunity', 'environment',
    'processes', 'process', 'systems', 'system', 'tools', 'tool',
    'manage', 'management', 'maintain', 'implement', 'develop',
    'skills', 'skill', 'solutions', 'solution', 'services', 'service',
    'stakeholders', 'issues', 'complex', 'resolve', 'needs',
}


def _extract_nlp_keywords(job_description: str) -> List[str]:
    """
    Extract meaningful keyword phrases from JD using n-gram frequency analysis.
    Finds domain-specific terms that a static list would miss.
    """
    # Tokenize: keep letters, digits, hyphens, slashes, plus signs
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#/.\-]*(?:'s)?", job_description)
    # Lowercase tokens, filter stop words
    filtered = [t.lower().removesuffix("'s") for t in tokens if t.lower().removesuffix("'s") not in _STOP_WORDS and len(t) > 2]

    # Count unigrams
    from collections import Counter
    uni_counts = Counter(filtered)

    # Build bigrams and trigrams from the original token stream
    bigrams = []
    trigrams = []
    for i in range(len(filtered) - 1):
        bigrams.append(f"{filtered[i]} {filtered[i+1]}")
    for i in range(len(filtered) - 2):
        trigrams.append(f"{filtered[i]} {filtered[i+1]} {filtered[i+2]}")

    bi_counts = Counter(bigrams)
    tri_counts = Counter(trigrams)

    results = []

    # Trigrams that appear 2+ times are very likely important phrases
    for phrase, count in tri_counts.most_common(10):
        if count >= 2:
            results.append(phrase.title())

    # Bigrams appearing 2+ times
    for phrase, count in bi_counts.most_common(20):
        if count >= 2:
            results.append(phrase.title())

    # Unigrams appearing 3+ times (technical nouns, not filler)
    for word, count in uni_counts.most_common(30):
        if count >= 3 and word not in _STOP_WORDS:
            results.append(word.title())

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for r in results:
        key = r.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    return deduped[:20]


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
    Inject missing keywords from job description and web search into the
    tailored CV content. Ensures keyword FREQUENCY in the resume approaches
    the frequency in the JD so that ATS scanners (Jobscan-style) see a high
    match rate.

    Strategy:
      1. Insert the exact job title from the JD into the summary (Jobscan
         "Job Title Match" check).
      2. Add missing skills into the Skills section.
      3. Weave high-frequency JD keywords into Summary, Experience bullets,
         and a new "Key Competencies" line so they appear multiple times.
      4. Add missing certifications.
      5. Ensure soft skills appear in experience bullet context.
    """
    lines = cv_text.split('\n')
    cv_lower = cv_text.lower()

    # ---- Job title from JD (critical for Jobscan "Job Title Match") ----
    job_title = jd_keywords.get('job_title', '')

    # ---- Collect JD keyword frequencies ----
    keyword_freq = jd_keywords.get('keyword_freq', {})

    # Collect ALL keywords not already in the CV
    new_skills = []
    _seen_lower = set()
    for skill in jd_keywords.get('skills', []) + web_keywords.get('trending_skills', []):
        sl = skill.lower()
        if sl not in cv_lower and sl not in _seen_lower:
            new_skills.append(skill)
            _seen_lower.add(sl)

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

    # ---- Identify keywords that EXIST in CV but need more occurrences ----
    boost_keywords = {}  # keyword -> how many more times to add
    all_jd_kw = (
        jd_keywords.get('skills', []) +
        jd_keywords.get('soft_skills', []) +
        jd_keywords.get('certifications', [])
    )
    for kw in all_jd_kw:
        kw_l = kw.lower()
        jd_count = keyword_freq.get(kw_l, 1)
        cv_count = len(re.findall(re.escape(kw_l), cv_lower))
        # If the JD uses it more than the CV, we need to boost
        if cv_count > 0 and cv_count < jd_count:
            boost_keywords[kw] = max(1, jd_count - cv_count)

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
                _inject_skills_lines(result_lines, skill_cats, new_soft, new_industry, boost_keywords)
                skills_section_done = True
            if in_summary_section and summary_lines:
                _flush_summary(result_lines, summary_lines, new_soft, new_industry, boost_keywords, job_title)
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
                    _flush_summary(result_lines, summary_lines, new_soft, new_industry, boost_keywords, job_title)
                    summary_lines = []
                result_lines.append(line)
                in_summary_section = False
            i += 1
            continue

        # Enhance experience bullets with action verbs AND keyword boosting
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

            # Boost: try to weave a high-frequency keyword into this bullet
            bullet_text = _boost_bullet(bullet_text, boost_keywords)

            # Inject a soft skill naturally into some bullets (Jobscan soft-skills check)
            if new_soft and experience_bullet_count % 3 == 0:
                soft = new_soft.pop(0)
                if soft.lower() not in bullet_text.lower():
                    bullet_text = f"{bullet_text}, demonstrating strong {soft}"

            # Add measurable result if bullet lacks numbers (Jobscan recruiter tip)
            if not re.search(r'\d+', bullet_text):
                bullet_text = _add_measurable_result(bullet_text, experience_bullet_count)

            experience_bullet_count += 1
            result_lines.append(f"• {bullet_text}")
            i += 1
            continue

        # In skills section, boost existing skill lines
        if in_skills_section and stripped.startswith(('•', '- ', '* ')):
            boosted = _boost_skill_line(stripped, boost_keywords)
            result_lines.append(boosted)
            i += 1
            continue

        # Pass through all other lines
        result_lines.append(line)
        i += 1

    # Handle case where summary or skills was the last section
    if summary_lines:
        _flush_summary(result_lines, summary_lines, new_soft, new_industry, boost_keywords, job_title)
    if in_skills_section and not skills_section_done:
        _inject_skills_lines(result_lines, skill_cats, new_soft, new_industry, boost_keywords)

    # If there are certifications to add and no CERTIFICATES section exists
    enhanced = '\n'.join(result_lines)
    if new_certs and 'CERTIFICATES' not in enhanced.upper():
        enhanced += '\n\nCERTIFICATES AND TRAINING\n'
        for cert in new_certs:
            enhanced += f'• {cert}\n'

    return enhanced


def _boost_bullet(bullet_text: str, boost_keywords: Dict[str, int]) -> str:
    """Try to naturally append a keyword that needs more occurrences to a bullet."""
    if not boost_keywords:
        return bullet_text
    # Pick the keyword with the highest remaining deficit
    best_kw = max(boost_keywords, key=boost_keywords.get)
    if boost_keywords[best_kw] <= 0:
        return bullet_text
    # Only add if the keyword isn't already in this bullet
    if best_kw.lower() not in bullet_text.lower():
        bullet_text = f"{bullet_text}, utilizing {best_kw}"
        boost_keywords[best_kw] -= 1
    return bullet_text


def _boost_skill_line(line: str, boost_keywords: Dict[str, int]) -> str:
    """Append keywords that need boosting to an existing skill-category line.
    Only appends if the keyword is contextually related to the line content."""
    if not boost_keywords:
        return line
    additions = []
    line_lower = line.lower()
    for kw, deficit in list(boost_keywords.items()):
        if deficit > 0 and kw.lower() not in line_lower:
            # Only add if at least one word of this skill line is related
            kw_words = set(kw.lower().split())
            line_words = set(re.findall(r'[a-z]+', line_lower))
            if kw_words & line_words:  # share at least one word
                additions.append(kw)
                boost_keywords[kw] -= 1
                if len(additions) >= 1:
                    break
    if additions:
        line = line.rstrip()
        if line.endswith('.'):
            line = line[:-1]
        line += ', ' + ', '.join(additions)
    return line


def _add_measurable_result(bullet_text: str, bullet_index: int) -> str:
    """Add a quantifiable metric to a bullet point that lacks numbers.
    Rotates through contextual result phrases so they don't repeat."""
    metrics = [
        ', resulting in a 30% improvement in efficiency',
        ', reducing processing time by 25%',
        ', improving team productivity by 20%',
        ', supporting 50+ users across the organisation',
        ', decreasing manual effort by 40%',
        ', achieving 99.9% system uptime',
        ', saving approximately 15 hours per week',
        ', handling 100+ requests per day',
        ', cutting turnaround time by 35%',
        ', improving compliance adherence by 45%',
    ]
    # Strip trailing period before appending metric
    text = bullet_text.rstrip('.')
    return text + metrics[bullet_index % len(metrics)]


def _inject_skills_lines(result_lines: list, skill_cats: dict, new_soft: list, new_industry: list, boost_keywords: dict = None):
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
    # Add a "Key Competencies" line with boosted keywords for frequency
    if boost_keywords:
        boost_list = [kw for kw, deficit in boost_keywords.items() if deficit > 0]
        if boost_list:
            result_lines.append(f"• Key Competencies: {', '.join(boost_list[:10])}")
            for kw in boost_list[:10]:
                if kw in boost_keywords:
                    boost_keywords[kw] = max(0, boost_keywords[kw] - 1)


def _flush_summary(result_lines: list, summary_lines: list, new_soft: list, new_industry: list, boost_keywords: dict = None, job_title: str = ''):
    """Flush enhanced summary with injected job title, keywords, and boosted frequency."""
    summary_text = ' '.join(summary_lines)

    # ---- Inject exact job title (critical for Jobscan "Job Title Match") ----
    if job_title and job_title.lower() not in summary_text.lower():
        # Prepend the job title naturally; use period separator to avoid mangling capitalisation
        summary_text = f"Results-driven {job_title}. {summary_text}" if summary_text else f"Results-driven {job_title}."

    additions = []
    if new_soft:
        additions.extend(new_soft[:5])
    if new_industry:
        additions.extend(new_industry[:5])
    if additions:
        summary_text += f" Demonstrated expertise in {', '.join(additions)}."
    # Boost high-frequency keywords by weaving them into the summary
    if boost_keywords:
        boost_phrases = []
        for kw, deficit in list(boost_keywords.items()):
            if deficit > 0 and kw.lower() not in summary_text.lower():
                boost_phrases.append(kw)
                boost_keywords[kw] -= 1
        if boost_phrases:
            summary_text += f" Proficient in {', '.join(boost_phrases[:6])} with hands-on experience."
    result_lines.append(summary_text)
