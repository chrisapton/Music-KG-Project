import json

year = 2024
type = 'relationships'
all_records = []
seen = set()

for i in range(1, 11):
    filename = f"../data/raw/whosampled_{type}_{year}_{i}.jsonl"
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            record = json.loads(line.strip())
            record_str = json.dumps(record, sort_keys=True)  # Use this for deduplication
            if record_str not in seen:
                seen.add(record_str)
                all_records.append(record)

# Save the deduplicated result
with open(f"../data/processed/whosampled_{type}_{year}.jsonl", 'w', encoding='utf-8') as outfile:
    for record in all_records:
        json.dump(record, outfile)
        outfile.write("\n")

print(f"Finished. Total unique records: {len(all_records)}")