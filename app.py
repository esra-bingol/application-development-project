import streamlit as st
import pandas as pd

from functions import (
    extract_pf_matrix_from_df,
    compute_criteria_weights_from_pf,
    compute_alternative_scores_pf,
    pf_score,
    load_all_sheets
)

st.set_page_config(page_title="PF-WENSLO-ARLON Decision Support System", layout="wide")
st.title("PF-WENSLO-ARLON Decision Support System")

# --- Input mode selection
mode = st.radio("Select your input method:", ["📄 Upload from Excel", "✍️ Manual Entry"])

if mode == "📄 Upload from Excel":
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file:
        all_data = load_all_sheets(uploaded_file)

        # Sheet selection
        selected_sheet = st.selectbox("Select Sheet to Preview", list(all_data.keys()))
        st.write("Preview of Selected Sheet")
        st.dataframe(all_data[selected_sheet])

        # TABLE sheet processing
        if "TABLE" in all_data:
            st.subheader("📊 PF Decision Matrix (from TABLE)")
            df_table = all_data["TABLE"]
            pf_matrix = extract_pf_matrix_from_df(df_table)

            # Collect all unique criteria
            criteria = set()
            for alt in pf_matrix.values():
                criteria.update(alt.keys())
            criteria = list(criteria)

            # Aggregate PF values by criterion
            dummy_pf_dict = {
                crit: [pf_matrix[alt][crit] for alt in pf_matrix if crit in pf_matrix[alt]]
                for crit in criteria
            }

            # Compute weights and final scores
            weights = compute_criteria_weights_from_pf(dummy_pf_dict)
            alt_scores = compute_alternative_scores_pf(pf_matrix, weights)

            st.markdown("### ⚖️ Computed Criteria Weights")
            st.json(weights)

            st.markdown("### 🏁 Final Alternative Rankings")
            st.json(alt_scores)

            # Display additional STEP sheets
            st.markdown("---")
            st.markdown("### 📄 Additional STEP Pages")
            for step in [s for s in all_data if s.startswith("STEP")]:
                with st.expander(f"🔍 View {step}"):
                    st.dataframe(all_data[step])

elif mode == "✍️ Manual Entry":
    from manual_input import manual_input_mode
    manual_input_mode()
