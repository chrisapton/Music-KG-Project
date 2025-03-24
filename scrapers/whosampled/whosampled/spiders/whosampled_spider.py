import scrapy
from scrapy.loader import ItemLoader
from urllib.parse import urljoin
import re
import logging
import time
from datetime import datetime
from whosampled.items import SampleItem, SampleRelationship


class SampleSpider(scrapy.Spider):
    """
    Optimized Bidirectional WhoSampled Spider

    This spider implements a complete bidirectional crawling strategy with optimizations:
    1. Follows both "Contains samples of" and "Was sampled in" for every track
    2. Detects "See all" buttons to find tracks with many samples
    3. Visits dedicated /samples and /sampled pages for tracks with many samples
    4. Only processes the first page of results from dedicated pages
    """
    name = "samples"
    allowed_domains = ["whosampled.com"]
    start_urls = ["https://www.whosampled.com/browse/year/2024/"]

    def __init__(self, *args, **kwargs):
        super(SampleSpider, self).__init__(*args, **kwargs)
        # Track visited URLs to avoid duplicates
        self.visited_urls = set()
        # Track sampling relationships to avoid duplicates
        self.sample_relationships = set()

        # Separate depth limits for forward and reverse crawling
        self.forward_depth_limit = kwargs.get('forward_depth_limit', 5)  # Default to 5
        self.reverse_depth_limit = kwargs.get('reverse_depth_limit', 5)  # Default to 5

        # Pegnination limit
        self.pagination_count = 1

        # Track statistics
        self.stats = {
            'tracks_processed': 0,
            'relationships_found': 0,
            'forward_relationships': 0,
            'reverse_relationships': 0,
            'see_all_samples_found': 0,
            'see_all_sampled_found': 0
        }

    def parse(self, response):
        """
        Parse the year page and extract links to each track
        """
        try:
            # Extract track links from the page
            track_links = response.css('h3.trackName a[itemprop="url"]::attr(href)').getall()

            self.logger.info(f"Found {len(track_links)} tracks on page {response.url}")

            # Follow each track link
            for link in track_links:
                full_url = urljoin(response.url, link)
                if full_url not in self.visited_urls:
                    self.visited_urls.add(full_url)
                    time.sleep(3)  # explicit delay to avoid being blocked
                    yield scrapy.Request(
                        url=full_url,
                        callback=self.parse_track,
                        meta={'track_type': 'initial', 'depth': 0}
                    )

            # Follow pagination if it exists
            next_page = response.css('span.next a::attr(href)').get()
            if next_page and self.pagination_count <= 10:
                self.pagination_count += 1
                self.logger.info(f"Following pagination link: {next_page}")
                next_url = urljoin(response.url, next_page)
                if next_url not in self.visited_urls:
                    self.visited_urls.add(next_url)
                    time.sleep(3)  # explicit delay to avoid being blocked
                    yield scrapy.Request(url=next_url, callback=self.parse)

        except Exception as e:
            self.logger.error(f"Error parsing page {response.url}: {str(e)}")

    def parse_track(self, response):
        """
        Parse individual track pages to extract detailed information
        """
        time.sleep(2)  # explicit delay to avoid being blocked
        try:
            # Get metadata about this request
            current_depth = response.meta.get('depth', 0)
            track_type = response.meta.get('track_type', 'unknown')

            self.logger.info(f"Parsing track: {response.url} (Type: {track_type}, Depth: {current_depth})")

            # Create a new item loader
            loader = ItemLoader(item=SampleItem(), response=response)

            # Extract basic track info
            track_title = response.css('div.trackInfo h1::text').get()
            if track_title:
                loader.add_value('title', self.clean_text(track_title))

            artist_names = response.css('div.trackInfo h1 a::text').getall()
            if artist_names:
                loader.add_value('artist', [self.clean_text(a) for a in artist_names])

            loader.add_value('url', str(response.url))

            # Extract album information
            album = response.css('div.release-name a::text').get()
            if album:
                loader.add_value('album', self.clean_text(album))

            # Extract label information
            label = response.css('div.label-details span::text').get()
            if label:
                loader.add_value('record_label', self.clean_text(label))

            # Extract release year
            release_year = response.css('div.label-details a::text').get()
            if release_year:
                year_match = re.search(r'\d{4}', release_year)
                if year_match:
                    loader.add_value('release_year', year_match.group(0))

            # Extract producer information
            producers = response.css('div.track-metainfo span.producer a::text').getall()
            if producers:
                loader.add_value('producer', [self.clean_text(p) for p in producers])

            # Extract youtube link
            youtube_link = response.css('div.media-container iframe::attr(src)').get()
            if youtube_link is not None:
                loader.add_value('youtube_link', youtube_link)

            # Get the track ID from the URL
            url_parts = response.url.split('/')
            track_id = '/'.join(url_parts[-3:-1]) if len(url_parts) > 2 else None
            loader.add_value('whosampled_id', track_id)

            # Add timestamp
            loader.add_value('timestamp', datetime.now().isoformat())

            # Get the track item
            track_item = loader.load_item()

            # Update statistics
            self.stats['tracks_processed'] += 1

            # Yield the track item
            yield track_item

            # BIDIRECTIONAL APPROACH WITH "SEE ALL" DETECTION:
            # Process both directions for every track

            # Process "Contains samples of" section (forward direction)
            if current_depth < self.forward_depth_limit:
                yield from self.process_samples_forward(response, track_id, current_depth)

            # Process "Was sampled in" section (reverse direction)
            if current_depth < self.reverse_depth_limit:
                yield from self.process_samplers_reverse(response, track_id, current_depth)

        except Exception as e:
            self.logger.error(f"Error parsing track {response.url}: {str(e)}")

    def process_samples_forward(self, response, track_id, current_depth):
        """
        Process the "Contains samples of" section with "See all" detection
        (Forward direction)
        """
        try:
            # First check for "See all" button for samples
            see_all_samples = response.xpath(
                './/header[.//h3[contains(text(), "Contains")]]/following-sibling::div//a[contains(@class, "btn") and contains(text(), "see all")]/@href'
            ).get()

            if see_all_samples:
                self.logger.info(f"Found 'See all' button for samples in track {track_id}")
                self.stats['see_all_samples_found'] += 1

                # Follow the "See all" link for samples
                samples_url = urljoin(response.url, see_all_samples)
                if samples_url not in self.visited_urls:
                    self.visited_urls.add(samples_url)
                    time.sleep(1) # explicit delay to avoid being blocked
                    yield scrapy.Request(
                        url=samples_url,
                        callback=self.parse_samples_page,
                        meta={
                            'source_track_id': track_id,
                            'depth': current_depth + 1
                        }
                    )
            else:
                # Process inline samples from the track page
                contains_section = response.xpath(
                    './/header[.//h3[contains(text(), "Contains")]]/following-sibling::table[1]//td[@class="tdata__td1"]'
                )

                if contains_section:
                    self.logger.info(f"Processing {len(contains_section)} inline samples in track {track_id}")

                    # Extract sampling relationships from the entries
                    for entry in contains_section:
                        time.sleep(1)  # explicit delay to avoid being blocked
                        # Get the sample link
                        sample_link = entry.css('a::attr(href)').get()

                        if sample_link:
                            # Follow the link to the sample page to get detailed information
                            full_url = urljoin(response.url, sample_link)
                            if full_url not in self.visited_urls:
                                self.visited_urls.add(full_url)
                                yield scrapy.Request(
                                    url=full_url,
                                    callback=self.parse_sample_page,
                                    meta={
                                        'source_track_id': track_id,
                                        'depth': current_depth + 1
                                    }
                                )

                else:
                    self.logger.info(f"No 'Contains samples' section found for track {track_id}")

        except Exception as e:
            self.logger.error(f"Error processing samples for {response.url}: {str(e)}")

    def parse_samples_page(self, response):
        """
        Parse the dedicated samples page (first page only)
        """
        try:
            source_track_id = response.meta.get('source_track_id')
            current_depth = response.meta.get('depth', 0)

            self.logger.info(f"Parsing samples page for track {source_track_id}: {response.url}")

            # Extract all samples from the page
            sample_entries = response.css('td.tdata__td1')

            self.logger.info(f"Found {len(sample_entries)} samples on dedicated samples page for {source_track_id}")

            for entry in sample_entries:
                # Get the sample link
                sample_link = entry.css('a::attr(href)').get()

                if sample_link:
                    # Follow the link to the sample page to get detailed information
                    full_url = urljoin(response.url, sample_link)
                    if full_url not in self.visited_urls:
                        self.visited_urls.add(full_url)
                        time.sleep(1)  # explicit delay to avoid being blocked
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_sample_page,
                            meta={
                                'source_track_id': source_track_id,
                                'depth': current_depth
                            }
                        )

        except Exception as e:
            self.logger.error(f"Error parsing samples page {response.url}: {str(e)}")

    def parse_sample_page(self, response):
        """
        Parse a sample page to extract detailed sampling information
        and follow links to the sampled track
        """
        try:
            source_track_id = response.meta.get('source_track_id')
            current_depth = response.meta.get('depth', 0)

            self.logger.info(f"Parsing sample page: {response.url}")

            # Extract the sampled track information (target)
            target_entry_box = response.css('div.sampleEntryBox')[1] if len(
                response.css('div.sampleEntryBox')) > 1 else None

            if target_entry_box:
                # Get the target track URL
                target_url = target_entry_box.css('a.trackName::attr(href)').get()
                target_url_parts = target_url.split('/')
                target_track_id = '/'.join(target_url_parts[-3:-1]) if len(target_url_parts) > 2 else None

                # Create relationship ID
                relationship = f'{source_track_id}-samples-{target_track_id}'

                # Check if we've already processed this relationship
                if relationship not in self.sample_relationships and target_track_id:
                    self.sample_relationships.add(relationship)

                    # Create a new relationship item
                    rel_loader = ItemLoader(item=SampleRelationship(), response=response)
                    rel_loader.add_value('source_track_id', source_track_id)
                    rel_loader.add_value('target_track_id', target_track_id)

                    # Extract timestamps from source
                    source_entry_box = response.css('div.sampleEntryBox')[0]
                    source_timestamps = source_entry_box.css('div.timing-wrapper span::text').getall()
                    if source_timestamps:
                        rel_loader.add_value('timestamp_in_source', source_timestamps)

                    # Extract timestamps from target
                    target_timestamps = target_entry_box.css('div.timing-wrapper span::text').getall()
                    if target_timestamps:
                        rel_loader.add_value('timestamp_in_target', target_timestamps)

                    # Update statistics
                    self.stats['relationships_found'] += 1
                    self.stats['forward_relationships'] += 1

                    # Yield the relationship
                    yield rel_loader.load_item()

                # Follow the link to the target track page
                if target_url:
                    full_url = urljoin(response.url, target_url)
                    if full_url not in self.visited_urls:
                        self.visited_urls.add(full_url)
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_track,
                            meta={
                                'track_type': 'sampled',
                                'depth': current_depth
                            }
                        )

        except Exception as e:
            self.logger.error(f"Error parsing sample page {response.url}: {str(e)}")

    def process_samplers_reverse(self, response, track_id, current_depth):
        """
        Process "Was sampled in" section with "See all" detection
        (Reverse direction)
        """
        try:
            # First check for "See all" button for samplers
            see_all_sampled = response.xpath(
                './/header[.//h3[contains(text(), "Sampled")]]/following-sibling::div//a[contains(@class, "btn") and contains(text(), "see all")]/@href'
            ).get()

            if see_all_sampled:
                self.logger.info(f"Found 'See all' button for samplers in track {track_id}")
                self.stats['see_all_sampled_found'] += 1

                # Follow the "See all" link for samplers
                sampled_url = urljoin(response.url, see_all_sampled)
                if sampled_url not in self.visited_urls:
                    self.visited_urls.add(sampled_url)
                    time.sleep(1)  # explicit delay to avoid being blocked
                    yield scrapy.Request(
                        url=sampled_url,
                        callback=self.parse_sampled_page,
                        meta={
                            'source_track_id': track_id,
                            'depth': current_depth + 1
                        }
                    )
            else:
                # Process inline samplers from the track page
                sampled_in_section = response.xpath(
                    './/header[.//h3[contains(text(), "Sampled")]]/following-sibling::table[1]//td[@class="tdata__td1"]'
                )

                if sampled_in_section:
                    self.logger.info(f"Processing {len(sampled_in_section)} inline samplers in track {track_id}")

                    # Process the samplers directly from this page
                    for entry in sampled_in_section:
                        # Get the sample link
                        sample_link = entry.css('a::attr(href)').get()

                        if sample_link:
                            # Follow the link to the sample page to get detailed information
                            full_url = urljoin(response.url, sample_link)
                            if full_url not in self.visited_urls:
                                self.visited_urls.add(full_url)
                                time.sleep(1) # explicit delay to avoid being blocked
                                yield scrapy.Request(
                                    url=full_url,
                                    callback=self.parse_sample_page_reverse,
                                    meta={
                                        'target_track_id': track_id,  # This track was sampled
                                        'depth': current_depth + 1
                                    }
                                )
                else:
                    self.logger.info(f"No 'Sampled in' section found for track {track_id}")

        except Exception as e:
            self.logger.error(f"Error processing samplers for {response.url}: {str(e)}")

    def parse_sampled_page(self, response):
        """
        Parse the dedicated sampled page (first page only)
        """
        try:
            source_track_id = response.meta.get('source_track_id')
            current_depth = response.meta.get('depth', 0)

            self.logger.info(f"Parsing sampled page for track {source_track_id}: {response.url}")

            # Extract all samplers from the page
            sampler_entries = response.css('td.tdata__td1')

            self.logger.info(f"Found {len(sampler_entries)} samplers on dedicated sampled page for {source_track_id}")

            for entry in sampler_entries:
                # Get the sample link
                sample_link = entry.css('a::attr(href)').get()

                if sample_link:
                    # Follow the link to the sample page to get detailed information
                    full_url = urljoin(response.url, sample_link)
                    if full_url not in self.visited_urls:
                        self.visited_urls.add(full_url)
                        time.sleep(1)  # explicit delay to avoid being blocked
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_sample_page_reverse,
                            meta={
                                'target_track_id': source_track_id,  # This track was sampled
                                'depth': current_depth
                            }
                        )

            # Note: We're not following pagination links as per user's requirement

        except Exception as e:
            self.logger.error(f"Error parsing sampled page {response.url}: {str(e)}")

    def parse_sample_page_reverse(self, response):
        """
        Parse a sample page in reverse direction
        (From sampler to sampled)
        """
        try:
            target_track_id = response.meta.get('target_track_id')
            current_depth = response.meta.get('depth', 0)

            self.logger.info(f"Parsing sample page (reverse): {response.url}")

            # Extract the sampler track information (source)
            source_entry_box = response.css('div.sampleEntryBox')[0] if len(
                response.css('div.sampleEntryBox')) > 0 else None

            if source_entry_box:
                # Get the source track URL
                source_url = source_entry_box.css('a.trackName::attr(href)').get()
                source_url_parts = source_url.split('/')
                source_track_id = '/'.join(source_url_parts[-3:-1]) if len(source_url_parts) > 2 else None

                # Create relationship ID
                relationship = f'{source_track_id}-samples-{target_track_id}'

                # Check if we've already processed this relationship
                if relationship not in self.sample_relationships and source_track_id:
                    self.sample_relationships.add(relationship)

                    # Create a new relationship item
                    rel_loader = ItemLoader(item=SampleRelationship(), response=response)
                    rel_loader.add_value('source_track_id', source_track_id)
                    rel_loader.add_value('target_track_id', target_track_id)

                    # Extract timestamps from source
                    source_timestamps = source_entry_box.css('div.timing-wrapper span::text').getall()
                    if source_timestamps:
                        rel_loader.add_value('timestamp_in_source', source_timestamps)

                    # Extract timestamps from target
                    target_entry_box = response.css('div.sampleEntryBox')[1] if len(
                        response.css('div.sampleEntryBox')) > 1 else None
                    if target_entry_box:
                        target_timestamps = target_entry_box.css('div.timing-wrapper span::text').getall()
                        if target_timestamps:
                            rel_loader.add_value('timestamp_in_target', target_timestamps)

                    # Update statistics
                    self.stats['relationships_found'] += 1
                    self.stats['reverse_relationships'] += 1

                    # Yield the relationship
                    yield rel_loader.load_item()

                # Follow the link to the source track page
                if source_url:
                    full_url = urljoin(response.url, source_url)
                    if full_url not in self.visited_urls:
                        self.visited_urls.add(full_url)
                        yield scrapy.Request(
                            url=full_url,
                            callback=self.parse_track,
                            meta={
                                'track_type': 'sampler',
                                'depth': current_depth
                            }
                        )

        except Exception as e:
            self.logger.error(f"Error parsing sample page (reverse) {response.url}: {str(e)}")

    def clean_text(self, text):
        """Clean and normalize text data"""
        if not text:
            return None
        return text.strip().replace('\n', ' ').replace('\r', '')

    def closed(self, reason):
        """Log statistics when spider closes"""
        self.logger.info(f"Spider closed: {reason}")
        self.logger.info(f"Tracks processed: {self.stats['tracks_processed']}")
        self.logger.info(f"Relationships found: {self.stats['relationships_found']}")
        self.logger.info(f"Forward relationships: {self.stats['forward_relationships']}")
        self.logger.info(f"Reverse relationships: {self.stats['reverse_relationships']}")
        self.logger.info(f"'See all' samples buttons found: {self.stats['see_all_samples_found']}")
        self.logger.info(f"'See all' sampled buttons found: {self.stats['see_all_sampled_found']}")
