from pathlib import Path

import pandas as pd
import plotly.express as px


input_path = "data/processed/my_forecast_map_data.csv"
output_path = "reports/figures/my_forecast_other_value_map.html"

Path("reports/figures").mkdir(parents=True, exist_ok=True)

map_df = pd.read_csv(input_path)
plot_df = map_df.dropna(
    subset=["緯度", "経度", "最大降水確率", "信頼度A件数"]
).copy()

# 0件の地点も地図上に表示できるように1を加える．
plot_df["信頼度A表示サイズ"] = plot_df["信頼度A件数"] + 1

fig = px.scatter_map(
    plot_df,
    lat="緯度",
    lon="経度",
    color="最大降水確率",
    size="信頼度A表示サイズ",
    hover_name="地域名",
    hover_data=[
        "発表区域名",
        "細分地域名",
        "アメダス地点名",
        "平均降水確率",
        "最大降水確率",
        "信頼度A件数",
        "標高",
    ],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=5,
    height=650,
)

fig.update_layout(
    title="週間予報：最大降水確率と信頼度A件数",
    map_style="open-street-map",
)

fig.write_html(output_path)

print("saved:", output_path)
