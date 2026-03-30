from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.pipeline import run_screening_pipeline


st.set_page_config(page_title="Candidate Screening with n8n", page_icon="🧑‍💼", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #08111f; color: #ecf3ff; }
    [data-testid="stSidebar"] { background: #0d1728; }
    </style>
    """,
    unsafe_allow_html=True,
)

artifacts = run_screening_pipeline()
candidates = artifacts.candidates.copy()

st.title("Candidate Screening Workflow with n8n")
st.caption(
    "Workflow de intake de candidatos, matching com vaga, score inicial, aprovação humana e logging de recrutamento."
)

with st.expander("Arquitetura técnica", expanded=False):
    st.markdown(
        """
        1. Trigger de candidatura via formulário ou webhook.
        2. Parsing do currículo e normalização do perfil.
        3. Matching com requisitos da vaga.
        4. Score inicial de aderência.
        5. Human-in-the-loop para avanço ou rejeição.
        6. Atualização do ATS / CRM / banco de recrutamento.
        """
    )
    st.markdown(
        """
        **Ferramentas**
        - `n8n` para orquestração do workflow.
        - `Webhook`, `Google Drive`, `Slack`, `Gmail`, `Notion/Sheets/Postgres`.
        - `TF-IDF + Logistic Regression` como baseline reproduzível.
        - `Streamlit` para inspeção técnica do pipeline.
        """
    )
    st.markdown(
        """
        **Sinais calculados no baseline**
        - `required_match_ratio`: cobertura dos requisitos mandatórios da vaga.
        - `preferred_match_ratio`: cobertura das skills desejáveis.
        - `location_match`: aderência entre localidade do candidato e modelo de trabalho da vaga.
        - `advance_probability`: probabilidade estimada de avanço na triagem inicial.
        - `requires_human_review`: flag operacional usada para encaminhar revisão do recrutador.
        """
    )

col1, col2, col3, col4 = st.columns(4)
col1.metric("Candidatos processados", str(artifacts.metrics["candidates_processed"]))
col2.metric("Acurácia da decisão", f"{artifacts.metrics['decision_accuracy'] * 100:.1f}%")
col3.metric("Recomendados para avanço", str(artifacts.metrics["advance_recommended"]))
col4.metric("Fila de revisão humana", str(artifacts.metrics["manual_review_queue"]))

tab1, tab2, tab3, tab4 = st.tabs(["Pipeline de screening", "Vagas", "Aprovação humana", "Métricas"])

with tab1:
    st.subheader("Candidatos triados")
    st.dataframe(
        candidates[
            [
                "candidate_id",
                "name",
                "matched_job_title",
                "required_match_ratio",
                "preferred_match_ratio",
                "advance_probability",
                "predicted_decision",
                "recommended_next_step",
            ]
        ],
        use_container_width=True,
    )
    selected = st.selectbox("Selecione um candidato para inspeção", candidates["candidate_id"].tolist())
    row = candidates[candidates["candidate_id"] == selected].iloc[0]
    st.markdown("**Resumo do candidato selecionado**")
    st.write(row["candidate_summary"])
    st.write(f"**Resumo do currículo:** {row['resume_summary']}")
    st.markdown("**Feature vector operacional**")
    st.json(
        {
            "required_match_ratio": float(row["required_match_ratio"]),
            "preferred_match_ratio": float(row["preferred_match_ratio"]),
            "location_match": int(row["location_match"]),
            "years_experience": int(row["years_experience"]),
            "advance_probability": float(row["advance_probability"]),
            "review_probability": float(row["review_probability"]),
            "predicted_decision": row["predicted_decision"],
            "requires_human_review": int(row["requires_human_review"]),
        }
    )

with tab2:
    st.subheader("Vagas cadastradas")
    st.dataframe(artifacts.jobs, use_container_width=True)
    st.markdown(
        """
        **Contrato informacional da vaga**
        - `required_skills` funciona como hard constraint para o screening inicial.
        - `preferred_skills` funciona como booster de aderência e ranking.
        - `description` entra no contexto semântico do vetor `TF-IDF`.
        """
    )
    dist = candidates["predicted_decision"].value_counts().reset_index()
    dist.columns = ["decision", "count"]
    fig = px.bar(dist, x="decision", y="count", color="decision", title="Distribuição das decisões previstas")
    fig.update_layout(paper_bgcolor="#08111f", plot_bgcolor="#08111f", font={"color": "#ecf3ff"}, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Fila de revisão humana")
    review_queue = candidates[candidates["requires_human_review"] == 1].copy()
    st.dataframe(
        review_queue[
            [
                "candidate_id",
                "name",
                "matched_job_title",
                "predicted_decision",
                "advance_probability",
                "recommended_next_step",
            ]
        ],
        use_container_width=True,
    )
    st.markdown(
        """
        **Como o HITL entra no fluxo**
        - candidatos com decisão `advance` ou `review` seguem para revisão do recrutador;
        - o revisor recebe score, matching e resumo do currículo;
        - a decisão final segue para agenda, shortlist ou encerramento.
        """
    )
    st.markdown(
        """
        **Racional de controle**
        - o workflow privilegia *human approval* nos candidatos de maior potencial para evitar falso negativo e garantir rastreabilidade;
        - em um cenário produtivo, a aprovação humana também permitiria coletar feedback supervisionado para re-treinamento do classificador.
        """
    )

with tab4:
    st.subheader("Métricas do baseline")
    metrics_df = pd.DataFrame([artifacts.metrics]).T.reset_index()
    metrics_df.columns = ["metric", "value"]
    st.dataframe(metrics_df, use_container_width=True)
    st.caption(
        "Essas métricas validam o desenho do workflow e a camada de matching. Em produção, o fluxo pode incorporar parsing real de currículo, embeddings e ATS integration."
    )
    st.markdown(
        """
        **Leitura técnica**
        - as métricas atuais são calculadas em um conjunto `demo controlled dataset`, pequeno e sem split holdout;
        - o objetivo é validar contrato de dados, roteamento do workflow e integração entre classificação, decisão e aprovação humana;
        - em produção, a camada de model serving deve ser avaliada com `train/validation/test`, *calibration*, *precision@top-k* e métricas de funnel.
        """
    )
