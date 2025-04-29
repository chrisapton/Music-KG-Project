# **Music Sampling Knowledge Graph Ontology**

## **Entities**

- **Song**
  - Represents a specific track or piece of music.

- **Artist**
  - A person or group who performs or contributes to a song.

- **Genre**
  - A category or style of music.

- **Album**
  - A collection of songs released together.

- **Year**
  - The release year of a song or album.

---

## **Relationships**

- **SAMPLES (Song → Song)**
  - Indicates that one song samples another.
  - **Properties**
    - **source_timestamps**: Timestamps in the sampling song.
    - **target_timestamps**: Timestamps in the sampled song.

- **HAS_ARTIST (Song → Artist)**
  - Links a song to its performing artist(s).

- **BELONGS_TO_GENRE (Song → Genre)**
  - Associates a song with its genre(s).

- **PART_OF_ALBUM (Song → Album)**
  - Links a song to the album it is part of.

- **RELEASED_IN (Song → Year)**
  - Connects a song with its release year.

---

## **Data Properties (Attributes of Entities)**

- **Song**
  - **title**: string
  - **release_date**: string (exact release date if available)
  - **record_label**: string (optional, label that released the song)
  - **wikipedia_summary**: string (optional, short description)
  - **url**: string (optional, external link to metadata)
  - **n2v**: list of floats (Node2Vec embedding vector)
  - **pagerank**: float (PageRank score based on sampling influence)
  - **sampling_community**: integer (community cluster from graph analysis)
  - **Audio Features**:
    - **danceability_danceable**
    - **timbre_bright**
    - **voice_instrumental_voice**
    - **tonal_atonal_atonal**
    - **mood_* (e.g., happy, sad, relaxed, aggressive)**
    - **genre_* (multiple genre classification scores)**
    - **ismir04_rhythm_* (rhythm pattern classification)**

- **Artist**
  - **name**: string
  - **wikipedia_summary**: string (optional)
  - **url**: string (optional)

- **Genre**
  - **name**: string

- **Album**
  - **title**: string
  - **release_date**: string (optional)

- **Year**
  - **value**: integer (e.g., 1997)
  
---
