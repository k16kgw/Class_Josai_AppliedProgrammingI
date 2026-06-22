from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


input_path = "data/processed/prefecture_migration_edges_2025.csv"
output_path = "reports/figures/migration_asymmetry.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(input_path)

reverse_df = edge_df.rename(columns={
    "転出元": "転入先",
    "転入先": "転出元",
    "移動者数": "逆方向移動者数",
})

comparison_df = edge_df.merge(
    reverse_df[["転出元", "転入先", "逆方向移動者数"]],
    on=["転出元", "転入先"],
)

# 同じ都道府県ペアを1回だけ残す．
comparison_df = comparison_df[
    comparison_df["転出元"] < comparison_df["転入先"]
].copy()

comparison_df["移動差"] = (
    comparison_df["移動者数"]
    - comparison_df["逆方向移動者数"]
)
comparison_df["差の絶対値"] = comparison_df["移動差"].abs()


def make_direction_label(row):
    if row["移動差"] >= 0:
        return f"{row['転出元']}→{row['転入先']}"
    return f"{row['転入先']}→{row['転出元']}"


comparison_df["多い方向"] = comparison_df.apply(
    make_direction_label,
    axis=1,
)

top10_df = comparison_df.nlargest(10, "差の絶対値")

fig, ax = plt.subplots(figsize=(9, 6))

sns.barplot(
    data=top10_df,
    x="差の絶対値",
    y="多い方向",
    color="darkorange",
    ax=ax,
)

ax.set_title("都道府県間人口移動の方向差が大きい組合せ（2025年）")
ax.set_xlabel("双方向の移動者数の差（人）")
ax.set_ylabel("移動者数が多い方向")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
