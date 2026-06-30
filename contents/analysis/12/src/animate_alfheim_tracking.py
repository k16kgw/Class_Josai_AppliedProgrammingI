from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Circle, Rectangle


def draw_pitch(ax):
    line_style = {
        "fill": False,
        "edgecolor": "white",
        "linewidth": 1.5,
    }

    ax.set_facecolor("#2f7d32")
    ax.add_patch(Rectangle((0, 0), 105, 68, **line_style))
    ax.plot([52.5, 52.5], [0, 68], color="white", lw=1.5)
    ax.add_patch(
        Circle((52.5, 34), 9.15, **line_style)
    )
    ax.add_patch(
        Rectangle((0, 13.84), 16.5, 40.32, **line_style)
    )
    ax.add_patch(
        Rectangle((88.5, 13.84), 16.5, 40.32, **line_style)
    )
    ax.add_patch(
        Rectangle((0, 24.84), 5.5, 18.32, **line_style)
    )
    ax.add_patch(
        Rectangle((99.5, 24.84), 5.5, 18.32, **line_style)
    )
    ax.scatter([52.5, 11, 94], [34, 34, 34], c="white", s=12)

    ax.set_xlim(-2, 107)
    ax.set_ylim(-2, 70)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])


def create_animation(tracking_df, output_path, fps):
    plt.rcParams["font.family"] = "Hiragino Sans"

    player_ids = sorted(tracking_df["tag_id"].unique())
    frame_ids = sorted(tracking_df["frame"].unique())
    color_map = plt.colormaps["tab10"]
    player_colors = {
        tag_id: color_map(index % 10)
        for index, tag_id in enumerate(player_ids)
    }

    fig, ax = plt.subplots(figsize=(10, 6.5))
    draw_pitch(ax)

    players = ax.scatter(
        [],
        [],
        s=90,
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
    ax.legend(loc="upper right", framealpha=0.9)

    def update(frame):
        frame_df = (
            tracking_df[tracking_df["frame"] == frame]
            .set_index("tag_id")
        )

        positions = []
        colors = []

        for tag_id in player_ids:
            if tag_id not in frame_df.index:
                labels[tag_id].set_visible(False)
                continue

            x_pos = float(frame_df.loc[tag_id, "x_pos"])
            y_pos = float(frame_df.loc[tag_id, "y_pos"])
            positions.append([x_pos, y_pos])
            colors.append(player_colors[tag_id])

            labels[tag_id].set_position((x_pos, y_pos))
            labels[tag_id].set_visible(True)

        players.set_offsets(np.asarray(positions))
        players.set_facecolors(colors)
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


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--input-path",
        type=Path,
        default=Path(
            "data/processed/alfheim_tracking_5fps.csv"
        ),
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path(
            "reports/figures/alfheim_tracking.gif"
        ),
    )
    parser.add_argument("--fps", type=int, default=5)
    args = parser.parse_args()

    tracking_df = pd.read_csv(
        args.input_path,
        parse_dates=["timestamp"],
    )

    create_animation(
        tracking_df=tracking_df,
        output_path=args.output_path,
        fps=args.fps,
    )
    print("saved:", args.output_path)


if __name__ == "__main__":
    main()
