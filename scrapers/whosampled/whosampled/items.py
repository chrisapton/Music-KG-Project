# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SampleItem(scrapy.Item):
    """
    Item for storing information about a track and its sampling relationships
    """
    title = scrapy.Field()
    artist = scrapy.Field()
    album = scrapy.Field()
    record_label = scrapy.Field()
    release_year = scrapy.Field()
    url = scrapy.Field()
    producer = scrapy.Field()
    timestamp = scrapy.Field()
    whosampled_id = scrapy.Field()
    youtube_link = scrapy.Field()


class SampleRelationship(scrapy.Item):
    """
    Item for storing detailed information about a sampling relationship
    """
    source_track_id = scrapy.Field()  # ID of the track that samples
    target_track_id = scrapy.Field()  # ID of the track being sampled

    timestamp_in_source = scrapy.Field()
    timestamp_in_target = scrapy.Field()
    timestamp = scrapy.Field()
