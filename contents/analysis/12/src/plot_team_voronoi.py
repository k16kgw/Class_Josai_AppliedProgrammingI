from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

from animate_alfheim_tracking import draw_pitch


input_path = Path("data/processed/alfheim_tracking_5fps.csv")
output_path = Path("reports/figures/team_voronoi_frame.png")

tracking_df = pd.read_csv(input_path, parse_dates=["timestamp"])
frame_df = (
    tracking_df[tracking_df["frame"] == 0]
    .sort_values("tag_id")
    .reset_index(drop=True)
)
player_points = frame_df[["x_pos", "y_pos"]].to_numpy()

dx = 0.25
dy = 0.25
x_centers = np.arange(dx / 2, 105, dx)
y_centers = np.arange(dy / 2, 68, dy)
grid_x, grid_y = np.meshgrid(x_centers, y_centers)

distance_squared = (
    (grid_x[:, :, None] - player_points[:, 0]) ** 2
    + (grid_y[:, :, None] - player_points[:, 1]) ** 2
)
nearest_player = distance_squared.argmin(axis=2)

voronoi_colors = plt.colormaps["tab10"](
    np.arange(len(frame_df))
)
voronoi_cmap = ListedColormap(voronoi_colors)

plt.rcParams["font.family"] = "Hiragino Sans"
fig, ax = plt.subplots(figsize=(10, 6.5))
draw_pitch(ax)

ax.imshow(
    nearest_player,
    extent=(0, 105, 0, 68),
    origin="lower",
    cmap=voronoi_cmap,
    alpha=0.42,
    interpolation="nearest",
    zorder=1,
)
ax.scatter(
    frame_df["x_pos"],
    frame_df["y_pos"],
    c=np.arange(len(frame_df)),
    cmap=voronoi_cmap,
    s=110,
    edgecolors="black",
    zorder=3,
)

for row in frame_df.itertuples():
    ax.text(
        row.x_pos,
        row.y_pos,
        str(row.tag_id),
        ha="center",
        va="center",
        fontsize=8,
        color="white",
        weight="bold",
        zorder=4,
    )

ax.set_title("ホームチームのボロノイ図：経過時間0.0秒")
output_path.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches="tight")
plt.close(fig)

print("saved:", output_path)
