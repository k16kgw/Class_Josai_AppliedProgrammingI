import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


edge_path = "data/processed/prefecture_migration_edges_2025.csv"
coordinate_path = "data/processed/prefecture_capital_coordinates.csv"
boundary_path = "data/processed/japan_prefectures.geojson"
output_path = "reports/figures/migration_network_map.html"

Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(edge_path)
coordinate_df = pd.read_csv(coordinate_path)

with open(boundary_path, encoding="utf-8") as f:
    boundary_geojson = json.load(f)

coordinate_lookup = coordinate_df.set_index("都道府県")
top_edges_df = edge_df.nlargest(40, "移動者数")
max_movers = top_edges_df["移動者数"].max()

fig = go.Figure()

prefecture_ids = [
    feature["properties"]["id"]
    for feature in boundary_geojson["features"]
]

fig.add_trace(
    go.Choroplethmap(
        geojson=boundary_geojson,
        locations=prefecture_ids,
        z=[0] * len(prefecture_ids),
        featureidkey="properties.id",
        colorscale=[
            [0, "#f8fafc"],
            [1, "#f8fafc"],
        ],
        marker={
            "line": {
                "color": "#94a3b8",
                "width": 0.8,
            }
        },
        showscale=False,
        hoverinfo="skip",
    )
)

for _, row in top_edges_df.iterrows():
    source = coordinate_lookup.loc[row["転出元"]]
    target = coordinate_lookup.loc[row["転入先"]]
    label = (
        f"{row['転出元']}→{row['転入先']}<br>"
        f"移動者数：{row['移動者数']:,}人"
    )

    fig.add_trace(
        go.Scattermap(
            lat=[source["緯度"], target["緯度"]],
            lon=[source["経度"], target["経度"]],
            mode="lines",
            line={
                "width": 0.5 + 5 * row["移動者数"] / max_movers,
                "color": "rgba(80, 80, 80, 0.45)",
            },
            text=[label, label],
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        )
    )

inflow_df = (
    edge_df
    .groupby("転入先", as_index=False)["移動者数"]
    .sum()
    .rename(columns={
        "転入先": "都道府県",
        "移動者数": "流入者数",
    })
    .merge(coordinate_df, on="都道府県")
)

inflow_df["表示サイズ"] = (
    8
    + 22
    * inflow_df["流入者数"]
    / inflow_df["流入者数"].max()
)

fig.add_trace(
    go.Scattermap(
        lat=inflow_df["緯度"],
        lon=inflow_df["経度"],
        mode="markers",
        marker={
            "size": inflow_df["表示サイズ"],
            "color": inflow_df["流入者数"],
            "colorscale": "viridis",
            "showscale": True,
            "colorbar": {"title": "流入者数"},
        },
        text=(
            inflow_df["都道府県"]
            + "<br>代表地点："
            + inflow_df["代表地点"]
            + "<br>流入者数："
            + inflow_df["流入者数"].map("{:,}".format)
            + "人"
        ),
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    )
)

fig.update_layout(
    title="日本地図上の都道府県間人口移動ネットワーク（上位40組）",
    map={
        "style": "white-bg",
        "center": {"lat": 36.2, "lon": 137.0},
        "zoom": 4,
    },
    height=750,
    margin={"l": 0, "r": 0, "t": 50, "b": 0},
    annotations=[
        {
            "text": "県境データ：地球地図日本を変換・簡略化",
            "x": 0.01,
            "y": 0.01,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 10, "color": "#475569"},
        }
    ],
)

fig.write_html(output_path)

print("saved:", output_path)
