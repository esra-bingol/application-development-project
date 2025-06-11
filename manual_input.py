import streamlit as st
import pandas as pd

def manual_input_mode():
    st.subheader("✍️ Manual PF-WENSLO + ARLON Input")

    # Step 1
    st.subheader("1. Define Matrix Dimensions")
    num_criteria = st.number_input("Number of Criteria", min_value=1, max_value=20, value=3)
    num_alternatives = st.number_input("Number of Alternatives", min_value=1, max_value=20, value=3)

    # Step 2
    st.subheader("2. Enter Criteria Names and Weights")
    criteria_names = []
    criteria_weights = []
    for i in range(num_criteria):
        col1, col2 = st.columns(2)
        with col1:
            crit = st.text_input(f"Criterion {i+1} Name", key=f"crit_name_{i}")
        with col2:
            weight = st.number_input(f"Weight for {crit}", min_value=0.0, max_value=1.0, value=1.0, key=f"weight_{i}")
        criteria_names.append(crit)
        criteria_weights.append(weight)

    # Normalize weights
    if sum(criteria_weights) > 0:
        criteria_weights = [w / sum(criteria_weights) for w in criteria_weights]

    # Step 3
    st.subheader("3. Enter PF Values (ρ, ρ̄, σ) for each Alternative and Criterion")
    alternatives = []
    manual_pf_matrix = {}

    for i in range(num_alternatives):
        alt_name = st.text_input(f"Alternative {i+1} Name", key=f"alt_name_{i}")
        alternatives.append(alt_name)
        manual_pf_matrix[alt_name] = {}

        for j, crit in enumerate(criteria_names):
            st.markdown(f"**{alt_name} – {crit}**")
            rho = st.number_input(f"ρ (True Membership)", 0.0, 1.0, 0.5, 0.01, key=f"rho_{i}_{j}")
            rho_bar = st.number_input(f"ρ̄ (False Membership)", 0.0, 1.0, 0.3, 0.01, key=f"rhobar_{i}_{j}")
            sigma = st.number_input(f"σ (Neutral)", 0.0, 1.0, 0.2, 0.01, key=f"sigma_{i}_{j}")
            manual_pf_matrix[alt_name][crit] = (rho, rho_bar, sigma)

    # Score function
    def pf_score(pf):
        return pf[0] - pf[2]  # ρ - σ

    # Compute results
    def compute_manual_scores(pf_matrix, weights):
        alt_scores = {}
        detailed_scores = {}

        for alt in pf_matrix:
            total = 0
            details = []
            for i, crit in enumerate(pf_matrix[alt]):
                w = weights[i]
                pf = pf_matrix[alt][crit]
                score = pf_score(pf)
                weighted_score = w * score
                total += weighted_score
                details.append((crit, weighted_score))
            alt_scores[alt] = total
            detailed_scores[alt] = details

        return dict(sorted(alt_scores.items(), key=lambda x: x[1], reverse=True)), detailed_scores

    # Step 4 - Trigger
    if st.button("Compute Ranking"):
        result, details = compute_manual_scores(manual_pf_matrix, criteria_weights)
        st.success("✅ Ranking Computed!")

        # Show main scores
        st.markdown("### 🧮 Final Scores")
        st.write(result)

        # Bar chart with proper labels
        st.markdown("### 📊 Score Bar Chart (Manual Entry)")
        df_scores = pd.DataFrame(list(result.items()), columns=["Alternative", "Score"])
        st.bar_chart(df_scores.set_index("Alternative"))

        # Show contributions
        for alt in details:
            st.markdown(f"#### 🔍 Criterion Contributions for `{alt}`")
            df = pd.DataFrame(details[alt], columns=["Criterion", "Weighted Score"])
            df = df.sort_values(by="Weighted Score", ascending=False).reset_index(drop=True)
            st.table(df)

            top_crit = df.iloc[0]
            st.success(f"🏆 Most impactful criterion: **{top_crit['Criterion']}** (Score: {top_crit['Weighted Score']:.3f})")
