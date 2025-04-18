# 🎶 **Music Sampling Knowledge Graph Ontology**

## 🗂️ **Entities**

- **Song**
  - Represents a specific track or piece of music.

- **Artist**
  - A person or group who performs or contributes to a song.

- **Genre**
  - A category or style of music.

- **Year**
  - The release year of a song or album.
  
- **Date**
  - The release date of a song or album.

- **Producer**
  - An individual responsible for the production of a song.

- **Album**
  - A collection of songs released together.

- **Popularity**
  - A quantitative or qualitative metric representing how well a song is received (e.g., chart rank, play counts).

- **Wikipedia Summary**
  - A brief textual description or biography of an artist or song, extracted from Wikipedia.

---

## 🔗 **Relationships**

- `SAMPLES (Song → Song)`
  - Indicates that one song samples another.
  - **Properties**
    - `source_timestamps`: Timestamps in the sampling song.
    - `target_timestamps`: Timestamps in the sampled song.

- `HAS_ARTIST (Song → Artist)`
  - Links a song to its performing artist(s).

- `HAS_PRODUCER (Song → Producer)`
  - Links a song to its producer(s).

- `BELONGS_TO_GENRE (Song → Genre)`
  - Associates a song with its genre(s).

- `RELEASED_IN (Song → Year)`
  - Connects a song with its release year.
  
- `RELEASED_DATE (Song → Date)`
  - Connects a song with its release date.

- `PART_OF_ALBUM (Song → Album)`
  - Links a song to the album it is part of.

- `HAS_POPULARITY (Song → Popularity)`
  - Associates a song with its popularity metric(s).

- `RELATED_TO (Artist → Related Artist)`
  - Connects an artist with similar or influential artists.

- `HAS_WIKIPEDIA_SUMMARY (Artist → Wikipedia Summary)`
  - Connects an artist to their Wikipedia summary for contextual information.

---

## 📝 **Data Properties (Attributes of Entities)**

- **Song**
  - `title`: string
  - `id`: string
  - `length`: integer (duration of the song in milliseconds)

- **Artist**
  - `name`: string

- **Genre**
  - `name`: string

- **Year**
  - `value`: integer (e.g., 1997)
  
- **Date**
  - `value`: string

- **Producer**
  - `name`: string

- **Album**
  - `title`: string
  - `release_year`: integer

- **Popularity**
  - `score`: float or integer (depending on metric used)
  - `source`: string (e.g., Spotify, Last.fm)

- **Wikipedia Summary**
  - `text`: string (a short description or biography sourced from Wikipedia)

---