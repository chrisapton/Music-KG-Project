import pandas as pd

csv_files = [
    "../../data/processed/acousticbrainz_2022.csv",
    "../../data/processed/acousticbrainz_2023.csv",
    "../../data/processed/acousticbrainz_2024.csv"
]

df_all = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

drop_columns = [
    "voice_instrumental_instrumental",
    "tonal_atonal_atonal",
    "timbre_dark"
]

drop_columns += [col for col in df_all.columns if col.startswith("gender_")]

# Drop safely (only existing columns)
df_all.drop(columns=[col for col in drop_columns if col in df_all.columns], inplace=True)

# Drop duplicates based on 'whosampled_id'
df_all.drop_duplicates(subset="whosampled_id", keep="first", inplace=True)

# Save final result
df_all.to_csv("../neo4j/data/import/acousticbrainz.csv", index=False)
