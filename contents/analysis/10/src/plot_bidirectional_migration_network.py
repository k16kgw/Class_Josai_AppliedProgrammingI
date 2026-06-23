from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import seaborn as sns


input_path = "data/processed/prefecture_migration_edges_2025.csv"
output_path = "reports/figures/bidirectional_migration_network.png"

plt.rcParams["font.family"] = "Hiragino Sans"
sns.set_theme(style="white", font="Hiragino Sans")
Path("reports/figures").mkdir(parents=True, exist_ok=True)

edge_df = pd.read_csv(input_path)

pair_df = edge_df.copy()

pair_names = pair_df.apply(
    lambda row: sorted([row["転出元"], row["転入先"]]),
    axis=1,
    result_type="expand",
)

pair_df[["都道府県1", "都道府県2"]] = pair_names

undirected_edge_df = (
    pair_df
    .groupby(["都道府県1", "都道府県2"], as_index=False)["移動者数"]
    .sum()
    .rename(columns={"移動者数": "双方向移動者数"})
)

top_df = undirected_edge_df.nlargest(
    20,
    "双方向移動者数",
)

bidirectional_G = nx.from_pandas_edgelist(
    top_df,
    source="都道府県1",
    target="都道府県2",
    edge_attr="双方向移動者数",
    create_using=nx.Graph,
)

pos = nx.spring_layout(
    bidirectional_G,
    weight="双方向移動者数",
    seed=42,
    k=1.2,
)

max_movers = top_df["双方向移動者数"].max()
edge_widths = [
    1 + 6 * data["双方向移動者数"] / max_movers
    for _, _, data in bidirectional_G.edges(data=True)
]

edge_labels = {
    (source, target): f"{data['双方向移動者数']:,}人"
    for source, target, data in bidirectional_G.edges(data=True)
}

fig, ax = plt.subplots(figsize=(14, 11))

nx.draw_networkx_nodes(
    bidirectional_G,
    pos,
    node_color="#66c2a5",
    node_size=1200,
    edgecolors="black",
    ax=ax,
)

nx.draw_networkx_edges(
    bidirectional_G,
    pos,
    width=edge_widths,
    edge_color="#d95f02",
    alpha=0.55,
    ax=ax,
)

nx.draw_networkx_labels(
    bidirectional_G,
    pos,
    font_family="Hiragino Sans",
    font_size=9,
    ax=ax,
)

nx.draw_networkx_edge_labels(
    bidirectional_G,
    pos,
    edge_labels=edge_labels,
    font_family="Hiragino Sans",
    font_size=6,
    rotate=False,
    ax=ax,
)

ax.set_title(
    "都道府県間の双方向人口移動ネットワーク"
    "：往復移動者数上位20組（2025年）"
)
ax.axis("off")

plt.tight_layout()
plt.savefig(output_path, dpi=150)

print("saved:", output_path)
