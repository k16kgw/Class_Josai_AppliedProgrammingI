import csv

input_path = "data/processed/jma_tokyo_weather_pop_clean.csv"
output_path = "data/processed/weather_summary_by_area.csv"

summary = {}

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        key = (row["地域名"], row["天気カテゴリ"])

        if key not in summary:
            summary[key] = {
                "件数": 0,
                "降水確率あり件数": 0,
                "降水確率合計": 0
            }

        summary[key]["件数"] += 1

        if row["降水確率"] != "":
            summary[key]["降水確率あり件数"] += 1
            summary[key]["降水確率合計"] += int(row["降水確率"])

rows_out = []

for (area_name, category), values in summary.items():
    if values["降水確率あり件数"] == 0:
        average_pop = ""
    else:
        average_pop = values["降水確率合計"] / values["降水確率あり件数"]

    rows_out.append({
        "地域名": area_name,
        "天気カテゴリ": category,
        "件数": values["件数"],
        "降水確率あり件数": values["降水確率あり件数"],
        "平均降水確率": average_pop
    })

rows_out.sort(key=lambda row: (row["地域名"], row["天気カテゴリ"]))

fieldnames = ["地域名", "天気カテゴリ", "件数", "降水確率あり件数", "平均降水確率"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", len(rows_out))