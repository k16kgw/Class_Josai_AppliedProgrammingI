import csv
import json

input_path = "data/raw/jma_tokyo_forecast.json"
output_path = "data/raw/jma_tokyo_pop_raw_table.csv"

with open(input_path, encoding="utf-8") as f:
    data = json.load(f)

forecast = data[0]
pop_series = forecast["timeSeries"][1]

rows_out = []

for area in pop_series["areas"]:
    area_name = area["area"]["name"]
    area_code = area["area"]["code"]

    for i, time in enumerate(pop_series["timeDefines"]):
        rows_out.append({
            "地域名": area_name,
            "地域コード": area_code,
            "予報時刻": time,
            "降水確率": area["pops"][i]
        })

fieldnames = ["地域名", "地域コード", "予報時刻", "降水確率"]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))