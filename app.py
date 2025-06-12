import streamlit as st
import pandas as pd
from functions import (
    extract_pf_matrix_from_df,
    compute_criteria_weights_from_pf,
    compute_alternative_scores_pf,
    load_all_sheets,
)
from manual_input import manual_input_mode

st.set_page_config(page_title="PF-WENSLO-ARLON Decision Support System", layout="wide")

st.markdown("""
<style>
    h1 {
        text-align: center;
        color: #FFBF00;
        font-size: 42px;
        font-weight: 800;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #444;
        padding-top: 10px;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)


st.markdown("<h1>🛡️ PF-WENSLO-ARLON Decision Support System</h1>", unsafe_allow_html=True)

st.markdown("""
<div class='subtitle'>
Welcome to our intelligent decision support system built to address complex <b>Occupational Health & Safety</b> challenges.
<br>This tool utilizes the <b style="color:#f4aa00;">PF-WENSLO + ARLON</b> methodology to <br>analyze and rank risk factors with precision, transparency, and advanced multi-criteria evaluation.
</div>
""", unsafe_allow_html=True)


st.markdown("### 🛠️ Select your input method:")
mode = st.radio(
    label="Choose input mode",
    options=["📄 Upload from Excel", "✍️ Manual Entry"],
    index=0,
    label_visibility="visible"  
)

# ----------------- Excel Yükleme Modu -----------------
if mode == "📄 Upload from Excel":
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    if uploaded_file:
        all_data = load_all_sheets(uploaded_file)

        selected_sheet = st.selectbox("Select Sheet to Preview", list(all_data.keys()))
        st.write("Preview of Selected Sheet")
        st.dataframe(all_data[selected_sheet])

        if selected_sheet in all_data:
            st.markdown("### 📊 PF Decision Matrix")
            df_table = all_data[selected_sheet]
            pf_matrix = extract_pf_matrix_from_df(df_table)

            # Kriterleri çıkar ve listele
            criteria = set()
            for alt in pf_matrix.values():
                criteria.update(alt.keys())
            criteria = list(criteria)

            st.markdown("### 📌 Criteria Used")
            st.write(criteria)

            # Ağırlık ve skor hesapla
            dummy_pf_dict = {
                crit: [pf_matrix[alt][crit] for alt in pf_matrix if crit in pf_matrix[alt]]
                for crit in criteria
            }

            weights = compute_criteria_weights_from_pf(dummy_pf_dict)
            alt_scores = compute_alternative_scores_pf(pf_matrix, weights)

            st.markdown("### ⚖️ Computed Criteria Weights")
            st.dataframe(pd.DataFrame(weights.items(), columns=["Criterion", "Weight"]))

            # Alternatif puanlarını sırala ve göster
            st.markdown("### 🏁 Final Alternative Rankings")
            sorted_scores = sorted(alt_scores.items(), key=lambda x: x[1], reverse=True)
            ranking_df = pd.DataFrame(sorted_scores, columns=["Alternative", "Score"])
            st.dataframe(ranking_df)

            best = ranking_df.iloc[0]
            st.success(f"🏆 Best Ranked Alternative: **{best['Alternative']}** (Score: {best['Score']:.4f})")
            # 📌 Top 3 Alternatives Table
            top_3_df = ranking_df.head(3).copy()
            top_3_df.index = [1, 2, 3]
            emoji_rank = {1: "🥇", 2: "🥈", 3: "🥉"}
            top_3_df.insert(0, "Rank", top_3_df.index.map(emoji_rank))

            st.markdown("### 🥇 Top 3 Alternatives Based on Model Results")
            st.dataframe(top_3_df, use_container_width=True)


            st.markdown("### 📊 Bar Chart of Scores")
            st.bar_chart(ranking_df.set_index("Alternative")["Score"])

            if selected_sheet == "SAYFA 11":
                st.markdown("---")
                st.markdown("### 🏆 Top 5 Alternatives from Model Results")

                # Alternatif isimlerini eşleştir (A kolonundaki A1, A2 vs ile açıklama)
                alt_names = all_data["SAYFA 11"].iloc[:, [3, 1]].dropna()
                alt_names.columns = ["Alternative", "Name"]
                alt_names["Alternative"] = alt_names["Alternative"].astype(str)

                top_5_model = ranking_df.head(5).copy()
                top_5_model["Alternative"] = top_5_model["Alternative"].astype(str)

                top_5_model_named = pd.merge(top_5_model, alt_names, on="Alternative", how="left")
                top_5_model_named = top_5_model_named[["Alternative", "Name", "Score"]]

                # Tabloyu göster
                st.dataframe(top_5_model_named)



                st.markdown("---")
                st.markdown("### 🧾 Top 5 Based on Survey Sheet (Excel Ranking)")

                sayfa11_df = all_data["SAYFA 11"]
                top5_from_excel = sayfa11_df.iloc[:, [0, 1]].copy()
                top5_from_excel.columns = ["Rank", "Description"]
                top5_from_excel = top5_from_excel.dropna()
                top5_from_excel["Rank"] = pd.to_numeric(top5_from_excel["Rank"], errors="coerce")
                top5_from_excel = top5_from_excel[top5_from_excel["Rank"] <= 5].sort_values("Rank")

                st.dataframe(top5_from_excel)

                st.markdown("📌 This table shows the top 5 criteria as ranked by survey participants in the Excel sheet.")

# ----------------- Manuel Giriş -----------------
elif mode == "✍️ Manual Entry":
    manual_input_mode()
