"""
Demo data seeding.

``seed_if_empty`` ensures every entry in ``DEMO_JOBS`` exists in the database.
It is idempotent — each demo entry is matched by (title, company) and only
inserted if missing. This means:

  • Fresh install        → all demo jobs are seeded.
  • Adding a new entry   → only the new one gets inserted on next boot;
                            existing jobs (including admin-created ones)
                            are untouched.
  • Deleting a demo job  → it will come back on the next restart.
                            Remove the entry from ``DEMO_JOBS`` to permanently
                            retire it.
"""

from sqlmodel import Session, select

from app.db.database import engine
from app.models import Job, JobCreate

DEMO_JOBS: list[JobCreate] = [
    JobCreate(
        title="Senior Full-Stack Developer",
        company="TechNova Solutions",
        location="San Francisco, CA (Remote)",
        job_type="Full-time",
        description=(
            "We are looking for an experienced Full-Stack Developer to join our "
            "engineering team. You will be responsible for designing, developing, "
            "and maintaining web applications using modern frameworks. You'll work "
            "closely with product managers, designers, and other engineers to "
            "deliver high-quality software."
        ),
        requirements=(
            "5+ years experience with React/Next.js and Node.js. Strong knowledge "
            "of TypeScript, PostgreSQL, and REST APIs. Experience with cloud "
            "services (AWS/GCP). Familiarity with CI/CD pipelines and Docker. "
            "Excellent problem-solving skills."
        ),
        salary_range="$140,000 – $180,000",
    ),
    JobCreate(
        title="Machine Learning Engineer",
        company="DataMind AI",
        location="New York, NY",
        job_type="Full-time",
        description=(
            "Join our ML team to build and deploy machine learning models that "
            "power intelligent products. You'll work on NLP, computer vision, and "
            "recommendation systems at scale. We value innovation, collaboration, "
            "and a data-driven approach."
        ),
        requirements=(
            "MS/PhD in Computer Science or related field. 3+ years experience "
            "with Python, TensorFlow/PyTorch. Strong understanding of ML "
            "algorithms, deep learning, and statistics. Experience with MLOps "
            "tools (MLflow, Kubeflow). Published research is a plus."
        ),
        salary_range="$160,000 – $200,000",
    ),
    JobCreate(
        title="UI/UX Designer",
        company="CreativeFlow Studio",
        location="Austin, TX (Hybrid)",
        job_type="Full-time",
        description=(
            "We're seeking a talented UI/UX Designer to create beautiful, "
            "intuitive interfaces for our SaaS products. You'll conduct user "
            "research, create wireframes and prototypes, and collaborate with "
            "developers to bring designs to life."
        ),
        requirements=(
            "3+ years of UI/UX design experience. Proficiency in Figma and "
            "Adobe Creative Suite. Strong portfolio showcasing web and mobile "
            "designs. Experience with design systems and component libraries. "
            "Understanding of accessibility standards (WCAG)."
        ),
        salary_range="$100,000 – $130,000",
    ),
    JobCreate(
        title="DevOps Engineer",
        company="CloudScale Inc.",
        location="Seattle, WA (Remote)",
        job_type="Contract",
        description=(
            "We need a DevOps Engineer to manage and optimize our cloud "
            "infrastructure. You'll build CI/CD pipelines, manage Kubernetes "
            "clusters, and ensure high availability of our services. This is a "
            "12-month contract with potential for extension."
        ),
        requirements=(
            "4+ years of DevOps experience. Expert knowledge of AWS/GCP/Azure. "
            "Hands-on experience with Kubernetes, Terraform, and Ansible. "
            "Strong scripting skills (Bash, Python). Experience with monitoring "
            "tools (Prometheus, Grafana)."
        ),
        salary_range="$70 – $90/hr",
    ),
    JobCreate(
        title="Backend Python Engineer",
        company="Northwind Labs",
        location="Stockholm, Sweden (Remote-friendly)",
        job_type="Full-time",
        description=(
            "Join a small, senior team building a high-throughput data platform "
            "for fintech clients. You'll own backend services end-to-end — from "
            "API design and data modelling through to deployment and on-call. "
            "Expect deep technical problems, code review culture, and minimal "
            "meetings."
        ),
        requirements=(
            "4+ years of Python in production. Strong with FastAPI or Django, "
            "PostgreSQL, and async I/O. Comfortable writing idiomatic SQL and "
            "reasoning about query plans. Familiarity with message queues "
            "(Kafka, RabbitMQ, or SQS). Bonus: Rust, OpenTelemetry, or "
            "experience with regulated environments (PCI/SOC 2)."
        ),
        salary_range="€75,000 – €100,000",
    ),
    JobCreate(
        title="iOS Mobile Engineer",
        company="Lumen Health",
        location="Toronto, Canada (Hybrid)",
        job_type="Full-time",
        description=(
            "We're hiring an iOS engineer to lead development of our "
            "consumer-facing health companion app, currently used by 200k+ "
            "patients. You'll work directly with designers and clinicians to "
            "ship features that meaningfully improve patient outcomes, owning "
            "everything from architecture to App Store releases."
        ),
        requirements=(
            "4+ years building native iOS apps with Swift and SwiftUI. Solid "
            "understanding of Combine, Swift Concurrency, and modern "
            "architecture patterns (MVVM, TCA, etc.). Shipped at least one app "
            "in the App Store. Experience with HealthKit, secure storage, and "
            "CI/CD (Fastlane / Xcode Cloud) is a plus."
        ),
        salary_range="CAD 120,000 – 150,000",
    ),
    JobCreate(
        title="Product Manager – AI Products",
        company="Helix AI",
        location="London, UK (Remote)",
        job_type="Full-time",
        description=(
            "Drive the roadmap for our enterprise AI product suite, working "
            "closely with research, engineering, and design. You'll talk to "
            "customers weekly, write crisp PRDs, and decide what we build (and "
            "just as importantly, what we don't). This is a senior IC PM role "
            "with significant ownership."
        ),
        requirements=(
            "5+ years of product management experience, at least 2 of which "
            "were on technical / developer or AI/ML products. Strong written "
            "communication and prioritisation skills. Comfortable reading "
            "technical papers, prototyping with LLM APIs, and pushing back on "
            "engineering when needed. Prior IC engineering experience is a "
            "plus, not a must."
        ),
        salary_range="£110,000 – £140,000 + equity",
    ),
    JobCreate(
        title="Cybersecurity Engineer",
        company="Sentinel Systems",
        location="Berlin, Germany (Hybrid)",
        job_type="Full-time",
        description=(
            "Help us harden infrastructure and applications used by "
            "critical-infrastructure customers across the EU. You'll be "
            "embedded with platform and application teams, leading threat "
            "modelling, secure code reviews, and incident response, as well as "
            "shaping our internal security tooling."
        ),
        requirements=(
            "3+ years in an applied security role (AppSec, ProdSec, or "
            "detection engineering). Hands-on with Linux internals, container "
            "security, and at least one cloud (AWS / GCP / Azure). Comfortable "
            "reading and writing Python or Go. Bonus: experience with SIEM "
            "tuning, eBPF, or compliance frameworks (ISO 27001, BSI C5)."
        ),
        salary_range="€85,000 – €110,000",
    ),
]


def seed_if_empty() -> None:
    """Top up the database with any demo jobs that are missing.

    Idempotent — safe to call on every startup.
    """
    with Session(engine) as session:
        for job_data in DEMO_JOBS:
            already_exists = session.exec(
                select(Job).where(
                    Job.title == job_data.title,
                    Job.company == job_data.company,
                )
            ).first()
            if already_exists:
                continue
            session.add(Job(**job_data.model_dump()))
        session.commit()
