import csv
from collections import Counter


def export_full_tech_data(data, filename="tech_stack_data.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Technology", "Level", "Source URL"])
        for tech, level, url in data:
            writer.writerow([tech, level, url])
    print(f"saved {filename}")


def export_aggregated_tech_data(data, filename="tech_stack_data.csv"):
    counter = Counter([tech for tech, level, url in data])
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Technology", "count"])
        for tech, count in counter.most_common():
            writer.writerow([tech, count])
    print(f"✅ Aggregated file saved as {filename}")
