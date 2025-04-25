from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))

constraints = [
    """CREATE CONSTRAINT song_id_unique IF NOT EXISTS FOR (s:Song) REQUIRE s.id IS UNIQUE""",
    """CREATE CONSTRAINT artist_name_unique IF NOT EXISTS FOR (a:Artist) REQUIRE a.name IS UNIQUE""",
    """CREATE CONSTRAINT album_title_unique IF NOT EXISTS FOR (al:Album) REQUIRE al.title IS UNIQUE""",
    """CREATE CONSTRAINT year_value_unique IF NOT EXISTS FOR (y:Year) REQUIRE y.value IS UNIQUE"""
]

track_import = """
// Load WhoSampled tracks with proper relationships
LOAD CSV WITH HEADERS FROM 'file:///whosampled_tracks_all.csv' AS row

MERGE (s:Song {id: row.whosampled_id})
SET s.title = row.title,
    s.url = row.url,
    s.record_label = row.record_label

// Album node
WITH s, row
WHERE row.album IS NOT NULL AND trim(row.album) <> ""
MERGE (al:Album {title: row.album})
MERGE (s)-[:PART_OF_ALBUM]->(al)

// Year node for temporal analysis
MERGE (y:Year {value: toInteger(row.release_year)})
MERGE (s)-[:RELEASED_IN]->(y)

// Artist relationships
WITH s, split(row.artist, ';') AS artistList
UNWIND artistList AS artistName
MERGE (a:Artist {name: trim(artistName)})
MERGE (s)-[:HAS_ARTIST]->(a)
"""

relationship_import = """
LOAD CSV WITH HEADERS FROM 'file:///whosampled_relationships_all.csv' AS row
MATCH (source:Song {id: row.source_id})
MATCH (target:Song {id: row.target_id})
MERGE (source)-[r:SAMPLES]->(target)
SET r.source_timestamps = split(row.timestamp_in_source, ';'),
    r.target_timestamps = split(row.timestamp_in_target, ';');
"""

date_import = """
// Load release dates
LOAD CSV WITH HEADERS FROM 'file:///musicbrainz_dates_all.csv' AS row
MATCH (s:Song {id: row.id})
SET s.release_date = CASE 
        WHEN row.release_date <> '' THEN date(row.release_date)
        ELSE s.release_date
    END;
"""

genre_import = """
// Load genres
LOAD CSV WITH HEADERS FROM 'file:///musicbrainz_genres_all.csv' AS row
MATCH (s:Song {id: row.song_id})
MERGE (g:Genre {name: row.genre})
MERGE (s)-[:BELONGS_TO_GENRE]->(g);
"""

summary_import = """
// Load artist summaries
LOAD CSV WITH HEADERS FROM 'file:///musicbrainz_summaries_all.csv' AS row
MATCH (a:Artist {name: row.artist_name})
SET a.wikipedia_summary = row.wikipedia_summary;
"""

