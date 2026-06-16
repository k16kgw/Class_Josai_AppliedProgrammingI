import json
from pathlib import Path

import pandas as pd


input_path = Path("data/raw/jma_tokyo_forecast.json")
output_path = Path("data/processed/tokyo_weekly_weather_from_json.csv")


def main():
    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]

    weather_rows = []

    for area in weather_series["areas"]:
        area_name = area["area"]["name"]
        area_code = area["area"]["code"]

        for i, forecast_time in enumerate(weather_series["timeDefines"]):
            pop_text = area["pops"][i]

            if pop_text == "":
                pop = None
            else:
                pop = int(pop_text)

            weather_rows.append({
                "発表区域名": "東京都",
                "発表区域コード": "130000",
                "発表機関": weekly_forecast["publishingOffice"],
                "発表時刻": weekly_forecast["reportDatetime"],
                "地域名": area_name,
                "地域コード": area_code,
                "予報時刻": forecast_time,
                "予報日": forecast_time[:10],
                "天気コード": area["weatherCodes"][i],
                "降水確率": pop,
                "信頼度": area["reliabilities"][i],
            })

    weather_df = pd.DataFrame(weather_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    weather_df.to_csv(output_path, index=False)

    print("行数・列数:", weather_df.shape)
    print("地域名:", list(weather_df["地域名"].unique()))
    print("降水確率が空欄の行数:", weather_df["降水確率"].isna().sum())
    print("saved:", output_path)


if __name__ == "__main__":
    main()
