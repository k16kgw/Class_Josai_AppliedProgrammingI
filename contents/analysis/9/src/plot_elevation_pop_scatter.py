from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


input_path = "data/processed/my_forecast_map_data.csv"
output_path = "reports/figures/elevation_pop_scatter.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="whitegrid", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

map_df = pd.read_csv(input_path)
plot_df = map_df.dropna(
    subset=["標高", "平均降水確率", "最大降水確率", "発表区域名"]
).copy()

fig, ax = plt.subplots(figsize=(8, 6))

sns.scatterplot(
    data=plot_df,
    x="標高",
    y="平均降水確率",
    hue="発表区域名",
    size="最大降水確率",
    sizes=(50, 250),
    alpha=0.8,
    ax=ax,
)

ax.set_title("アメダス地点の標高と平均降水確率")
ax.set_xlabel("標高（m）")
ax.set_ylabel("平均降水確率（%）")
ax.legend(
    title="発表区域・最大降水確率",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
)

plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches="tight")

print("saved:", output_path)
