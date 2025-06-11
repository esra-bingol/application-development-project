import pandas as pd

def load_all_sheets(file_path):
    xlsx = pd.ExcelFile(file_path)
    data = {}
    for sheet in xlsx.sheet_names:
        df = xlsx.parse(sheet)
        data[sheet.strip()] = df.dropna(how='all')
    return data


def extract_pf_matrix_from_df(df):
    # Satır 3 (index=2) başlık satırı
    df.columns = df.iloc[2]
    df = df[3:].reset_index(drop=True)

    matrix = {}
    for i, row in df.iterrows():
        alt_name = str(row.iloc[0]).strip()

        # Alternatif adı geçersizse atla
        if not alt_name or alt_name.lower().startswith("step") or alt_name.lower() == "none":
            continue

        matrix[alt_name] = {}

        for j in range(1, len(row) - 2, 3):  # 3'erli bloklar
            crit = str(df.columns[j]).strip()
            try:
                rho = float(row.iloc[j])
                rho_bar = float(row.iloc[j + 1])
                sigma = float(row.iloc[j + 2])

                if pd.isna(rho) or pd.isna(rho_bar) or pd.isna(sigma):
                    continue

                matrix[alt_name][crit] = (rho, rho_bar, sigma)
            except Exception as e:
                continue  # Boş/hatalı değer varsa pas geç

    return matrix
 

def pf_score(pf):
    return pf[0] - pf[2]

def compute_criteria_weights_from_pf(pf_dict):
    scores = {}
    for criterion, pf_values in pf_dict.items():
        score = sum([pf_score(pf) for pf in pf_values]) / len(pf_values)
        scores[criterion] = score
    total = sum(scores.values())
    return {k: v / total for k, v in scores.items()}

def compute_alternative_scores_pf(pf_matrix, weights):
    alt_scores = {}
    for alt_name, crit_values in pf_matrix.items():
        score = 0
        for crit, pf in crit_values.items():
            w = weights.get(crit, 0)
            score += pf_score(pf) * w
        alt_scores[alt_name] = score
    return dict(sorted(alt_scores.items(), key=lambda x: x[1], reverse=True))
