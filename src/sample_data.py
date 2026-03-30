from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


JOB_ROWS = [
    {
        "job_id": "J001",
        "title": "Applied AI Engineer",
        "seniority": "mid",
        "location": "remote",
        "required_skills": "python,llm,rag,api,sql,mlops",
        "preferred_skills": "langchain,n8n,streamlit,vector-db,fastapi",
        "description": "Build AI applications with Python, LLM orchestration, retrieval pipelines, API integration and MLOps practices.",
    },
    {
        "job_id": "J002",
        "title": "Data Engineer",
        "seniority": "mid",
        "location": "hybrid",
        "required_skills": "python,spark,sql,etl,airflow,cloud",
        "preferred_skills": "dbt,databricks,kafka,terraform",
        "description": "Design data pipelines, orchestrate ETL jobs and manage scalable analytics platforms.",
    },
]


CANDIDATE_ROWS = [
    {
        "candidate_id": "C001",
        "name": "Ana Martins",
        "source": "linkedin",
        "years_experience": 6,
        "current_location": "remote",
        "resume_summary": "Python engineer with experience in LLM applications, RAG, APIs, SQL and Streamlit dashboards. Worked on evaluation and workflow automation.",
        "skills": "python,llm,rag,api,sql,streamlit,evaluation,n8n",
        "target_job_id": "J001",
        "ground_truth_decision": "advance",
    },
    {
        "candidate_id": "C002",
        "name": "Bruno Silva",
        "source": "referral",
        "years_experience": 4,
        "current_location": "hybrid",
        "resume_summary": "Data engineer focused on Spark, ETL, Airflow and SQL. Some exposure to cloud platforms and dashboards.",
        "skills": "python,spark,sql,etl,airflow,cloud",
        "target_job_id": "J002",
        "ground_truth_decision": "advance",
    },
    {
        "candidate_id": "C003",
        "name": "Carla Nunes",
        "source": "email",
        "years_experience": 2,
        "current_location": "remote",
        "resume_summary": "Junior backend developer with Python, REST APIs and some machine learning coursework. Limited production exposure.",
        "skills": "python,api,ml,git",
        "target_job_id": "J001",
        "ground_truth_decision": "review",
    },
    {
        "candidate_id": "C004",
        "name": "Diego Costa",
        "source": "linkedin",
        "years_experience": 7,
        "current_location": "onsite",
        "resume_summary": "Senior product manager with experience in roadmap planning, analytics and stakeholder management.",
        "skills": "product,analytics,communication,roadmap",
        "target_job_id": "J001",
        "ground_truth_decision": "reject",
    },
    {
        "candidate_id": "C005",
        "name": "Elisa Rocha",
        "source": "referral",
        "years_experience": 5,
        "current_location": "hybrid",
        "resume_summary": "Engineer with Databricks, dbt, SQL, Python and some Kafka usage in data platforms.",
        "skills": "python,sql,databricks,dbt,etl,cloud,kafka",
        "target_job_id": "J002",
        "ground_truth_decision": "advance",
    },
    {
        "candidate_id": "C006",
        "name": "Felipe Gomes",
        "source": "web_form",
        "years_experience": 3,
        "current_location": "remote",
        "resume_summary": "Automation specialist using n8n, APIs, CRM integrations, low-code tools and operational workflows.",
        "skills": "n8n,api,automation,crm,webhooks",
        "target_job_id": "J001",
        "ground_truth_decision": "review",
    },
]


def ensure_directories() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def build_sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    ensure_directories()
    jobs = pd.DataFrame(JOB_ROWS)
    candidates = pd.DataFrame(CANDIDATE_ROWS)
    jobs.to_csv(RAW_DIR / "jobs.csv", index=False)
    candidates.to_csv(RAW_DIR / "candidates.csv", index=False)
    return jobs, candidates

