# 演習1・セル2：ライブラリを読み込む
import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import requests


# 演習5・セル1：取得する発表区域を定義する
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

output_point_path = "data/processed/forecast_area_points.csv"
output_weather_path = "data/processed/my_weekly_weather.csv"
output_data_path = "data/processed/my_forecast_map_data.csv"
output_map_path = "reports/figures/my_forecast_pop_elevation_map.html"

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("reports/figures").mkdir(parents=True, exist_ok=True)


# 演習5・セル2：APIからJSONを取得する処理を関数にする
def fetch_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


# 演習3・セル1：緯度・経度を度分形式から小数へ変換する
def degree_minute_to_decimal(value):
    return value[0] + value[1] / 60


# 課題3補足：週間予報の地域コードから地域名を調べる辞書を作る
def build_weekly_area_lookup(forecast_json):
    weekly_forecast = forecast_json[1]
    weather_series = weekly_forecast["timeSeries"][0]
    lookup = {}

    for area in weather_series["areas"]:
        lookup[area["area"]["code"]] = area["area"]["name"]

    return lookup


# 課題3補足：細分地域を実際の週間予報地域へ対応させる
def to_weekly_forecast_area(
    office_name,
    office_code,
    class10_code,
    class10_name,
    weekly_area_lookup,
):
    if class10_code in weekly_area_lookup:
        return class10_code, weekly_area_lookup[class10_code]

    for weekly_code, weekly_name in weekly_area_lookup.items():
        if class10_name in weekly_name or weekly_name in class10_name:
            return weekly_code, weekly_name

    if office_code in weekly_area_lookup:
        return office_code, weekly_area_lookup[office_code]

    if len(weekly_area_lookup) == 1:
        area_code = list(weekly_area_lookup.keys())[0]
        area_name = weekly_area_lookup[area_code]
        return area_code, area_name

    return class10_code, class10_name


# 演習6・セル1：JSONから週間予報の行を作る
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


# 演習3・セル1：予報地域とアメダス地点に関するJSONを取得する
area_data = fetch_json(area_url)
forecast_area_data = fetch_json(forecast_area_url)
amedas_data = fetch_json(amedas_url)

# 演習5・セル2：各発表区域の天気予報JSONを取得して保存する
forecast_jsons = {}

for office_name, office_code in FORECAST_OFFICES.items():
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{office_code}.json"
    data = fetch_json(url)
    forecast_jsons[office_name] = data

    output_path = f"data/raw/forecast_{office_code}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("saved:", output_path)

# 演習3・セル1：予報地域とアメダス地点を対応させた表を作る
point_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    weekly_area_lookup = build_weekly_area_lookup(forecast_jsons[office_name])

    for item in forecast_area_data[office_code]:
        class10_code = item["class10"]
        class10_name = area_data["class10s"][class10_code]["name"]
        forecast_area_code, forecast_area_name = to_weekly_forecast_area(
            office_name,
            office_code,
            class10_code,
            class10_name,
            weekly_area_lookup,
        )

        for amedas_id in item["amedas"]:
            amedas_info = amedas_data[amedas_id]
            lat = degree_minute_to_decimal(amedas_info["lat"])
            lon = degree_minute_to_decimal(amedas_info["lon"])

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

# 演習3・セル2：予報地域・アメダス対応CSVを保存する
point_df = pd.DataFrame(point_rows)
point_df.to_csv(output_point_path, index=False)
print("saved:", output_point_path)

# 演習6・セル2：複数都道府県の週間予報を1つの表にまとめる
weather_rows = []

for office_name, office_code in FORECAST_OFFICES.items():
    weather_rows.extend(
        build_weekly_weather_rows(
            forecast_jsons[office_name],
            office_name,
            office_code,
        )
    )

# 演習6・セル3：週間予報をCSVとして保存する
weather_df = pd.DataFrame(weather_rows)
weather_df.to_csv(output_weather_path, index=False)
print("saved:", output_weather_path)

# 演習7・セル1：地域ごとに降水確率を集計する
source_df = weather_df.dropna(subset=["降水確率"]).copy()
summary_rows = []

keys_df = source_df[["発表区域名", "地域名"]].drop_duplicates()

for _, key_row in keys_df.iterrows():
    office_name = key_row["発表区域名"]
    area_name = key_row["地域名"]

    area_df = source_df[
        (source_df["発表区域名"] == office_name)
        & (source_df["地域名"] == area_name)
    ]

    summary_rows.append({
        "発表区域名": office_name,
        "地域名": area_name,
        "予報日数": len(area_df),
        "平均降水確率": round(area_df["降水確率"].mean(), 1),
        "最大降水確率": area_df["降水確率"].max(),
        "信頼度A件数": (area_df["信頼度"] == "A").sum(),
    })

summary_df = pd.DataFrame(summary_rows)

# 演習7・セル2：集計結果にアメダス地点情報を結合する
map_df = pd.merge(
    summary_df,
    point_df,
    on=["発表区域名", "地域名"],
    how="left",
)

# 演習7・セル3：結合できなかった地域を確認する
missing_df = map_df[map_df["緯度"].isna()]

if len(missing_df) > 0:
    print("結合できなかった行があります")
    print(missing_df[["発表区域名", "地域名"]])

# 演習10・セル1：標高から点の表示サイズを作る
map_df["標高表示サイズ"] = map_df["標高"].clip(upper=800)

# 演習7・セル4：地図用データをCSVとして保存する
map_df.to_csv(output_data_path, index=False)
print("saved:", output_data_path)

# 演習10・セル2：平均降水確率と標高を重ねた地図を作る
fig = px.scatter_map(
    map_df.dropna(subset=["緯度", "経度"]),
    lat="緯度",
    lon="経度",
    color="平均降水確率",
    size="標高表示サイズ",
    hover_name="地域名",
    hover_data=[
        "発表区域名",
        "細分地域名",
        "アメダス地点名",
        "平均降水確率",
        "最大降水確率",
        "標高",
    ],
    color_continuous_scale="viridis",
    size_max=25,
    zoom=6,
    height=650,
)

fig.update_layout(
    title="選択した都道府県の週間予報：平均降水確率と標高",
    map_style="open-street-map",
)

# 演習10・セル2：地図をHTMLファイルとして保存する
fig.write_html(output_map_path)
print("saved:", output_map_path)
