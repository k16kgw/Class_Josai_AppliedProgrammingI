import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


edge_path = "data/processed/prefecture_migration_edges_2025.csv"
population_path = "data/raw/dashboard_population.json"
region_path = "data/raw/dashboard_regions.json"
output_path = "reports/figures/prefecture_migration_rate.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(edge_path)

outflow_df = (
    edge_df
    .groupby("転出元", as_index=False)["移動者数"]
    .sum()
    .rename(columns={
        "転出元": "都道府県",
        "移動者数": "流出者数",
    })
)

with open(population_path, encoding="utf-8") as f:
    population_data = json.load(f)

population_objects = (
    population_data["GET_STATS"]
    ["STATISTICAL_DATA"]["DATA_INF"]["DATA_OBJ"]
)

population_df = pd.DataFrame([
    {
        "地域コード": obj["VALUE"]["@regionCode"],
        "総人口": int(obj["VALUE"]["$"]),
    }
    for obj in population_objects
])

with open(region_path, encoding="utf-8") as f:
    region_data = json.load(f)

region_classes = (
    region_data["GET_META_REGION_INF"]["METADATA_INF"]
    ["CLASS_INF"]["CLASS_OBJ"][0]["CLASS"]
)

region_df = pd.DataFrame([
    {
        "地域コード": region["@regionCode"],
        "都道府県": region["@name"],
    }
    for region in region_classes
])

rate_df = (
    outflow_df
    .merge(region_df, on="都道府県")
    .merge(population_df, on="地域コード")
)

# 人口は2020年，人口移動は2025年であるため，厳密な同年比較ではない．
rate_df["転出率"] = (
    rate_df["流出者数"]
    / rate_df["総人口"]
    * 100
)

top10_df = rate_df.nlargest(10, "転出率")

fig, ax = plt.subplots(figsize=(8, 5))

sns.barplot(
    data=top10_df,
    x="転出率",
    y="都道府県",
    color="steelblue",
    ax=ax,
)

ax.set_title("都道府県人口に対する都道府県間転出者数の割合")
ax.set_xlabel("転出率（%，人口は2020年，移動は2025年）")
ax.set_ylabel("都道府県")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
