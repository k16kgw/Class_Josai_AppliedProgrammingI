from argparse import ArgumentParser
from pathlib import Path

import pandas as pd
import requests


DATA_URL = (
    "https://datasets.simula.no/downloads/alfheim/"
    "2013-11-03/zxy/"
    "2013-11-03_tromso_stromsgodset_first.csv"
)

COLUMNS = [
    "timestamp",
    "tag_id",
    "x_pos",
    "y_pos",
    "heading",
    "direction",
    "energy",
    "speed",
    "total_distance",
]


def download_file(url, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = destination.with_suffix(
        destination.suffix + ".part"
    )

    with requests.get(
        url,
        stream=True,
        timeout=(30, 300),
    ) as response:
        response.raise_for_status()
        total_size = int(
            response.headers.get("content-length", 0)
        )
        downloaded = 0

        with open(temporary_path, "wb") as file:
            for chunk in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if not chunk:
                    continue
                file.write(chunk)
                downloaded += len(chunk)

                if total_size:
                    percent = downloaded / total_size * 100
                    print(
                        f"\rdownload: {percent:5.1f}%",
                        end="",
                    )

    temporary_path.replace(destination)
    print("\nsaved:", destination)


def build_sample(
    raw_path,
    output_path,
    start_time,
    duration,
    fps,
):
    tracking_df = pd.read_csv(
        raw_path,
        names=COLUMNS,
        usecols=[
            "timestamp",
            "tag_id",
            "x_pos",
            "y_pos",
            "speed",
        ],
    )

    tracking_df["timestamp"] = pd.to_datetime(
        tracking_df["timestamp"],
        format="mixed",
        errors="coerce",
    )

    start = pd.Timestamp(start_time)
    end = start + pd.Timedelta(seconds=duration)

    clip_df = tracking_df[
        tracking_df["timestamp"].between(
            start,
            end,
            inclusive="left",
        )
    ].copy()

    clip_df = clip_df[
        clip_df["x_pos"].between(0, 105)
        & clip_df["y_pos"].between(0, 68)
    ].copy()

    clip_df["elapsed_seconds"] = (
        clip_df["timestamp"] - start
    ).dt.total_seconds()
    clip_df["frame"] = (
        clip_df["elapsed_seconds"] * fps
    ).astype(int)

    sample_df = (
        clip_df
        .sort_values("timestamp")
        .groupby(["frame", "tag_id"], as_index=False)
        .first()
    )

    expected_frames = duration * fps
    coverage = sample_df.groupby("tag_id")[
        "frame"
    ].nunique()
    active_tags = coverage[
        coverage >= expected_frames * 0.8
    ].index

    sample_df = sample_df[
        sample_df["tag_id"].isin(active_tags)
    ].copy()
    sample_df["elapsed_seconds"] = (
        sample_df["frame"] / fps
    )

    sample_df = sample_df[
        [
            "frame",
            "elapsed_seconds",
            "timestamp",
            "tag_id",
            "x_pos",
            "y_pos",
            "speed",
        ]
    ].sort_values(["frame", "tag_id"])

    if sample_df.empty:
        raise ValueError(
            "指定した時間帯のデータを抽出できませんでした．"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample_df.to_csv(output_path, index=False)

    print("rows:", len(sample_df))
    print("frames:", sample_df["frame"].nunique())
    print("players:", sample_df["tag_id"].nunique())
    print("saved:", output_path)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--raw-path",
        type=Path,
        default=Path(
            "data/raw/alfheim_tracking_first.csv"
        ),
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path(
            "data/processed/alfheim_tracking_5fps.csv"
        ),
    )
    parser.add_argument(
        "--start-time",
        default="2013-11-03 18:35:00",
    )
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--fps", type=int, default=5)
    args = parser.parse_args()

    if not args.raw_path.exists():
        download_file(DATA_URL, args.raw_path)
    else:
        print("use existing file:", args.raw_path)

    build_sample(
        raw_path=args.raw_path,
        output_path=args.output_path,
        start_time=args.start_time,
        duration=args.duration,
        fps=args.fps,
    )


if __name__ == "__main__":
    main()
