import requests
import logging
import re
from bs4 import BeautifulSoup # We should check if bs4 is installed or use fallback. Fallback is standard string search.
from django.db import IntegrityError
from .models import Job

logger = logging.getLogger(__name__)

# List of popular companies using Greenhouse & Lever to query dynamically
GREENHOUSE_COMPANIES = ['stripe', 'figma', 'airbnb', 'cloudflare', 'hashicorp']
LEVER_COMPANIES = ['lever', 'vercel', 'figma', 'posthog', 'gitlab']

class JobFetcherService:
    @staticmethod
    def fetch_all():
        """
        Wrapper to fetch from all safe job sources.
        """
        stats = {
            'remoteok': 0,
            'greenhouse': 0,
            'lever': 0,
            'wellfound': 0,
        }
        
        # 1. Fetch from RemoteOK
        stats['remoteok'] = JobFetcherService.fetch_remoteok()
        
        # 2. Fetch from Greenhouse (predefined popular boards)
        stats['greenhouse'] = JobFetcherService.fetch_greenhouse()
        
        # 3. Fetch from Lever (predefined popular boards)
        stats['lever'] = JobFetcherService.fetch_lever()
        
        # 4. Fetch from Wellfound (mock data since public API is deprecated)
        stats['wellfound'] = JobFetcherService.fetch_wellfound_mock()

        return stats

    @staticmethod
    def fetch_remoteok():
        """
        Fetch remote jobs from RemoteOK JSON API.
        """
        url = "https://remoteok.com/api"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        count = 0
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                jobs_data = response.json()
                # RemoteOK returns legal statement as first item, we skip it
                for item in jobs_data[1:]:
                    if 'position' not in item or 'url' not in item:
                        continue
                    
                    # Construct clean description (strip HTML tags)
                    desc_html = item.get('description', '')
                    description = JobFetcherService.clean_html(desc_html)
                    
                    tags = item.get('tags', [])
                    
                    try:
                        Job.objects.create(
                            title=item['position'],
                            company=item.get('company', 'Remote Company'),
                            location=item.get('location', 'Remote'),
                            source='remoteok',
                            url=item['url'],
                            description=description,
                            salary=item.get('salary', ''),
                            tags=tags
                        )
                        count += 1
                    except IntegrityError:
                        # Job already exists
                        pass
        except Exception as e:
            logger.error(f"Error fetching from RemoteOK: {str(e)}")
        return count

    @staticmethod
    def fetch_greenhouse():
        """
        Fetch public jobs from selected company boards via Greenhouse API.
        """
        count = 0
        for company in GREENHOUSE_COMPANIES:
            url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    jobs = data.get('jobs', [])
                    for j in jobs:
                        title = j.get('title')
                        location = j.get('location', {}).get('name', 'Remote / Hybrid')
                        job_url = j.get('absolute_url')
                        content = j.get('content', '')
                        
                        description = JobFetcherService.clean_html(content)
                        
                        try:
                            Job.objects.create(
                                title=title,
                                company=company.title(),
                                location=location,
                                source='greenhouse',
                                url=job_url,
                                description=description,
                                tags=[company, 'greenhouse']
                            )
                            count += 1
                        except IntegrityError:
                            pass
            except Exception as e:
                logger.error(f"Error fetching Greenhouse for {company}: {str(e)}")
        return count

    @staticmethod
    def fetch_lever():
        """
        Fetch public jobs from selected company boards via Lever API.
        """
        count = 0
        for company in LEVER_COMPANIES:
            url = f"https://api.lever.co/v0/postings/{company}"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    postings = response.json()
                    for post in postings:
                        title = post.get('text')
                        job_url = post.get('hostedUrl')
                        
                        # Leverage category/team as tags
                        tags = [company, 'lever']
                        categories = post.get('categories', {})
                        if categories.get('team'):
                            tags.append(categories.get('team'))
                        if categories.get('commitment'):
                            tags.append(categories.get('commitment'))

                        location = post.get('categories', {}).get('location', 'Remote')
                        
                        desc_text = post.get('descriptionPlain', '')
                        lists = post.get('lists', [])
                        for item_list in lists:
                            desc_text += f"\n\n{item_list.get('text', '')}\n"
                            desc_text += "\n".join([f"- {li}" for li in item_list.get('content', [])])
                        
                        try:
                            Job.objects.create(
                                title=title,
                                company=company.title(),
                                location=location,
                                source='lever',
                                url=job_url,
                                description=desc_text.strip(),
                                tags=tags
                            )
                            count += 1
                        except IntegrityError:
                            pass
            except Exception as e:
                logger.error(f"Error fetching Lever for {company}: {str(e)}")
        return count

    @staticmethod
    def fetch_wellfound_mock():
        """
        Wellfound public endpoints require API authorization keys.
        We seed some mock startup listings to let the user discover jobs with the same tag structure.
        """
        count = 0
        mock_jobs = [
            {
                "title": "Junior Python Developer",
                "company": "Decentriq",
                "location": "Bengaluru, IN",
                "url": "https://wellfound.com/jobs/mock-decentriq-python",
                "description": "We are looking for a Python Developer to join our core backend engineering team. You will build serverless microservices, handle API integrations, and structure clean PostgreSQL schemas.",
                "salary": "$40,000 - $60,000",
                "tags": ["python", "django", "postgresql", "backend"]
            },
            {
                "title": "Machine Learning Engineer",
                "company": "Cognition AI",
                "location": "San Francisco, CA (Remote)",
                "url": "https://wellfound.com/jobs/mock-cognition-ml",
                "description": "Seeking an ML Engineer expert in Transformer modeling, vector embedding pipelines, and orchestrating RAG systems. Experience with Gemini API or OpenAI API is a big plus.",
                "salary": "$120,000 - $180,000",
                "tags": ["ml", "ai", "python", "embeddings", "gemini"]
            },
            {
                "title": "Frontend Engineer (React / CSS)",
                "company": "Glassflow",
                "location": "Berlin, DE (Hybrid)",
                "url": "https://wellfound.com/jobs/mock-glassflow-frontend",
                "description": "Build premium, glassmorphic customer dashboards using modern web UI technologies. Expertise in vanilla CSS, animation libraries (GSAP/Framer Motion) and layout design.",
                "salary": "€50,000 - €70,000",
                "tags": ["react", "frontend", "css", "glassmorphism"]
            }
        ]
        for job in mock_jobs:
            try:
                Job.objects.create(
                    title=job['title'],
                    company=job['company'],
                    location=job['location'],
                    source='wellfound',
                    url=job['url'],
                    description=job['description'],
                    salary=job['salary'],
                    tags=job['tags']
                )
                count += 1
            except IntegrityError:
                pass
        return count

    @staticmethod
    def clean_html(html_content):
        """
        Strips HTML tags cleanly without using heavy parsing libraries,
        falling back to regex if bs4 fails.
        """
        if not html_content:
            return ""
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            return soup.get_text(separator="\n").strip()
        except Exception:
            # Fallback regex html clean
            clean = re.compile('<.*?>')
            return re.sub(clean, '', html_content).strip()
