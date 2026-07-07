from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap

from animate_alfheim_tracking import draw_pitch


def create_animation(tracking_df, output_path, fps, grid_size):
    plt.rcParams["font.family"] = "Hiragino Sans"

    # 演習4・セル1：動画で使用する選手IDとフレームを準備する．
    player_ids = sorted(tracking_df["tag_id"].unique())
    player_index = {
        tag_id: index
        for index, tag_id in enumerate(player_ids)
    }
    frame_ids = sorted(tracking_df["frame"].unique())

    # 演習5・セル1：ボロノイ領域を計算する格子を準備する．
    x_centers = np.arange(grid_size / 2, 105, grid_size)
    y_centers = np.arange(grid_size / 2, 68, grid_size)
    grid_x, grid_y = np.meshgrid(x_centers, y_centers)

    voronoi_colors = plt.colormaps["tab10"](
        np.arange(len(player_ids))
    )
    voronoi_cmap = ListedColormap(voronoi_colors)

    # 演習3・セル1，演習4・セル2：更新する図形を準備する．
    fig, ax = plt.subplots(figsize=(10, 6.5))
    draw_pitch(ax)

    region_image = ax.imshow(
        np.zeros_like(grid_x),
        extent=(0, 105, 0, 68),
        origin="lower",
        cmap=voronoi_cmap,
        vmin=-0.5,
        vmax=len(player_ids) - 0.5,
        alpha=0.42,
        interpolation="nearest",
        zorder=1,
    )
    players = ax.scatter(
        [],
        [],
        s=100,
        edgecolors="black",
        linewidths=0.8,
        zorder=3,
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
            zorder=4,
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
    ax.set_title("ホームチームのボロノイ図の時間変化")

    def update(frame):
        # 演習4・セル3：指定フレームの選手位置を取り出す．
        frame_df = (
            tracking_df[tracking_df["frame"] == frame]
            .set_index("tag_id")
        )

        positions = []
        color_indices = []

        for tag_id in player_ids:
            if tag_id not in frame_df.index:
                labels[tag_id].set_visible(False)
                continue

            x_pos = float(frame_df.loc[tag_id, "x_pos"])
            y_pos = float(frame_df.loc[tag_id, "y_pos"])
            positions.append([x_pos, y_pos])
            color_indices.append(player_index[tag_id])

            labels[tag_id].set_position((x_pos, y_pos))
            labels[tag_id].set_visible(True)

        player_points = np.asarray(positions)
        color_indices = np.asarray(color_indices)

        # 演習5・セル2：各格子点に最も近い選手を求める．
        distance_squared = (
            (grid_x[:, :, None] - player_points[:, 0]) ** 2
            + (grid_y[:, :, None] - player_points[:, 1]) ** 2
        )
        nearest_local_player = distance_squared.argmin(axis=2)
        nearest_player = color_indices[nearest_local_player]

        # 演習4・セル3，演習5・セル3：領域と選手位置を更新する．
        region_image.set_data(nearest_player)
        players.set_offsets(player_points)
        players.set_facecolors(voronoi_colors[color_indices])

        elapsed_seconds = float(
            frame_df["elapsed_seconds"].iloc[0]
        )
        time_text.set_text(
            f"経過時間: {elapsed_seconds:4.1f} 秒"
        )

        return [
            region_image,
            players,
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
            "reports/figures/alfheim_voronoi.gif"
        ),
    )
    parser.add_argument("--fps", type=int, default=5)
    parser.add_argument(
        "--grid-size",
        type=float,
        default=0.5,
    )
    args = parser.parse_args()

    tracking_df = pd.read_csv(
        args.input_path,
        parse_dates=["timestamp"],
    )

    create_animation(
        tracking_df=tracking_df,
        output_path=args.output_path,
        fps=args.fps,
        grid_size=args.grid_size,
    )
    print("saved:", args.output_path)


if __name__ == "__main__":
    main()