audio_features_import = """
LOAD CSV WITH HEADERS FROM 'file:///acousticbrainz.csv' AS row
MATCH (s:Song {id: row.whosampled_id})
SET
  s.danceability_danceable = toFloat(row.danceability_danceable),
  s.genre_dortmund_alternative = toFloat(row.genre_dortmund_alternative),
  s.genre_dortmund_blues = toFloat(row.genre_dortmund_blues),
  s.genre_dortmund_electronic = toFloat(row.genre_dortmund_electronic),
  s.genre_dortmund_folkcountry = toFloat(row.genre_dortmund_folkcountry),
  s.genre_dortmund_funksoulrnb = toFloat(row.genre_dortmund_funksoulrnb),
  s.genre_dortmund_jazz = toFloat(row.genre_dortmund_jazz),
  s.genre_dortmund_pop = toFloat(row.genre_dortmund_pop),
  s.genre_dortmund_raphiphop = toFloat(row.genre_dortmund_raphiphop),
  s.genre_dortmund_rock = toFloat(row.genre_dortmund_rock),
  s.genre_electronic_ambient = toFloat(row.genre_electronic_ambient),
  s.genre_electronic_dnb = toFloat(row.genre_electronic_dnb),
  s.genre_electronic_house = toFloat(row.genre_electronic_house),
  s.genre_electronic_techno = toFloat(row.genre_electronic_techno),
  s.genre_electronic_trance = toFloat(row.genre_electronic_trance),
  s.genre_rosamerica_cla = toFloat(row.genre_rosamerica_cla),
  s.genre_rosamerica_dan = toFloat(row.genre_rosamerica_dan),
  s.genre_rosamerica_hip = toFloat(row.genre_rosamerica_hip),
  s.genre_rosamerica_jaz = toFloat(row.genre_rosamerica_jaz),
  s.genre_rosamerica_pop = toFloat(row.genre_rosamerica_pop),
  s.genre_rosamerica_rhy = toFloat(row.genre_rosamerica_rhy),
  s.genre_rosamerica_roc = toFloat(row.genre_rosamerica_roc),
  s.genre_rosamerica_spe = toFloat(row.genre_rosamerica_spe),
  s.genre_tzanetakis_blu = toFloat(row.genre_tzanetakis_blu),
  s.genre_tzanetakis_cla = toFloat(row.genre_tzanetakis_cla),
  s.genre_tzanetakis_cou = toFloat(row.genre_tzanetakis_cou),
  s.genre_tzanetakis_dis = toFloat(row.genre_tzanetakis_dis),
  s.genre_tzanetakis_hip = toFloat(row.genre_tzanetakis_hip),
  s.genre_tzanetakis_jaz = toFloat(row.genre_tzanetakis_jaz),
  s.genre_tzanetakis_met = toFloat(row.genre_tzanetakis_met),
  s.genre_tzanetakis_pop = toFloat(row.genre_tzanetakis_pop),
  s.genre_tzanetakis_reg = toFloat(row.genre_tzanetakis_reg),
  s.genre_tzanetakis_roc = toFloat(row.genre_tzanetakis_roc),
  s.ismir04_rhythm_ChaChaCha = toFloat(row.ismir04_rhythm_ChaChaCha),
  s.ismir04_rhythm_Jive = toFloat(row.ismir04_rhythm_Jive),
  s.ismir04_rhythm_Quickstep = toFloat(row.ismir04_rhythm_Quickstep),
  s.ismir04_rhythm_Rumba_American = toFloat(row.`ismir04_rhythm_Rumba-American`),
  s.ismir04_rhythm_Rumba_International = toFloat(row.`ismir04_rhythm_Rumba-International`),
  s.ismir04_rhythm_Rumba_Misc = toFloat(row.`ismir04_rhythm_Rumba-Misc`),
  s.ismir04_rhythm_Samba = toFloat(row.ismir04_rhythm_Samba),
  s.ismir04_rhythm_Tango = toFloat(row.ismir04_rhythm_Tango),
  s.ismir04_rhythm_VienneseWaltz = toFloat(row.ismir04_rhythm_VienneseWaltz),
  s.ismir04_rhythm_Waltz = toFloat(row.ismir04_rhythm_Waltz),
  s.mood_acoustic_acoustic = toFloat(row.mood_acoustic_acoustic),
  s.mood_aggressive_aggressive = toFloat(row.mood_aggressive_aggressive),
  s.mood_electronic_electronic = toFloat(row.mood_electronic_electronic),
  s.mood_happy_happy = toFloat(row.mood_happy_happy),
  s.mood_party = toFloat(row.mood_party_party),
  s.mood_relaxed = toFloat(row.mood_relaxed_relaxed),
  s.mood_sad = toFloat(row.mood_sad_sad),
  s.timbre_bright = toFloat(row.timbre_bright),
  s.tonal_atonal_atonal = toFloat(row.tonal_atonal_tonal),
  s.voice_instrumental_voice = toFloat(row.voice_instrumental_voice);
"""

pagerank_projection = """
CALL gds.graph.project(
  'songGraph',
  'Song',
  'SAMPLES'
)
"""

pagerank_write = """
CALL gds.pageRank.write('songGraph', {
  writeProperty: 'pagerank'
})
YIELD nodePropertiesWritten, ranIterations
"""

community_graph = """
CALL gds.graph.project(
  'sampling_graph',
  'Song',
  {
    SAMPLES: {
      orientation: 'UNDIRECTED'
    }
  }
)
"""

community_detection = """
CALL gds.leiden.write('sampling_graph', {
  writeProperty: 'sampling_community'
})
"""

with driver.session() as session:
    for constraint in constraints:
        session.run(constraint)
    print("✅ Constraints created")
    session.run(track_import)
    print("✅ Track import completed")
    session.run(relationship_import)
    print("✅ Relationship import completed")
    session.run(date_import)
    print("✅ Date import completed")
    session.run(genre_import)
    print("✅ Genre import completed")
    session.run(summary_import)
    print("✅ Summary import completed")
    session.run(audio_features_import)
    print("✅ Audio features import completed")
    session.run(pagerank_projection)
    print("✅ Graph projected")
    session.run(pagerank_write)
    print("✅ PageRank scores written")
    session.run(community_graph)
    print("✅ Community graph projected")
    session.run(community_detection)
    print("✅ Community detection completed")

    print("✅ All imports completed")

driver.close()

