import pandas as pd

csv_files = [
    "../neo4j/data/import/musicbrainz_summaries_2024.csv",
    "../neo4j/data/import/musicbrainz_summaries_2023.csv",
    "../neo4j/data/import/musicbrainz_summaries_2022.csv"
]

df_all = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

df_all.drop_duplicates(subset=['artist_name'], keep="first", inplace=True)

# Genre clean up
# df_all = df_all[~(
#     df_all['genre'].str.startswith('_') |
#     df_all['genre'].str.contains(';') |
#     df_all['genre'].str.match(r'^\d') |
#     (df_all['genre'].str.len() <= 2) |
#     (df_all['genre'].str.len() >= 20)
# )]

# Save final result
df_all.to_csv("../neo4j/data/import/musicbrainz_summaries_all.csv", index=False)

# df = pd.read_csv('../neo4j/data/import/musicbrainz_genres_all.csv')
# df['genre'] = df['genre'].str.strip().str.title()
#
# df.to_csv('../neo4j/data/import/musicbrainz_genres_all.csv', index=False)
