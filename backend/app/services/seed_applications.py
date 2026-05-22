"""
Sample application data for demo/development.

Seeds realistic candidate applications with pre-filled AI screening results
so the UI has data to display without requiring a Gemini API key.

Idempotent — matched by (name, job title) so duplicates are never created.
"""

from sqlmodel import Session, select

from app.db.database import engine
from app.models import Application, Job

# Each entry: (job_title, candidate_name, email, phone, resume_text,
#               ai_score, ai_summary, ai_strengths, ai_weaknesses,
#               ai_recommendation)
DEMO_APPLICATIONS = [
    # ── Senior Full-Stack Developer @ TechNova Solutions ──────────
    {
        "job_title": "Senior Full-Stack Developer",
        "job_company": "TechNova Solutions",
        "candidates": [
            {
                "name": "Alice Chen",
                "email": "alice.chen@email.com",
                "phone": "+1-415-555-0101",
                "resume_filename": "alice_chen_resume.pdf",
                "resume_text": (
                    "Alice Chen — Senior Software Engineer\n"
                    "San Francisco, CA | alice.chen@email.com\n\n"
                    "EXPERIENCE\n"
                    "Senior Full-Stack Engineer, Stripe (2020–Present)\n"
                    "- Led migration of merchant dashboard from Angular to Next.js/React, "
                    "serving 50k+ daily users\n"
                    "- Designed and built real-time payment analytics API with Node.js and PostgreSQL\n"
                    "- Implemented CI/CD pipelines with GitHub Actions and Docker\n"
                    "- Mentored 4 junior engineers across 2 product teams\n\n"
                    "Full-Stack Developer, Twilio (2017–2020)\n"
                    "- Built React component library used across 8 internal tools\n"
                    "- Developed REST APIs with Express.js and TypeScript\n"
                    "- Managed deployments on AWS (ECS, RDS, S3)\n\n"
                    "EDUCATION\n"
                    "B.S. Computer Science, UC Berkeley, 2017\n\n"
                    "SKILLS\n"
                    "React, Next.js, TypeScript, Node.js, PostgreSQL, AWS, Docker, "
                    "GraphQL, Redis, CI/CD"
                ),
                "ai_score": 92,
                "ai_summary": (
                    "Exceptional full-stack candidate with 7+ years of experience at "
                    "top-tier companies. Strong React/Next.js and Node.js expertise "
                    "with proven leadership and cloud infrastructure skills."
                ),
                "ai_strengths": [
                    "Deep React/Next.js experience at scale (50k+ DAU)",
                    "Strong backend skills with Node.js and PostgreSQL",
                    "Proven mentorship and technical leadership",
                    "Hands-on CI/CD and Docker experience",
                    "Top-tier company pedigree (Stripe, Twilio)",
                ],
                "ai_weaknesses": [
                    "No explicit GCP experience mentioned",
                    "Could benefit from more architectural design examples",
                ],
                "ai_recommendation": "Strong Hire",
            },
            {
                "name": "Marcus Rivera",
                "email": "m.rivera@email.com",
                "phone": "+1-512-555-0202",
                "resume_filename": "marcus_rivera_resume.pdf",
                "resume_text": (
                    "Marcus Rivera — Web Developer\n"
                    "Austin, TX | m.rivera@email.com\n\n"
                    "EXPERIENCE\n"
                    "Frontend Developer, Freelance (2021–Present)\n"
                    "- Built websites for small businesses using React and Tailwind CSS\n"
                    "- Integrated Stripe payment processing for 3 e-commerce clients\n\n"
                    "Junior Developer, LocalTech Agency (2019–2021)\n"
                    "- Developed WordPress themes and plugins\n"
                    "- Some experience with jQuery and PHP\n\n"
                    "EDUCATION\n"
                    "Web Development Bootcamp, General Assembly, 2019\n\n"
                    "SKILLS\n"
                    "React, HTML/CSS, Tailwind, JavaScript, WordPress, PHP"
                ),
                "ai_score": 38,
                "ai_summary": (
                    "Junior-level candidate with mainly frontend freelance experience. "
                    "Lacks the required 5+ years and has no backend, TypeScript, or "
                    "cloud infrastructure experience needed for this senior role."
                ),
                "ai_strengths": [
                    "Familiar with React basics",
                    "Self-driven freelance experience",
                ],
                "ai_weaknesses": [
                    "Only ~3 years of experience vs. 5+ required",
                    "No TypeScript, Node.js, or PostgreSQL experience",
                    "No cloud or DevOps skills",
                    "No team collaboration experience at scale",
                ],
                "ai_recommendation": "No Hire",
            },
            {
                "name": "Priya Sharma",
                "email": "priya.sharma@email.com",
                "phone": "+1-650-555-0303",
                "resume_filename": "priya_sharma_resume.pdf",
                "resume_text": (
                    "Priya Sharma — Software Engineer\n"
                    "Mountain View, CA | priya.sharma@email.com\n\n"
                    "EXPERIENCE\n"
                    "Software Engineer II, Google (2021–Present)\n"
                    "- Developed internal tools using Angular and Java backend services\n"
                    "- Built data pipelines with Apache Beam on GCP\n\n"
                    "Software Engineer, Infosys (2018–2021)\n"
                    "- Full-stack development with React and Spring Boot\n"
                    "- Worked with MySQL and MongoDB databases\n"
                    "- Participated in Agile sprints and code reviews\n\n"
                    "EDUCATION\n"
                    "M.S. Computer Science, Stanford University, 2018\n"
                    "B.Tech Information Technology, IIT Delhi, 2016\n\n"
                    "SKILLS\n"
                    "React, Angular, Java, Spring Boot, Python, GCP, MySQL, "
                    "MongoDB, Docker, Kubernetes"
                ),
                "ai_score": 72,
                "ai_summary": (
                    "Solid engineer with full-stack experience and strong educational "
                    "background. Has React skills but primary stack is Java/Angular "
                    "rather than the required TypeScript/Node.js. GCP experience is "
                    "a plus."
                ),
                "ai_strengths": [
                    "Strong educational credentials (Stanford, IIT)",
                    "Full-stack experience across frontend and backend",
                    "GCP and containerization experience",
                    "Experience at top tech company (Google)",
                ],
                "ai_weaknesses": [
                    "Primary backend is Java, not Node.js/TypeScript",
                    "Angular-focused rather than React/Next.js",
                    "No explicit REST API design ownership",
                ],
                "ai_recommendation": "Maybe",
            },
        ],
    },
    # ── Machine Learning Engineer @ DataMind AI ───────────────────
    {
        "job_title": "Machine Learning Engineer",
        "job_company": "DataMind AI",
        "candidates": [
            {
                "name": "Dr. James Okafor",
                "email": "j.okafor@email.com",
                "phone": "+1-212-555-0404",
                "resume_filename": "james_okafor_resume.pdf",
                "resume_text": (
                    "Dr. James Okafor — Machine Learning Researcher\n"
                    "New York, NY | j.okafor@email.com\n\n"
                    "EXPERIENCE\n"
                    "ML Research Scientist, Meta AI (2021–Present)\n"
                    "- Published 6 papers at NeurIPS, ICML, and ACL on large language models\n"
                    "- Developed novel attention mechanism reducing inference cost by 40%\n"
                    "- Led team of 3 researchers on multilingual NLP project\n\n"
                    "ML Engineer, Amazon (2019–2021)\n"
                    "- Built recommendation models serving 100M+ users\n"
                    "- Deployed models using SageMaker and MLflow\n"
                    "- Optimized training pipelines reducing costs by 30%\n\n"
                    "EDUCATION\n"
                    "Ph.D. Computer Science (NLP focus), Columbia University, 2019\n"
                    "B.S. Mathematics, MIT, 2014\n\n"
                    "SKILLS\n"
                    "Python, PyTorch, TensorFlow, Transformers, MLflow, "
                    "Kubeflow, AWS SageMaker, CUDA, distributed training"
                ),
                "ai_score": 96,
                "ai_summary": (
                    "Outstanding ML candidate with PhD, published research, and "
                    "production ML experience at top companies. Deep expertise in "
                    "NLP and large-scale recommendation systems with strong MLOps skills."
                ),
                "ai_strengths": [
                    "PhD with 6 published papers at top-tier venues",
                    "Production ML at massive scale (100M+ users)",
                    "Both PyTorch and TensorFlow proficiency",
                    "MLOps experience with MLflow and Kubeflow",
                    "Research leadership and mentorship",
                ],
                "ai_weaknesses": [
                    "May be overqualified — could be looking for a pure research role",
                ],
                "ai_recommendation": "Strong Hire",
            },
            {
                "name": "Sophie Laurent",
                "email": "sophie.l@email.com",
                "resume_filename": "sophie_laurent_resume.pdf",
                "resume_text": (
                    "Sophie Laurent — Data Scientist\n"
                    "Brooklyn, NY | sophie.l@email.com\n\n"
                    "EXPERIENCE\n"
                    "Data Scientist, Spotify (2022–Present)\n"
                    "- Built playlist recommendation features using collaborative filtering\n"
                    "- Conducted A/B tests and statistical analysis for product decisions\n"
                    "- Experience with scikit-learn, pandas, and basic PyTorch\n\n"
                    "Data Analyst, Deloitte (2020–2022)\n"
                    "- Created dashboards and reports using SQL and Tableau\n"
                    "- Applied basic ML models for client churn prediction\n\n"
                    "EDUCATION\n"
                    "M.S. Data Science, NYU, 2020\n"
                    "B.A. Statistics, McGill University, 2018\n\n"
                    "SKILLS\n"
                    "Python, scikit-learn, pandas, SQL, Tableau, basic PyTorch, "
                    "A/B testing, statistics"
                ),
                "ai_score": 55,
                "ai_summary": (
                    "Competent data scientist with some ML exposure but lacks the "
                    "deep ML engineering experience required. Limited PyTorch/TensorFlow "
                    "proficiency and no MLOps or deployment experience."
                ),
                "ai_strengths": [
                    "Strong statistical and analytical foundation",
                    "Production data science experience at Spotify",
                    "Good educational background (NYU M.S.)",
                ],
                "ai_weaknesses": [
                    "Limited deep learning experience",
                    "No MLOps or model deployment skills",
                    "No published research",
                    "More data scientist than ML engineer profile",
                ],
                "ai_recommendation": "Maybe",
            },
        ],
    },
    # ── Backend Python Engineer @ Northwind Labs ──────────────────
    {
        "job_title": "Backend Python Engineer",
        "job_company": "Northwind Labs",
        "candidates": [
            {
                "name": "Erik Lindqvist",
                "email": "erik.lindqvist@email.com",
                "phone": "+46-70-555-0505",
                "resume_filename": "erik_lindqvist_resume.pdf",
                "resume_text": (
                    "Erik Lindqvist — Senior Backend Engineer\n"
                    "Stockholm, Sweden | erik.lindqvist@email.com\n\n"
                    "EXPERIENCE\n"
                    "Senior Python Engineer, Klarna (2020–Present)\n"
                    "- Designed and built payment processing APIs with FastAPI\n"
                    "- Managed PostgreSQL databases handling 10M+ transactions/day\n"
                    "- Implemented event-driven architecture with Kafka\n"
                    "- Led PCI-DSS compliance audit for backend services\n\n"
                    "Backend Developer, iZettle (2017–2020)\n"
                    "- Built RESTful APIs with Django and DRF\n"
                    "- Async task processing with Celery and RabbitMQ\n"
                    "- Wrote complex SQL queries and managed migrations\n\n"
                    "EDUCATION\n"
                    "M.S. Computer Science, KTH Royal Institute of Technology, 2017\n\n"
                    "SKILLS\n"
                    "Python, FastAPI, Django, PostgreSQL, Kafka, RabbitMQ, "
                    "Redis, Docker, async/await, OpenTelemetry, PCI-DSS"
                ),
                "ai_score": 95,
                "ai_summary": (
                    "Near-perfect match for this role. Deep FastAPI and PostgreSQL "
                    "expertise in fintech with Kafka experience and PCI compliance "
                    "background. Based in Stockholm — ideal location fit."
                ),
                "ai_strengths": [
                    "FastAPI expert with production fintech experience",
                    "PostgreSQL at scale (10M+ txns/day)",
                    "Kafka and RabbitMQ message queue experience",
                    "PCI-DSS compliance — directly relevant bonus",
                    "OpenTelemetry experience matches bonus criteria",
                ],
                "ai_weaknesses": [
                    "No Rust experience mentioned",
                ],
                "ai_recommendation": "Strong Hire",
            },
            {
                "name": "Tomoko Watanabe",
                "email": "t.watanabe@email.com",
                "resume_filename": "tomoko_watanabe_resume.pdf",
                "resume_text": (
                    "Tomoko Watanabe — Software Engineer\n"
                    "Tokyo, Japan | t.watanabe@email.com\n\n"
                    "EXPERIENCE\n"
                    "Backend Engineer, Mercari (2021–Present)\n"
                    "- Built microservices in Go for marketplace platform\n"
                    "- Experience with gRPC, Protocol Buffers, and Kubernetes\n"
                    "- Some Python scripting for data pipeline automation\n\n"
                    "Software Engineer, Rakuten (2019–2021)\n"
                    "- Java backend development with Spring Framework\n"
                    "- MySQL database management and optimization\n\n"
                    "EDUCATION\n"
                    "B.S. Information Engineering, University of Tokyo, 2019\n\n"
                    "SKILLS\n"
                    "Go, Java, Python (basic), gRPC, Kubernetes, MySQL, "
                    "Docker, Protocol Buffers"
                ),
                "ai_score": 42,
                "ai_summary": (
                    "Strong backend engineer but primarily in Go and Java, not Python. "
                    "Minimal Python experience and no FastAPI/Django, PostgreSQL, or "
                    "message queue skills. Would need significant ramp-up time."
                ),
                "ai_strengths": [
                    "Solid backend engineering fundamentals",
                    "Kubernetes and containerization experience",
                    "Good educational background",
                ],
                "ai_weaknesses": [
                    "Python is not primary language — only basic scripting",
                    "No FastAPI or Django experience",
                    "No PostgreSQL or async Python experience",
                    "No message queue experience (Kafka/RabbitMQ)",
                ],
                "ai_recommendation": "No Hire",
            },
            {
                "name": "Lucia Fernandez",
                "email": "lucia.f@email.com",
                "phone": "+34-622-555-0606",
                "resume_filename": "lucia_fernandez_resume.pdf",
                "resume_text": (
                    "Lucia Fernandez — Python Developer\n"
                    "Barcelona, Spain | lucia.f@email.com\n\n"
                    "EXPERIENCE\n"
                    "Python Engineer, Typeform (2020–Present)\n"
                    "- Built async APIs with FastAPI and SQLAlchemy\n"
                    "- Managed PostgreSQL with Alembic migrations\n"
                    "- Integrated with SQS for async job processing\n"
                    "- Implemented distributed tracing with Jaeger\n\n"
                    "Junior Python Developer, Glovo (2018–2020)\n"
                    "- Backend development with Flask\n"
                    "- Basic PostgreSQL queries and schema design\n\n"
                    "EDUCATION\n"
                    "B.S. Computer Engineering, UPC Barcelona, 2018\n\n"
                    "SKILLS\n"
                    "Python, FastAPI, Flask, PostgreSQL, SQLAlchemy, SQS, "
                    "Redis, Docker, asyncio, Jaeger"
                ),
                "ai_score": 82,
                "ai_summary": (
                    "Strong Python backend candidate with FastAPI and PostgreSQL "
                    "experience. Has async Python and SQS queue experience. Slightly "
                    "less senior than ideal but solid technical match."
                ),
                "ai_strengths": [
                    "FastAPI and async Python in production",
                    "PostgreSQL with proper migration tooling",
                    "SQS message queue experience",
                    "Distributed tracing experience (Jaeger)",
                ],
                "ai_weaknesses": [
                    "~4 years experience — on the lower end of requirements",
                    "No Kafka or RabbitMQ (only SQS)",
                    "No exposure to regulated environments",
                ],
                "ai_recommendation": "Hire",
            },
        ],
    },
    # ── DevOps Engineer @ CloudScale Inc. ─────────────────────────
    {
        "job_title": "DevOps Engineer",
        "job_company": "CloudScale Inc.",
        "candidates": [
            {
                "name": "Daniel Kim",
                "email": "d.kim@email.com",
                "phone": "+1-206-555-0707",
                "resume_filename": "daniel_kim_resume.pdf",
                "resume_text": (
                    "Daniel Kim — Senior DevOps Engineer\n"
                    "Seattle, WA | d.kim@email.com\n\n"
                    "EXPERIENCE\n"
                    "Senior DevOps Engineer, Microsoft Azure (2019–Present)\n"
                    "- Managed 200+ node Kubernetes clusters across 3 regions\n"
                    "- Built infrastructure-as-code with Terraform and ARM templates\n"
                    "- Designed CI/CD pipelines with Azure DevOps and GitHub Actions\n"
                    "- Implemented Prometheus/Grafana monitoring stack\n\n"
                    "DevOps Engineer, Tableau (2016–2019)\n"
                    "- AWS infrastructure management with CloudFormation\n"
                    "- Ansible automation for server provisioning\n"
                    "- On-call rotation and incident response\n\n"
                    "EDUCATION\n"
                    "B.S. Computer Science, University of Washington, 2016\n\n"
                    "SKILLS\n"
                    "AWS, Azure, GCP, Kubernetes, Terraform, Ansible, Docker, "
                    "Prometheus, Grafana, Python, Bash, GitHub Actions"
                ),
                "ai_score": 94,
                "ai_summary": (
                    "Excellent DevOps candidate with 8+ years across all major "
                    "clouds. Deep Kubernetes, Terraform, and monitoring expertise. "
                    "Seattle-based — perfect location fit for this contract."
                ),
                "ai_strengths": [
                    "Multi-cloud expertise (AWS, Azure, GCP)",
                    "Large-scale Kubernetes management (200+ nodes)",
                    "Terraform and Ansible IaC proficiency",
                    "Prometheus/Grafana monitoring experience",
                    "Strong scripting skills (Python, Bash)",
                ],
                "ai_weaknesses": [
                    "May prefer full-time over contract engagement",
                ],
                "ai_recommendation": "Strong Hire",
            },
        ],
    },
    # ── Product Manager – AI Products @ Helix AI ─────────────────
    {
        "job_title": "Product Manager – AI Products",
        "job_company": "Helix AI",
        "candidates": [
            {
                "name": "Amara Osei",
                "email": "amara.osei@email.com",
                "resume_filename": "amara_osei_resume.pdf",
                "resume_text": (
                    "Amara Osei — Senior Product Manager\n"
                    "London, UK | amara.osei@email.com\n\n"
                    "EXPERIENCE\n"
                    "Senior PM, DeepMind (2021–Present)\n"
                    "- Owned roadmap for AI safety evaluation tools used by 50+ researchers\n"
                    "- Shipped 3 major product launches, growing adoption from 0 to 200 orgs\n"
                    "- Wrote technical specs and prototyped with LLM APIs\n"
                    "- Led cross-functional team of 12 (eng, research, design)\n\n"
                    "Product Manager, Palantir (2018–2021)\n"
                    "- Managed enterprise data platform used by government clients\n"
                    "- Prior role as software engineer (2 years) before transitioning to PM\n\n"
                    "EDUCATION\n"
                    "M.S. Computer Science, Imperial College London, 2016\n"
                    "B.S. Mathematics, University of Ghana, 2014\n\n"
                    "SKILLS\n"
                    "Product strategy, technical writing, LLM APIs, PRDs, "
                    "user research, A/B testing, SQL, Python"
                ),
                "ai_score": 91,
                "ai_summary": (
                    "Outstanding PM candidate with direct AI product experience at "
                    "DeepMind. Has the rare combination of technical IC engineering "
                    "background, LLM API prototyping skills, and proven product launches."
                ),
                "ai_strengths": [
                    "Direct AI/ML product management at DeepMind",
                    "Prior IC engineering experience — strong technical credibility",
                    "Hands-on with LLM APIs and technical specs",
                    "Proven product launches with measurable adoption growth",
                    "London-based — perfect location fit",
                ],
                "ai_weaknesses": [
                    "Enterprise-heavy background — may need to adjust to startup pace",
                ],
                "ai_recommendation": "Strong Hire",
            },
            {
                "name": "Tom Bradley",
                "email": "tom.b@email.com",
                "resume_filename": "tom_bradley_resume.pdf",
                "resume_text": (
                    "Tom Bradley — Product Manager\n"
                    "Manchester, UK | tom.b@email.com\n\n"
                    "EXPERIENCE\n"
                    "Product Manager, Booking.com (2020–Present)\n"
                    "- Managed search and discovery features for hotel listings\n"
                    "- Ran A/B experiments improving conversion by 12%\n"
                    "- Coordinated with 3 engineering teams across time zones\n\n"
                    "Associate PM, BBC (2018–2020)\n"
                    "- Worked on iPlayer streaming features\n"
                    "- Gathered user requirements and wrote user stories\n\n"
                    "EDUCATION\n"
                    "MBA, Manchester Business School, 2018\n"
                    "B.A. English Literature, Durham University, 2015\n\n"
                    "SKILLS\n"
                    "Product management, Jira, A/B testing, user stories, "
                    "stakeholder management, Figma"
                ),
                "ai_score": 45,
                "ai_summary": (
                    "Decent PM experience but lacks the technical depth and AI/ML "
                    "product background required. No engineering experience, no "
                    "ability to prototype with LLM APIs, and no technical product work."
                ),
                "ai_strengths": [
                    "Solid A/B testing and experimentation skills",
                    "Cross-team coordination experience",
                    "UK-based — good location fit",
                ],
                "ai_weaknesses": [
                    "No AI/ML product experience",
                    "No technical or engineering background",
                    "Cannot prototype with LLM APIs or read technical papers",
                    "Only 4 years of PM experience vs. 5+ required",
                ],
                "ai_recommendation": "No Hire",
            },
        ],
    },
]


