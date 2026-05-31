import csv
import json
from pathlib import Path


input_path = Path("data/raw/jma_tokyo_forecast.json")
weather_output_path = Path("data/processed/jma_tokyo_weekly_weather.csv")
temperature_output_path = Path("data/processed/jma_tokyo_weekly_temperature.csv")
weather_summary_output_path = Path("data/processed/jma_tokyo_weekly_weather_summary.csv")
temperature_summary_output_path = Path("data/processed/jma_tokyo_weekly_temperature_summary.csv")

missing_values = {"", "NA", "N/A", "null", "-"}


def clean_text(value):
    return str(value).strip().replace("　", " ")


def to_int_or_blank(value):
    value = clean_text(value)

    if value in missing_values:
        return ""

    return int(value)


def average_or_blank(values):
    values = [value for value in values if value != ""]

    if len(values) == 0:
        return ""

    return round(sum(values) / len(values), 1)


def build_weekly_weather_rows(data):
    weekly_forecast = data[1]
    weather_series = weekly_forecast["timeSeries"][0]
    rows_out = []

    for area in weather_series["areas"]:
        area_name = clean_text(area["area"]["name"])
        area_code = clean_text(area["area"]["code"])

        for i, forecast_time in enumerate(weather_series["timeDefines"]):
            rows_out.append({
                "発表機関": clean_text(weekly_forecast["publishingOffice"]),
                "発表時刻": clean_text(weekly_forecast["reportDatetime"]),
                "地域名": area_name,
                "地域コード": area_code,
                "予報時刻": clean_text(forecast_time),
                "予報日": clean_text(forecast_time)[:10],
                "天気コード": to_int_or_blank(area["weatherCodes"][i]),
                "降水確率": to_int_or_blank(area["pops"][i]),
                "信頼度": clean_text(area["reliabilities"][i]),
            })

    return rows_out


def build_weekly_temperature_rows(data):
    weekly_forecast = data[1]
    temperature_series = weekly_forecast["timeSeries"][1]
    rows_out = []

    for area in temperature_series["areas"]:
        point_name = clean_text(area["area"]["name"])
        point_code = clean_text(area["area"]["code"])

        for i, forecast_time in enumerate(temperature_series["timeDefines"]):
            rows_out.append({
                "発表機関": clean_text(weekly_forecast["publishingOffice"]),
                "発表時刻": clean_text(weekly_forecast["reportDatetime"]),
                "地点名": point_name,
                "地点コード": point_code,
                "予報時刻": clean_text(forecast_time),
                "予報日": clean_text(forecast_time)[:10],
                "最低気温": to_int_or_blank(area["tempsMin"][i]),
                "最高気温": to_int_or_blank(area["tempsMax"][i]),
                "最低気温上限": to_int_or_blank(area["tempsMinUpper"][i]),
                "最低気温下限": to_int_or_blank(area["tempsMinLower"][i]),
                "最高気温上限": to_int_or_blank(area["tempsMaxUpper"][i]),
                "最高気温下限": to_int_or_blank(area["tempsMaxLower"][i]),
            })

    return rows_out


def summarize_weekly_weather(rows):
    summary = {}

    for row in rows:
        key = (row["地域名"], row["地域コード"])

        if key not in summary:
            summary[key] = {
                "予報日数": 0,
                "降水確率": [],
                "信頼度A件数": 0,
                "信頼度B件数": 0,
                "信頼度C件数": 0,
            }

        summary[key]["予報日数"] += 1

        if row["降水確率"] != "":
            summary[key]["降水確率"].append(row["降水確率"])

        if row["信頼度"] in {"A", "B", "C"}:
            summary[key][f"信頼度{row['信頼度']}件数"] += 1

    rows_out = []

    for (area_name, area_code), values in summary.items():
        pops = values["降水確率"]

        rows_out.append({
            "地域名": area_name,
            "地域コード": area_code,
            "予報日数": values["予報日数"],
            "降水確率あり件数": len(pops),
            "平均降水確率": average_or_blank(pops),
            "最大降水確率": max(pops) if len(pops) > 0 else "",
            "最小降水確率": min(pops) if len(pops) > 0 else "",
            "信頼度A件数": values["信頼度A件数"],
            "信頼度B件数": values["信頼度B件数"],
            "信頼度C件数": values["信頼度C件数"],
        })

    rows_out.sort(key=lambda row: row["地域コード"])
    return rows_out


def summarize_weekly_temperature(rows):
    summary = {}

    for row in rows:
        key = (row["地点名"], row["地点コード"])

        if key not in summary:
            summary[key] = {
                "予報日数": 0,
                "最低気温": [],
                "最高気温": [],
            }

        summary[key]["予報日数"] += 1

        if row["最低気温"] != "":
            summary[key]["最低気温"].append(row["最低気温"])

        if row["最高気温"] != "":
            summary[key]["最高気温"].append(row["最高気温"])

    rows_out = []

    for (point_name, point_code), values in summary.items():
        min_temps = values["最低気温"]
        max_temps = values["最高気温"]

        rows_out.append({
            "地点名": point_name,
            "地点コード": point_code,
            "予報日数": values["予報日数"],
            "最低気温あり日数": len(min_temps),
            "最高気温あり日数": len(max_temps),
            "平均最低気温": average_or_blank(min_temps),
            "平均最高気温": average_or_blank(max_temps),
            "最低気温の最小値": min(min_temps) if len(min_temps) > 0 else "",
            "最高気温の最大値": max(max_temps) if len(max_temps) > 0 else "",
        })

    rows_out.sort(key=lambda row: row["地点コード"])
    return rows_out


def write_csv(output_path, fieldnames, rows):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("saved:", output_path)
    print("rows:", len(rows))


def main():
    with input_path.open(encoding="utf-8") as f:
        data = json.load(f)

    weather_rows = build_weekly_weather_rows(data)
    temperature_rows = build_weekly_temperature_rows(data)
    weather_summary_rows = summarize_weekly_weather(weather_rows)
    temperature_summary_rows = summarize_weekly_temperature(temperature_rows)

    write_csv(
        weather_output_path,
        [
            "発表機関", "発表時刻", "地域名", "地域コード",
            "予報時刻", "予報日", "天気コード", "降水確率", "信頼度",
        ],
        weather_rows,
    )
    write_csv(
        temperature_output_path,
        [
            "発表機関", "発表時刻", "地点名", "地点コード",
            "予報時刻", "予報日", "最低気温", "最高気温",
            "最低気温上限", "最低気温下限", "最高気温上限", "最高気温下限",
        ],
        temperature_rows,
    )
    write_csv(
        weather_summary_output_path,
        [
            "地域名", "地域コード", "予報日数", "降水確率あり件数",
            "平均降水確率", "最大降水確率", "最小降水確率",
            "信頼度A件数", "信頼度B件数", "信頼度C件数",
        ],
        weather_summary_rows,
    )
    write_csv(
        temperature_summary_output_path,
        [
            "地点名", "地点コード", "予報日数", "最低気温あり日数",
            "最高気温あり日数", "平均最低気温", "平均最高気温",
            "最低気温の最小値", "最高気温の最大値",
        ],
        temperature_summary_rows,
    )


if __name__ == "__main__":
    main()
