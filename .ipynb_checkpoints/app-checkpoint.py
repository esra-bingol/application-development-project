import streamlit as st
import pandas as pd
import numpy as np

# --- Picture Fuzzy Linguistic Mapping ---
linguistic_to_pf = {
    "Very Important": (0.9, 0.05, 0.05),
    "Important": (0.75, 0.15, 0.10),
    "Neither important nor unimportant": (0.5, 0.3, 0.2),
    "Unimportant": (0.3, 0.5, 0.2),
    "Not Important at All": (0.1, 0.8, 0.1),
    "Very Good": (0.9, 0.05, 0.05),
    "Good": (0.75, 0.15, 0.10),
    "Neutral": (0.5, 0.3, 0.2),
    "Bad": (0.25, 0.6, 0.15),
    "Very Bad": (0.1, 0.8, 0.1)
}

# --- PF functions ---
def pf_score(pf):
    return pf[0] - pf[1]

def compute_criteria_weights_manual(values_dict):
    scores = {}
    for k, v in values_dict.items():
        pf = linguistic_to_pf.get(v, (0.5, 0.3, 0.2))
        scores[k] = pf_score(pf)
    total = sum(scores.values())
    return {k: v / total for k, v in scores.items()} if total > 0 else {}

def compute_alternative_scores(df, weights):
    alt_scores = {}
    for index, row in df.iterrows():
        alt_name = row[0]
        values = []
        for i, col in enumerate(df.columns[1:]):
            cell = str(row[col]).split(",")[0]
            pf = linguistic_to_pf.get(cell.strip().title(), (0.5, 0.3, 0.2))
            s = pf_score(pf)
            w = list(weights.values())[i] if i < len(weights) else 0
            values.append(s * w)
        alt_scores[alt_name] = sum(values)
    return dict(sorted(alt_scores.items(), key=lambda item: item[1], reverse=True))

# --- Streamlit state ---
if "risk_analyzed" not in st.session_state:
    st.session_state.risk_analyzed = False
if "weights" not in st.session_state:
    st.session_state.weights = None

# --- UI Section ---
st.title("OHS Risk Analysis - Manual PF-WENSLO + ARLON")

# 1. FORM - RISK CRITERIA INPUT
st.markdown("### 1. Select importance levels for each OHS risk criterion:")

criteria = [
    "Work-related disease risk",
    "Risk of noise-induced hearing loss",
    "Risks from natural disasters (e.g. earthquake, flood)",
    "Risk of exposure to chemicals",
    "Machinery and equipment safety risk",
    "Psychosocial risks (stress, mobbing, etc.)",
    "Risk of ergonomic inconvenience",
    "Risk of electrical hazard",
    "Possibility of fire",
    "Competence in the use of PPE",
    "The level of occupational health and safety training of employees",
    "Identifying hazards in advance and keeping risk analyses up-to-date"
]

options = [
    "Very Important",
    "Important",
    "Neither important nor unimportant",
    "Unimportant",
    "Not Important at All"
]

user_inputs = {}
col1, col2 = st.columns(2)
for i, crit in enumerate(criteria):
    with (col1 if i % 2 == 0 else col2):
        user_inputs[crit] = st.selectbox(crit, options, key=f"crit_{i}")

if st.button("Analyze Risk"):
    weights = compute_criteria_weights_manual(user_inputs)
    st.session_state.weights = weights
    st.session_state.risk_analyzed = True
    st.success("✅ Risk analysis completed.")
    st.json(weights)

# 2. FORM - ALTERNATIVE SOLUTIONS INPUT
st.markdown("---")
st.header("2. Rate OHS Improvement Suggestions")

alternatives = [
    "Making active noise cancelling headphones mandatory in areas with high noise levels",
    "Integrating behavioral safety training programs into on-the-job training",
    "Periodic health screenings for occupational diseases should be carried out twice a year.",
    "Daily exposure monitoring for personnel working with hazardous chemicals",
    "Establishing air-conditioned rest areas for employees exposed to high temperatures",
    "Mandatory safety briefings at the beginning of each shift",
    "Establishing a software system for instant tracking and analysis of accident/breakage reports",
    "Organizing special high risk awareness workshops for new employees",
    "Providing training to all employees once a year with OHS virtual reality (VR) simulation",
    "Implementation of rotation system in jobs that carry the risk of occupational diseases",
    "Implementation of an employee reward system based on safety observations",
    "Warning signs placed in areas where work accidents frequently occur should be made illuminated and audible"
]

alt_options = ["Very Good", "Good", "Neutral", "Bad", "Very Bad"]
user_alt_inputs = {}
for i, alt in enumerate(alternatives):
    user_alt_inputs[alt] = st.selectbox(alt, alt_options, key=f"alt_{i}")

if st.button("Evaluate Solutions"):
    if st.session_state.weights:
        alt_df_manual = pd.DataFrame([user_alt_inputs])
        alt_scores = compute_alternative_scores(alt_df_manual, st.session_state.weights)

        st.success("✅ Solution Evaluation Completed")
        st.write("### Ranked Solutions:")
        for i, (name, score) in enumerate(alt_scores.items(), 1):
            st.write(f"**{i}.** {name} — Score: `{score:.4f}`")

        best = next(iter(alt_scores.items()))
        st.markdown(f"""
        ### 🔍 Recommendation:
        Based on your selected importance levels and evaluations,  
        the most effective safety solution is:  
        **✅ _{best[0]}_** (score: `{best[1]:.4f}`)
        """)
    else:
        st.warning("⚠️ Please run the risk analysis first (Step 1).")

