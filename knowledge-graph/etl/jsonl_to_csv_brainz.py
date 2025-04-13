import json
import csv


def metadata_jsonl_to_csv(input_file, output_dates, output_genres, output_summaries):
    def sanitize(value):
        return '' if value == 'N/A' else value

    # Open output files
    songs_f = open(output_dates, 'w', newline='', encoding='utf-8')
    genres_f = open(output_genres, 'w', newline='', encoding='utf-8')
    summaries_f = open(output_summaries, 'w', newline='', encoding='utf-8')

    songs_writer = csv.DictWriter(songs_f, fieldnames=['id', 'title', 'release_date'])
    genres_writer = csv.writer(genres_f)
    summaries_writer = csv.writer(summaries_f)

    songs_writer.writeheader()
    genres_writer.writerow(['song_id', 'genre'])
    summaries_writer.writerow(['artist_name', 'wikipedia_summary'])

    # Read JSONL file
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            data = json.loads(line)

            # Write song
            songs_writer.writerow({
                'id': sanitize(data.get('id', '')),
                'title': sanitize(data.get('title', '')),
                'release_date': sanitize(data.get('release_date', ''))
            })

            # Write genres
            genres = data.get('genres', [])

            # If it's a string like "N / A", clean and skip it
            if isinstance(genres, str):
                normalized = genres.strip().lower().replace(' ', '').replace('/', '')
                if normalized in ['na', '_fixwhosampledupeurl']:
                    genres = []  # skip it
                else:
                    genres = [genres]  # treat it as a single genre

            # Now handle the list safely
            if isinstance(genres, list):
                for genre in genres:
                    cleaned_genre = genre.strip()
                    normalized = cleaned_genre.lower().replace(' ', '').replace('/', '')
                    if normalized not in ['na', '_fixwhosampledupeurl']:
                        genres_writer.writerow([data['id'], cleaned_genre])

            # Write artist summaries
            artists = data.get('artist', [])
            summaries = data.get('wikipedia_summary', [])

            # Handle case where artist is a single string (e.g., "Metro Boomin")
            if isinstance(artists, str):
                artists = [artists]

            # Same for summaries, just in case
            if isinstance(summaries, str):
                summaries = [summaries]

            # Only zip if both are lists of equal length
            if isinstance(artists, list) and isinstance(summaries, list) and len(artists) == len(summaries):
                for name, summary in zip(artists, summaries):
                    cleaned_name = name.strip()
                    if summary.strip().lower().replace(' ', '').replace('/', '') != 'na':
                        summaries_writer.writerow([cleaned_name, summary.strip()])
            else:
                print(f"Skipped artist-summary mismatch for song: {data.get('id')}")

    # Close files
    songs_f.close()
    genres_f.close()
    summaries_f.close()

    print(f"✅ CSV files saved: {output_dates}, {output_genres}, {output_summaries}")

# Example usage
metadata_jsonl_to_csv('../../scrapers/musicbrainz/musicbrainz_tracks_2023.jsonl',
                      '../neo4j/data/import/musicbrainz_dates_2023.csv',
                      '../neo4j/data/import/musicbrainz_genres_2023.csv',
                      '../neo4j/data/import/musicbrainz_summaries_2023.csv', )
