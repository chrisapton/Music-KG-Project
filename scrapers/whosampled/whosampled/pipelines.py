import json
import re
import logging
from itemadapter import ItemAdapter
from datetime import datetime
from scrapy.exceptions import DropItem
from whosampled.items import SampleItem, SampleRelationship


class WhoSampledPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Add timestamp if not present
        if 'timestamp' not in adapter or not adapter['timestamp']:
            adapter['timestamp'] = datetime.now().isoformat()

        # Clean timestamp fields
        timestamp_fields = ['timestamp_in_source', 'timestamp_in_target']

        for field in timestamp_fields:
            if field in adapter:
                raw_value = adapter.get(field, [])

                if isinstance(raw_value, list):
                    # Filter out non-timestamp elements
                    cleaned = [
                        ts for ts in raw_value
                        if re.match(r'^\d+:\d+$', ts)
                    ]
                    adapter[field] = cleaned
                elif isinstance(raw_value, str):
                    adapter[field] = [raw_value] if re.match(r'^\d+:\d+$', raw_value) else []

        return item


class JsonWriterPipeline:
    """
    Pipeline to save items to separate JSON Lines files based on their type
    """

    def open_spider(self, spider):
        self.tracks_file = open('../../data/raw/whosampled_tracks_2024_1_10.jsonl', 'w', encoding='utf-8')
        self.relationships_file = open('../../data/raw/whosampled_relationships_2024_1_10.jsonl', 'w', encoding='utf-8')

        # Track what we've already written to each file
        self.track_ids = set()
        self.relationship_ids = set()

        self.tracks_count = 0
        self.relationships_count = 0

    def close_spider(self, spider):
        self.tracks_file.close()
        self.relationships_file.close()

        spider.logger.info(
            f"Saved {self.tracks_count} tracks and {self.relationships_count} relationships")

    def process_item(self, item, spider):
        # Determine item type and process accordingly
        if isinstance(item, SampleItem):
            return self._process_track_item(item, spider)
        elif isinstance(item, SampleRelationship):
            return self._process_relationship_item(item, spider)
        return item

    def _process_track_item(self, item, spider):
        """Process and save track items"""
        adapter = ItemAdapter(item)

        track_id = adapter.get('whosampled_id', '')[0]
        if track_id:
            if track_id in self.track_ids:
                return item

            # Add to our set of processed tracks
            self.track_ids.add(track_id)

            # Convert single-value lists to strings
            processed_item = {}
            for key, value in adapter.asdict().items():
                if isinstance(value, list) and len(value) == 1:
                    processed_item[key] = value[0]
                else:
                    processed_item[key] = value

            # Write to file as a single JSON line
            line = json.dumps(processed_item, ensure_ascii=False) + "\n"
            self.tracks_file.write(line)
            self.tracks_count += 1

        else:
            print(f"Missing whosampled_id for track: {adapter.get('title', '')}")

        return item

    def _process_relationship_item(self, item, spider):
        """Process and save relationship items"""
        adapter = ItemAdapter(item)

        # Create a unique identifier for this relationship
        source_id = adapter.get('source_track_id', '')
        target_id = adapter.get('target_track_id', '')
        relationship_id = f"{source_id}-samples-{target_id}"

        # Check if we've already saved this relationship
        if relationship_id in self.relationship_ids:
            return item

        # Add to our set of processed relationships
        self.relationship_ids.add(relationship_id)

        # Convert single-value lists to strings
        processed_item = {}
        for key, value in adapter.asdict().items():
            if isinstance(value, list) and len(value) == 1:
                processed_item[key] = value[0]
            else:
                processed_item[key] = value

        # Write to file as a single JSON line
        line = json.dumps(processed_item, ensure_ascii=False) + "\n"
        self.relationships_file.write(line)
        self.relationships_count += 1

        return item
