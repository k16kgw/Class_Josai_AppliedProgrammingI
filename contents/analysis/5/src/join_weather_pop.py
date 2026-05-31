import csv

weather_path = "data/raw/jma_tokyo_weather_raw_table.csv"
pop_path = "data/raw/jma_tokyo_pop_raw_table.csv"
output_path = "data/raw/jma_tokyo_weather_pop_raw_table.csv"

with open(weather_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    weather_rows = list(reader)

with open(pop_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    pop_rows = list(reader)

pop_by_key = {}

for row in pop_rows:
    key = (row["地域コード"], row["予報時刻"])
    pop_by_key[key] = row["降水確率"]

rows_out = []

for row in weather_rows:
    key = (row["地域コード"], row["予報時刻"])
    row["降水確率"] = pop_by_key.get(key, "")
    rows_out.append(row)

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード", "予報時刻",
    "天気コード", "天気", "風", "波", "降水確率"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("rows:", len(rows_out))