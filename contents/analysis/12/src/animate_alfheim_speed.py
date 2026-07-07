from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import Normalize

from animate_alfheim_tracking import draw_pitch


input_path = Path(
    "data/processed/alfheim_tracking_5fps.csv"
)
output_path = Path(
    "reports/figures/alfheim_tracking_speed.gif"
)
fps = 5

plt.rcParams["font.family"] = "Hiragino Sans"

# 演習2・セル1：前処理済みCSVを読み込む．
tracking_df = pd.read_csv(
    input_path,
    parse_dates=["timestamp"],
)

# 演習4・セル1：選手IDとフレーム番号を準備する．
player_ids = sorted(tracking_df["tag_id"].unique())
frame_ids = sorted(tracking_df["frame"].unique())

# 演習4・セル2：更新する図形を準備する．
fig, ax = plt.subplots(figsize=(10, 6.5))
draw_pitch(ax)

# 課題1：選手の色を速さへ対応させる．
speed_norm = Normalize(vmin=0, vmax=7)
players = ax.scatter(
    [],
    [],
    s=100,
    c=[],
    cmap="viridis",
    norm=speed_norm,
    edgecolors="black",
    linewidths=0.8,
    zorder=3,
)
centroid = ax.scatter(
    [],
    [],
    s=160,
    c="#ffd54f",
    marker="X",
    edgecolors="black",
    label="チーム重心",
    zorder=4,
)
labels = {
    tag_id: ax.text(
        0,
        0,
        str(tag_id),
        ha="center",
        va="center",
        fontsize=8,
        color="white",
        weight="bold",
        zorder=5,
    )
    for tag_id in player_ids
}
time_text = ax.text(
    0.02,
    1.02,
    "",
    transform=ax.transAxes,
    fontsize=12,
)

colorbar = fig.colorbar(players, ax=ax, pad=0.02)
colorbar.set_label("速さ（m/s）")
ax.legend(loc="upper right", framealpha=0.9)


# 演習4・セル3：指定フレームの表示を更新する．
def update(frame):
    frame_df = (
        tracking_df[tracking_df["frame"] == frame]
        .set_index("tag_id")
    )

    positions = []
    speeds = []

    for tag_id in player_ids:
        if tag_id not in frame_df.index:
            labels[tag_id].set_visible(False)
            continue

        x_pos = float(frame_df.loc[tag_id, "x_pos"])
        y_pos = float(frame_df.loc[tag_id, "y_pos"])
        positions.append([x_pos, y_pos])
        # 課題1：各選手の速さを色の更新に使用する．
        speeds.append(float(frame_df.loc[tag_id, "speed"]))

        labels[tag_id].set_position((x_pos, y_pos))
        labels[tag_id].set_visible(True)

    players.set_offsets(np.asarray(positions))
    players.set_array(np.asarray(speeds))
    centroid.set_offsets([
        [
            frame_df["x_pos"].mean(),
            frame_df["y_pos"].mean(),
        ]
    ])
    time_text.set_text(
        f"経過時間: {frame / fps:4.1f} 秒"
    )

    return [
        players,
        centroid,
        time_text,
        *labels.values(),
    ]


# 演習4・セル4：全フレームをつないでGIFへ保存する．
animation = FuncAnimation(
    fig,
    update,
    frames=frame_ids,
    interval=1000 / fps,
    blit=False,
)

output_path.parent.mkdir(parents=True, exist_ok=True)
animation.save(
    output_path,
    writer=PillowWriter(fps=fps),
    dpi=90,
)
plt.close(fig)

print("saved:", output_path)
