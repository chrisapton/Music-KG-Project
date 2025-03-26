# Property Definitions for Music Sampling Knowledge Graph Ontology

This document provides detailed specifications for all properties in the music sampling knowledge graph ontology, including data types, constraints, and descriptions.

## Core Entity Properties

### Song Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| title | String | The title of the song | Required, Max length: 200 | "Bitter Sweet Symphony" |
| release_date | Date | The date when the song was officially released | Format: YYYY-MM-DD | "1997-06-16" |
| duration | Integer | The length of the song in seconds | Min: 1 | 368 |
| popularity_score | Float | A normalized score representing the song's popularity | Range: 0.0-100.0 | 87.5 |
| isrc | String | International Standard Recording Code | Format: CC-XXX-YY-NNNNN | "GBAYE9700267" |
| lyrics | Text | The lyrics of the song | Optional | "Cause it's a bitter sweet symphony..." |
| bpm | Integer | Beats per minute | Range: 20-300 | 86 |
| key | String | Musical key of the song | Format: [A-G][#b]?[m]? | "C#m" |

### Artist Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| name | String | The name of the artist | Required, Max length: 100 | "The Verve" |
| active_period_start | Date | When the artist began their career | Format: YYYY-MM-DD | "1990-01-01" |
| active_period_end | Date | When the artist ended their career (if applicable) | Format: YYYY-MM-DD, Optional | "2009-08-12" |
| biography | Text | Biographical information about the artist | Optional | "The Verve were an English rock band..." |
| location | String | Geographic origin of the artist | Optional | "Wigan, England" |
| mbid | String | MusicBrainz Identifier | Format: UUID | "8adff013-d8b9-4c74-8db1-459e3e1dffaf" |

### Sample Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| start_time | Float | Start time of the sample in the original song (seconds) | Min: 0.0 | 15.3 |
| end_time | Float | End time of the sample in the original song (seconds) | > start_time | 23.7 |
| duration | Float | Length of the sample in seconds | Calculated: end_time - start_time | 8.4 |
| modification_type | Enum | How the sample was modified | Values: ["None", "Pitch Shifted", "Time Stretched", "Chopped", "Reversed", "Filtered", "Other"] | "Pitch Shifted" |
| clearance_status | Enum | Legal status of the sample | Values: ["Cleared", "Uncleared", "Disputed", "Unknown"] | "Disputed" |
| prominence | Integer | How prominent the sample is in the new song | Range: 1-10 | 8 |
| loop_count | Integer | Number of times the sample is repeated | Min: 0 | 4 |

### Genre Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| name | String | The name of the genre | Required, Max length: 50 | "Trip Hop" |
| description | Text | Description of the genre | Optional | "A genre of electronic music that originated..." |
| era | String | The time period when the genre was most popular | Optional | "1990s" |
| parent_genre | Reference | Reference to a parent genre | Optional | "Electronic" |
| origin_location | String | Geographic origin of the genre | Optional | "Bristol, UK" |
| origin_year | Integer | Year when the genre emerged | Format: YYYY | 1991 |

### Album Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| title | String | The title of the album | Required, Max length: 200 | "Urban Hymns" |
| release_date | Date | The date when the album was officially released | Format: YYYY-MM-DD | "1997-09-29" |
| label | String | The record label that released the album | Optional | "Hut Records" |
| format | Enum | The format of the album | Values: ["CD", "Vinyl", "Cassette", "Digital", "Other"] | "CD" |
| cover_art | URL | Link to the album cover image | Optional | "https://example.com/covers/urban_hymns.jpg" |
| mbid | String | MusicBrainz Identifier | Format: UUID | "af2801d5-6c0e-4bc7-9930-9e52b67e4471" |
| total_tracks | Integer | Total number of tracks on the album | Min: 1 | 13 |

### Release Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| release_date | Date | The date of this specific release | Format: YYYY-MM-DD | "1997-09-29" |
| format | Enum | The format of this release | Values: ["CD", "Vinyl", "Cassette", "Digital", "Other"] | "Vinyl" |
| label | String | The record label for this release | Optional | "Hut Records" |
| country | String | Country where released | ISO 3166-1 alpha-2 | "GB" |
| catalog_number | String | Catalog number assigned by label | Optional | "HUTDG82" |
| barcode | String | Barcode for the release | Optional | "724384479824" |

### Popularity Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| stream_count | Integer | Number of streams across platforms | Min: 0 | 45000000 |
| chart_position | Integer | Highest chart position achieved | Min: 1 | 2 |
| sales_figures | Integer | Number of units sold | Min: 0 | 350000 |
| listener_count | Integer | Number of unique listeners | Min: 0 | 2500000 |
| peak_date | Date | Date of peak popularity | Format: YYYY-MM-DD | "1997-07-12" |
| certification | Enum | Sales certification level | Values: ["None", "Gold", "Platinum", "Multi-Platinum", "Diamond"] | "Platinum" |

### TimePeriod Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| start_year | Integer | Starting year of the period | Format: YYYY | 1990 |
| end_year | Integer | Ending year of the period | Format: YYYY, >= start_year | 1999 |
| name | String | Name of the time period | Optional | "1990s" |
| description | Text | Description of musical characteristics of the period | Optional | "The 1990s saw the rise of grunge..." |

## Secondary Entity Properties

### Label Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| name | String | The name of the record label | Required, Max length: 100 | "Hut Records" |
| founding_date | Date | When the label was founded | Format: YYYY-MM-DD | "1990-01-01" |
| location | String | Headquarters location | Optional | "London, UK" |
| parent_company | String | Parent company of the label | Optional | "Virgin Records" |
| status | Enum | Current operational status | Values: ["Active", "Defunct", "Subsidiary"] | "Defunct" |

### Instrument Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| name | String | The name of the instrument | Required, Max length: 100 | "Roland TR-808" |
| type | Enum | Type of instrument | Values: ["Percussion", "String", "Wind", "Electronic", "Other"] | "Electronic" |
| family | String | Instrument family | Optional | "Drum Machine" |
| year_introduced | Integer | Year when the instrument was introduced | Format: YYYY | 1980 |
| manufacturer | String | Manufacturer of the instrument | Optional | "Roland" |

### SampleTechnique Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| name | String | Name of the sampling technique | Required, Max length: 100 | "Chopping" |
| description | Text | Description of how the technique works | Optional | "Dividing a sample into smaller segments..." |
| first_used_date | Date | When the technique was first used | Format: YYYY-MM-DD | "1986-03-12" |
| equipment | String | Equipment typically used for this technique | Optional | "MPC2000XL" |
| difficulty | Integer | Relative difficulty to execute | Range: 1-10 | 7 |

### Event Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| date | Date | When the event occurred | Format: YYYY-MM-DD | "1996-08-15" |
| location | String | Where the event occurred | Optional | "Olympic Studios, London" |
| participants | Array[Reference] | Artists involved in the event | Optional | ["Andrew Loog Oldham Orchestra", "The Verve"] |
| description | Text | Description of the event | Optional | "Recording session where samples were created" |

## Relationship Properties

### SAMPLES Relationship Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| sample_timestamp | Float | Timestamp in derivative song where sample appears (seconds) | Min: 0.0 | 0.0 |
| duration | Float | Duration of sample use in derivative song (seconds) | Min: 0.1 | 240.0 |
| clearance_status | Enum | Legal status of the sample | Values: ["Cleared", "Uncleared", "Disputed", "Unknown"] | "Disputed" |
| sample_type | Enum | Type of sampling used | Values: ["Loop", "One-shot", "Chop", "Interpolation"] | "Loop" |
| legal_case | String | Reference to legal case if disputed | Optional | "ABKCO Music, Inc. v. The Verve" |

### CREATED_BY Relationship Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| role | Enum | Role in creation | Values: ["Primary", "Featured", "Uncredited"] | "Primary" |
| contribution_type | String | Specific contribution | Optional | "Songwriter" |
| year | Integer | Year of contribution | Format: YYYY | 1997 |

### BELONGS_TO_GENRE Relationship Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| confidence | Float | Confidence score of genre classification | Range: 0.0-1.0 | 0.85 |
| primary | Boolean | Whether this is the primary genre | Default: false | true |
| source | String | Source of genre classification | Optional | "MusicBrainz" |

### INFLUENCED Relationship Properties

| Property | Data Type | Description | Constraints | Example |
|----------|-----------|-------------|------------|---------|
| strength | Integer | Strength of influence | Range: 1-10 | 8 |
| time_period | String | When the influence occurred | Optional | "1990s" |
| source | String | Source of influence information | Optional | "Interview in Rolling Stone, 1998" |
| influence_type | Enum | Type of influence | Values: ["Stylistic", "Technical", "Lyrical", "Conceptual"] | "Stylistic" |

## Data Type Definitions

| Data Type | Format | Description |
|-----------|--------|-------------|
| String | Text | Basic text string |
| Text | Long text | Extended text content |
| Integer | Whole number | Numeric value without decimals |
| Float | Decimal number | Numeric value with decimals |
| Date | YYYY-MM-DD | Calendar date |
| Boolean | true/false | Binary value |
| Enum | Predefined values | Selection from a fixed set of values |
| URL | Valid URL format | Web address |
| Reference | Entity identifier | Reference to another entity in the ontology |
| Array | List of values | Collection of values of the same type |

## Property Constraints

| Constraint Type | Description | Example |
|-----------------|-------------|---------|
| Required | Property must have a value | title is Required |
| Min | Minimum numeric value | duration Min: 1 |
| Max | Maximum numeric value | popularity_score Max: 100.0 |
| Range | Valid range of values | Range: 0.0-1.0 |
| Format | Specific format requirement | Format: YYYY-MM-DD |
| Max length | Maximum string length | Max length: 200 |
| Values | Enumeration of allowed values | Values: ["CD", "Vinyl", "Cassette", "Digital", "Other"] |
| Default | Default value if not specified | Default: false |
