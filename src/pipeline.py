from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression

from .sample_data import PROCESSED_DIR, build_sample_data


@dataclass
class ScreeningArtifacts:
    candidates: pd.DataFrame
    jobs: pd.DataFrame
    metrics: dict


DECISION_ORDER = {"reject": 0, "review": 1, "advance": 2}


def _parse_skills(skills: str) -> set[str]:
    return {item.strip().lower() for item in skills.split(",") if item.strip()}


def _combined_text(candidates: pd.DataFrame, jobs_lookup: dict[str, dict]) -> pd.Series:
    texts: list[str] = []
    for _, row in candidates.iterrows():
        job = jobs_lookup[row["target_job_id"]]
        texts.append(
            f"{row['resume_summary']} skills {row['skills']} "
            f"target {job['title']} required {job['required_skills']} preferred {job['preferred_skills']}"
        )
    return pd.Series(texts)


def _rule_based_signals(candidates: pd.DataFrame, jobs: pd.DataFrame) -> pd.DataFrame:
    jobs_lookup = jobs.set_index("job_id").to_dict(orient="index")
    rows: list[dict] = []
    for _, row in candidates.iterrows():
        job = jobs_lookup[row["target_job_id"]]
        candidate_skills = _parse_skills(row["skills"])
        required = _parse_skills(job["required_skills"])
        preferred = _parse_skills(job["preferred_skills"])
        required_match = len(candidate_skills & required) / max(len(required), 1)
        preferred_match = len(candidate_skills & preferred) / max(len(preferred), 1)
        location_match = 1 if row["current_location"] == job["location"] or job["location"] == "remote" else 0
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "required_match_ratio": round(required_match, 4),
                "preferred_match_ratio": round(preferred_match, 4),
                "location_match": location_match,
                "years_experience": row["years_experience"],
            }
        )
    return pd.DataFrame(rows)


def run_screening_pipeline() -> ScreeningArtifacts:
    jobs, candidates = build_sample_data()
    jobs_lookup = jobs.set_index("job_id").to_dict(orient="index")

    signals = _rule_based_signals(candidates, jobs)
    candidates = candidates.merge(signals, on="candidate_id", how="left")

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    text_matrix = vectorizer.fit_transform(_combined_text(candidates, jobs_lookup))
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(candidates["ground_truth_decision"])

    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    model.fit(text_matrix, y)
    predicted = label_encoder.inverse_transform(model.predict(text_matrix))

    candidates["predicted_decision"] = predicted
    probabilities = model.predict_proba(text_matrix)
    classes = label_encoder.classes_
    candidates["advance_probability"] = probabilities[:, list(classes).index("advance")] if "advance" in classes else 0.0
    candidates["review_probability"] = probabilities[:, list(classes).index("review")] if "review" in classes else 0.0
    candidates["matched_job_title"] = candidates["target_job_id"].map(jobs.set_index("job_id")["title"])
    candidates["recommended_next_step"] = candidates["predicted_decision"].map(
        {
            "advance": "schedule recruiter screening",
            "review": "send to recruiter for manual review",
            "reject": "archive with feedback template",
        }
    )
    candidates["requires_human_review"] = candidates["predicted_decision"].map({"advance": 1, "review": 1, "reject": 0})
    candidates["candidate_summary"] = candidates.apply(
        lambda row: (
            f"{row['name']} matched {row['matched_job_title']} with "
            f"{row['required_match_ratio'] * 100:.0f}% of required skills and "
            f"{row['advance_probability'] * 100:.1f}% probability of advancing."
        ),
        axis=1,
    )

    accuracy = accuracy_score(candidates["ground_truth_decision"], candidates["predicted_decision"])
    macro_f1 = f1_score(candidates["ground_truth_decision"], candidates["predicted_decision"], average="macro")
    metrics = {
        "candidates_processed": int(len(candidates)),
        "decision_accuracy": round(float(accuracy), 4),
        "decision_macro_f1": round(float(macro_f1), 4),
        "advance_recommended": int((candidates["predicted_decision"] == "advance").sum()),
        "manual_review_queue": int((candidates["requires_human_review"] == 1).sum()),
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    candidates.to_csv(PROCESSED_DIR / "screening_predictions.csv", index=False)
    pd.DataFrame([metrics]).to_csv(PROCESSED_DIR / "metrics.csv", index=False)

    return ScreeningArtifacts(candidates=candidates, jobs=jobs, metrics=metrics)

