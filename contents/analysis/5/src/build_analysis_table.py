import csv

input_path = "data/raw/jma_tokyo_weather_pop_raw_table.csv"
output_path = "data/processed/jma_tokyo_weather_pop_clean.csv"
missing_values = {"", "NA", "N/A", "null", "-"}

def clean_text(value):
    return value.strip().replace("　", " ")

def to_int_or_blank(value):
    value = clean_text(value)
    if value in missing_values:
        return ""
    return int(value)

def weather_category(weather):
    weather = clean_text(weather)
    if "雨" in weather:
        return "雨"
    if "雪" in weather:
        return "雪"
    if "晴" in weather:
        return "晴"
    if "くもり" in weather:
        return "くもり"
    return "その他"

rows_out = []

with open(input_path, encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        forecast_time = clean_text(row["予報時刻"])
        weather = clean_text(row["天気"])

        rows_out.append({
            "発表機関":    clean_text(row["発表機関"]),
            "発表時刻":    clean_text(row["発表時刻"]),
            "地域名":      clean_text(row["地域名"]),
            "地域コード":   clean_text(row["地域コード"]),
            "予報時刻":    forecast_time,
            "予報日":      forecast_time[:10],
            "予報時":      forecast_time[11:16],
            "天気コード":   int(clean_text(row["天気コード"])),
            "天気":        weather,
            "天気カテゴリ": weather_category(weather),
            "風":          clean_text(row["風"]),
            "波":          clean_text(row["波"]),
            "降水確率": to_int_or_blank(row["降水確率"])
        })

fieldnames = [
    "発表機関", "発表時刻", "地域名", "地域コード",
    "予報時刻", "予報日", "予報時",
    "天気コード", "天気", "天気カテゴリ",
    "風", "波", "降水確率"
]

with open(output_path, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows_out)

print("saved:", output_path)
print("出力行数:", len(rows_out))