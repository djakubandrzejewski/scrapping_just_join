import csv

def export_full_tech_data(data, filename="tech_stack_data.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Technology", "Level", "Source URL"])
        for tech, level, url in data:
            writer.writerow([tech, level, url])
    print(f"saved {filename}")
