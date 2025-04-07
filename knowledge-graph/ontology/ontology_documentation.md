# Music Sampling Knowledge Graph Ontology

## Entities

- **Song**
  - Represents a specific track or piece of music.

- **Artist**
  - A person or group who performs or contributes to a song.

- **Genre**
  - A category or style of music.

- **Year**
  - The release year of a song or album.

- **Producer**
  - An individual responsible for the production of a song.

- **Album**
  - A collection of songs released together.

- **Popularity**
  - A quantitative or qualitative metric representing how well a song is received (e.g., chart rank, play counts).

## Relationships

- `SAMPLES (Song → Song)`
  - Indicates that one song samples another.
  - Properties
    - source_timestamps
    - target_timestamps

- `HAS_ARTIST (Song → Artist)`
  - Links a song to its performing artist(s).

- `HAS_PRODUCER (Song → Producer)`
  - Links a song to its producer(s).

- `BELONGS_TO_GENRE (Song → Genre)`
  - Associates a song with its genre(s).

- `RELEASED_IN (Song → Year)`
  - Connects a song with its release year.

- `PART_OF_ALBUM (Song → Album)`
  - Links a song to the album it is part of.

- `HAS_POPULARITY (Song → Popularity)`
  - Associates a song with its popularity metric(s).

- `RELATED_TO (Artist → Related Artist)`
  - Connects an artist with similar or influential artists.

## Data Properties (Attributes of Entities)

- **Song**
  - `title`: string
  - `id`: string

- **Artist**
  - `name`: string

- **Genre**
  - `name`: string

- **Year**
  - `value`: integer (e.g., 1997)

- **Producer**
  - `name`: string

- **Album**
  - `title`: string
  - `release_year`: integer

- **Popularity**
  - `score`: float or integer (depending on metric used)
  - `source`: string (e.g., Spotify, Last.fm)


---