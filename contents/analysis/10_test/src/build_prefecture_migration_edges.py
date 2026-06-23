from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/raw/prefecture_migration_2025.xlsx")
OUTPUT_PATH = Path("data/processed/prefecture_migration_edges_2025.csv")

PREFECTURES = [
    "北海道",
    "青森県",
    "岩手県",
    "宮城県",
    "秋田県",
    "山形県",
    "福島県",
    "茨城県",
    "栃木県",
    "群馬県",
    "埼玉県",
    "千葉県",
    "東京都",
    "神奈川県",
    "新潟県",
    "富山県",
    "石川県",
    "福井県",
    "山梨県",
    "長野県",
    "岐阜県",
    "静岡県",
    "愛知県",
    "三重県",
    "滋賀県",
    "京都府",
    "大阪府",
    "兵庫県",
    "奈良県",
    "和歌山県",
    "鳥取県",
    "島根県",
    "岡山県",
    "広島県",
    "山口県",
    "徳島県",
    "香川県",
    "愛媛県",
    "高知県",
    "福岡県",
    "佐賀県",
    "長崎県",
    "熊本県",
    "大分県",
    "宮崎県",
    "鹿児島県",
    "沖縄県",
]


def main():
    raw_df = pd.read_excel(INPUT_PATH, header=None, engine="openpyxl")

    destination_columns = [
        column
        for column in raw_df.columns
        if raw_df.iloc[4, column] in PREFECTURES
        and raw_df.iloc[5, column] == "総数"
    ]

    source_df = raw_df[
        (raw_df.iloc[:, 0] == "都道府県間移動者数")
        & (raw_df.iloc[:, 2] == "移動者")
        & (raw_df.iloc[:, 6].isin(PREFECTURES))
    ]

    rows = []

    for _, source_row in source_df.iterrows():
        source = source_row.iloc[6]

        for column in destination_columns:
            target = raw_df.iloc[4, column]
            movers = pd.to_numeric(source_row.iloc[column], errors="coerce")

            if source == target or pd.isna(movers) or movers <= 0:
                continue

            rows.append({
                "年": 2025,
                "転出元": source,
                "転入先": target,
                "移動者数": int(movers),
            })

    edge_df = pd.DataFrame(rows)
    edge_df = edge_df.sort_values(
        ["移動者数", "転出元", "転入先"],
        ascending=[False, True, True],
    ).reset_index(drop=True)

    if set(edge_df["転出元"]) != set(PREFECTURES):
        raise ValueError("転出元に47都道府県がそろっていません")

    if set(edge_df["転入先"]) != set(PREFECTURES):
        raise ValueError("転入先に47都道府県がそろっていません")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    edge_df.to_csv(OUTPUT_PATH, index=False)

    print("行数:", len(edge_df))
    print("都道府県数:", edge_df["転出元"].nunique())
    print("移動者数合計:", edge_df["移動者数"].sum())
    print("saved:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