def seed_sample_applications() -> int:
    """Insert demo applications with pre-filled screening results.

    Returns the number of applications inserted.
    """
    inserted = 0

    with Session(engine) as session:
        for job_group in DEMO_APPLICATIONS:
            # Look up the job by title + company
            job = session.exec(
                select(Job).where(
                    Job.title == job_group["job_title"],
                    Job.company == job_group["job_company"],
                )
            ).first()

            if not job:
                continue

            for c in job_group["candidates"]:
                # Skip if this candidate already exists for this job
                already_exists = session.exec(
                    select(Application).where(
                        Application.job_id == job.id,
                        Application.name == c["name"],
                    )
                ).first()
                if already_exists:
                    continue

                app = Application(
                    job_id=job.id,
                    name=c["name"],
                    email=c["email"],
                    phone=c.get("phone"),
                    resume_filename=c["resume_filename"],
                    resume_text=c["resume_text"],
                    ai_score=c["ai_score"],
                    ai_summary=c["ai_summary"],
                    ai_strengths=c["ai_strengths"],
                    ai_weaknesses=c["ai_weaknesses"],
                    ai_recommendation=c["ai_recommendation"],
                    screened=True,
                )
                session.add(app)
                job.applications_count += 1
                inserted += 1

        session.commit()

    return inserted


if __name__ == "__main__":
    from app.db.database import init_db

    init_db()
    count = seed_sample_applications()
    print(f"Seeded {count} sample application(s).")
