import json
import csv


def tracks_jsonl_to_csv(jsonl_path, csv_path):
    with open(jsonl_path, 'r', encoding='utf-8') as infile, open(csv_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = [
            "title",
            "artist",  # multiple artists will be joined by `;`
            "url",
            "album",
            "record_label",
            "release_year",
            "whosampled_id",
            "timestamp"
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in infile:
            data = json.loads(line)

            # Handle multiple artists as a list or single string
            artist = data.get("artist", "")
            if isinstance(artist, list):
                artist_str = ";".join(artist)
            else:
                artist_str = artist

            writer.writerow({
                "title": data.get("title", ""),
                "artist": artist_str,
                "url": data.get("url", ""),
                "album": data.get("album", ""),
                "record_label": data.get("record_label", ""),
                "release_year": data.get("release_year", ""),
                "whosampled_id": data.get("whosampled_id", ""),
                "timestamp": data.get("timestamp", "")
            })

    print(f"✅ CSV saved to: {csv_path}")


def relationships_jsonl_to_csv(jsonl_path, csv_path):
    with open(jsonl_path, 'r', encoding='utf-8') as infile, open(csv_path, 'w', newline='', encoding='utf-8') as outfile:
        fieldnames = [
            "source_id",
            "target_id",
            "timestamp_in_source",
            "timestamp_in_target"
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in infile:
            data = json.loads(line)

            def normalize_timestamps(ts):
                if isinstance(ts, list):
                    return ";".join(ts)
                elif isinstance(ts, str):
                    return ts
                else:
                    return ""

            writer.writerow({
                "source_id": data.get("source_track_id", ""),
                "target_id": data.get("target_track_id", ""),
                "timestamp_in_source": normalize_timestamps(data.get("timestamp_in_source", "")),
                "timestamp_in_target": normalize_timestamps(data.get("timestamp_in_target", ""))
            })


# Example usage
# tracks_jsonl_to_csv("../../data/processed/whosampled_tracks_2022.jsonl", "../neo4j/data/import/whosampled_tracks_2022.csv")
relationships_jsonl_to_csv( "../../data/processed/whosampled_relationships_2022.jsonl",
                            "../neo4j/data/import/whosampled_relationships_2022.csv")