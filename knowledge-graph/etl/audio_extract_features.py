import json
import pandas as pd

INPUT_FILE = "../../data/raw/acousticbrainz_2022.jsonl"
OUTPUT_FILE = "../../data/processed/acousticbrainz_2022.csv"
data_rows = []

with open(INPUT_FILE, "r") as f:
    for line in f:
        record = json.loads(line)
        row = {"whosampled_id": record.get("whosampled_id", None)}

        features = record.get("features", {}).get("highlevel", {})
        for feature_name, content in features.items():
            if feature_name == "moods_mirex":
                continue  # skip this feature entirely
            if "all" in content:
                for label, prob in content["all"].items():
                    if not label.startswith("not_"):
                        row[f"{feature_name}_{label}"] = prob

        data_rows.append(row)

df = pd.DataFrame(data_rows)
df.to_csv(OUTPUT_FILE, index=False)
