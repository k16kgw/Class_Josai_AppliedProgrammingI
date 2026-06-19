import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests


FORECAST_OFFICES = {
    "東京都": "130000",
    "埼玉県": "110000",
    "長野県": "200000",
    "新潟県": "150000",
    "神奈川県": "140000", 
}

area_url = "https://www.jma.go.jp/bosai/common/const/area.json"
forecast_area_url = "https://www.jma.go.jp/bosai/forecast/const/forecast_area.json"
amedas_url = "https://www.jma.go.jp/bosai/amedas/const/amedastable.json"

area_response = requests.get(area_url)
area_response.raise_for_status()
area_data = area_response.json()

forecast_area_response = requests.get(forecast_area_url)
forecast_area_response.raise_for_status()
forecast_area_data = forecast_area_response.json()

amedas_response = requests.get(amedas_url)
amedas_response.raise_for_status()
amedas_data = amedas_response.json()

print("area.jsonに含まれる発表区域数:", len(area_data["offices"]))
print("forecast_area.jsonに含まれる発表区域数:", len(forecast_area_data))
print("amedastable.jsonに含まれるアメダス地点数:", len(amedas_data))

area_data.keys()
forecast_area_data["210000"]
for item in forecast_area_data["210000"]:
    class10_code = item["class10"]
    class10_name = area_data["class10s"][class10_code]["name"]

    print(
        class10_code,
        class10_name,
        "amedas:",
        item["amedas"],
        "class20:",
        item["class20"],
    )
def to_weekly_forecast_area(office_name, office_code, class10_code, class10_name):
    if office_code == "130000" and class10_code in {"130020", "130030"}:
        return "130100", "伊豆諸島"

    if office_code == "130000":
        return class10_code, class10_name

    return office_code, office_name
def degree_minute_to_decimal(value):
    return value[0] + value[1] / 60

point_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    for item in forecast_area_data[office_code]:
        class10_code = item["class10"]
        class10_name = area_data["class10s"][class10_code]["name"]
        forecast_area_code, forecast_area_name = to_weekly_forecast_area(
            office_name,
            office_code,
            class10_code,
            class10_name,
        )

        for amedas_id in item["amedas"]:
            amedas_info = amedas_data[amedas_id]

            lat = degree_minute_to_decimal(amedas_info["lat"]) # latitude
            lon = degree_minute_to_decimal(amedas_info["lon"]) # longitude

            point_rows.append({
                "発表区域名": office_name,
                "発表区域コード": office_code,
                "地域名": forecast_area_name,
                "地域コード": forecast_area_code,
                "細分地域名": class10_name,
                "細分地域コード": class10_code,
                "アメダス番号": amedas_id,
                "アメダス地点名": amedas_info["kjName"],
                "緯度": round(lat, 6),
                "経度": round(lon, 6),
                "標高": amedas_info["alt"],
                "予報区域対応取得元": "気象庁 forecast_area.json",
                "座標標高取得元": "気象庁 amedastable.json",
            })

point_df = pd.DataFrame(point_rows)

point_df

forecast_jsons = {}

for office_name, office_code in FORECAST_OFFICES.items():
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    forecast_jsons[office_name] = data

    output_path = f"data/raw/forecast_{office_code}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("saved:", output_path)

for office_name, data in forecast_jsons.items():
    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]

    print("----", office_name, "----")
    for area in weather_series["areas"]:
        print(area["area"]["name"], area["area"]["code"])

def build_weekly_weather_rows(data, office_name, office_code):
    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]
    rows = []

    for area in weather_series["areas"]:
        area_name = area["area"]["name"]
        area_code = area["area"]["code"]

        for i, forecast_time in enumerate(weather_series["timeDefines"]):
            pop_text = area["pops"][i]

            if pop_text == "":
                pop = None
            else:
                pop = int(pop_text)

            rows.append({
                "発表区域名": office_name,
                "発表区域コード": office_code,
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

    return rows

all_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    rows = build_weekly_weather_rows(
        forecast_jsons[office_name],
        office_name,
        office_code
    )
    all_rows.extend(rows)

multi_weather_df = pd.DataFrame(all_rows)

print("行数・列数:", multi_weather_df.shape)
multi_weather_df.head()

multi_weather_df.to_csv(
    "data/processed/multi_pref_weekly_weather.csv",
    index=False
)

print("saved: data/processed/multi_pref_weekly_weather.csv")

multi_source_df = multi_weather_df.dropna(subset=["降水確率"]).copy()
summary_rows = []

keys_df = multi_source_df[["発表区域名", "地域名"]].drop_duplicates()

for _, key_row in keys_df.iterrows():
    office_name = key_row["発表区域名"]
    area_name = key_row["地域名"]

    area_df = multi_source_df[
        (multi_source_df["発表区域名"] == office_name)
        & (multi_source_df["地域名"] == area_name)
    ]

    summary_rows.append({
        "発表区域名": office_name,
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": round(area_df["降水確率"].mean(), 1),
        "最大降水確率": area_df["降水確率"].max(),
        "信頼度A件数": (area_df["信頼度"] == "A").sum(),
    })

multi_summary_df = pd.DataFrame(summary_rows)

multi_summary_df.head()

multi_map_df = pd.merge(
    multi_summary_df,
    point_df,
    on=["発表区域名", "地域名"],
    how="left"
)

multi_map_df

missing_point_df = multi_map_df[multi_map_df["緯度"].isna()]

missing_point_df

multi_map_df.to_csv(
    "data/processed/my_forecast_map_data.csv",
    index=False
)

print("saved: data/processed/my_forecast_map_data.csv")

multi_map_df["標高表示サイズ"] = multi_map_df["標高"].clip(upper=800)

multi_map_df[["発表区域名", "地域名", "標高", "標高表示サイズ"]].head()

Path("../reports/figures").mkdir(parents=True, exist_ok=True)

multi_map_df["標高表示サイズ"] = multi_map_df["標高"].clip(upper=800)

fig = px.scatter_mapbox(
    multi_map_df,
    lat="緯度",
    lon="経度",
    color="平均降水確率",
    size="標高表示サイズ",
    hover_name="地域名",
    hover_data=["発表区域名", "細分地域名", "アメダス地点名", "平均降水確率", "最大降水確率", "標高"],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=5,
    height=650,
)

fig.update_layout(
    title="東京都・埼玉県・長野県・新潟県・神奈川県の週間予報：平均降水確率と標高",
    mapbox_style="open-street-map",
)

fig.show()

fig.write_html("../reports/figures/my_forecast_pop_elevation_map.html")

print("saved: ../reports/figures/my_forecast_pop_elevation_map.html")
