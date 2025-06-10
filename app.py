import streamlit as st
import pandas as pd

from functions import (
    extract_pf_matrix_from_df,
    compute_criteria_weights_from_pf,
    compute_alternative_scores_pf,
    pf_score,
    load_all_sheets
)

st.title("PF-WENSLO-ARLON Decision Support System")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    all_data = load_all_sheets(uploaded_file)
    selected_sheet = st.selectbox("Select Sheet to Preview", list(all_data.keys()))
    st.write("Preview of Selected Sheet")
    st.dataframe(all_data[selected_sheet])
if "TABLE" in all_data:
    st.subheader("PF Decision Matrix (from TABLE)")
    df_table = all_data["TABLE"]
    pf_matrix = extract_pf_matrix_from_df(df_table)

    
    criteria = list(next(iter(pf_matrix.values())).keys())

    dummy_pf_dict = {crit: [pf_matrix[alt][crit] for alt in pf_matrix] for crit in criteria}

    weights = compute_criteria_weights_from_pf(dummy_pf_dict)

    st.markdown("### ⚖️ Computed Criteria Weights")
    st.json(weights)

    alt_scores = compute_alternative_scores_pf(pf_matrix, weights)
    st.markdown("### 🏁 Final Alternative Rankings")
    st.json(alt_scores)

    st.markdown("---")
    st.markdown("### 📄 Additional STEP Pages")

for step in [s for s in all_data if s.startswith("STEP")]:
    with st.expander(f"🔍 View {step}"):
        st.dataframe(all_data[step])

