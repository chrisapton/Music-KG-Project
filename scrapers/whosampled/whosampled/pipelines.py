# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import logging
from itemadapter import ItemAdapter
from datetime import datetime
from scrapy.exceptions import DropItem
from whosampled.items import SampleItem, SampleRelationship


class WhoSampledPipeline:
    def process_item(self, item, spider):
        """
        Basic pipeline to clean and validate items
        """
        adapter = ItemAdapter(item)

        # Add timestamp if not present
        if 'timestamp' not in adapter or not adapter['timestamp']:
            adapter['timestamp'] = datetime.now().isoformat()

        return item


class JsonWriterPipeline:
    """
    Pipeline to save items to separate JSON files based on their type
    """

    def open_spider(self, spider):
        self.tracks_file = open('../../data/raw/whosampled_tracks_test.json', 'w')
        self.relationships_file = open('../../data/raw/whosampled_relationships.json', 'w')

        # Initialize empty lists
        self.tracks_file.write('[\n')
        self.relationships_file.write('[\n')

        # Track what we've already written to each file
        self.track_ids = set()
        self.relationship_ids = set()

        # Comma tracking for JSON arrays
        self.tracks_count = 0
        self.relationships_count = 0

    def close_spider(self, spider):
        # Close the JSON arrays
        self.tracks_file.write('\n]')
        self.relationships_file.write('\n]')

        # Close the files
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

            # Write to file with proper JSON formatting
            if self.tracks_count > 0:
                self.tracks_file.write(',\n')
            self.tracks_file.write(json.dumps(processed_item, ensure_ascii=False))
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

        # Write to file with proper JSON formatting
        if self.relationships_count > 0:
            self.relationships_file.write(',\n')
        self.relationships_file.write(json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False))
        self.relationships_count += 1

        return item