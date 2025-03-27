import graphviz

# Create a new directed graph
dot = graphviz.Digraph('Music_Sampling_Ontology', comment='Music Sampling Knowledge Graph Ontology')

# Set graph attributes
dot.attr(rankdir='TB', size='14,10', ratio='fill', fontsize='16', overlap='false', splines='true')
dot.attr('node', shape='box', style='filled', fillcolor='lightblue', fontname='Arial', margin='0.2')
dot.attr('edge', fontname='Arial', fontsize='10')

# Define node clusters for organization
with dot.subgraph(name='cluster_primary') as c:
    c.attr(label='Primary Entities', style='filled', color='lightgrey')
    
    # Primary Entities
    c.node('Song', 'Song\n(title, release_date, duration, popularity_score, isrc)')
    c.node('OriginalSong', 'OriginalSong')
    c.node('DerivativeSong', 'DerivativeSong')
    c.node('Artist', 'Artist\n(name, active_period, biography, location)')
    c.node('MusicGroup', 'MusicGroup')
    c.node('SoloArtist', 'SoloArtist')
    c.node('Producer', 'Producer')
    c.node('Sample', 'Sample\n(start_time, end_time, duration, modification_type, clearance_status)')
    c.node('Genre', 'Genre\n(name, description, era, parent_genre)')
    c.node('Album', 'Album\n(title, release_date, label, format, cover_art)')
    c.node('Release', 'Release\n(release_date, format, label, country)')
    c.node('Popularity', 'Popularity\n(stream_count, chart_position, sales_figures, listener_count)')
    c.node('TimePeriod', 'TimePeriod\n(start_year, end_year, name)')

with dot.subgraph(name='cluster_secondary') as c:
    c.attr(label='Secondary Entities', style='filled', color='lightgrey')
    
    # Secondary Entities
    c.node('Label', 'Label\n(name, founding_date, location)')
    c.node('Instrument', 'Instrument\n(name, type, family)')
    c.node('SampleTechnique', 'SampleTechnique\n(name, description, first_used_date)')
    c.node('Event', 'Event')
    c.node('Composition', 'Composition')
    c.node('Performance', 'Performance')
    c.node('Recording', 'Recording')
    c.node('SamplingEvent', 'SamplingEvent')

# Entity Hierarchies
dot.edge('Song', 'OriginalSong', label='is-a')
dot.edge('Song', 'DerivativeSong', label='is-a')
dot.edge('Artist', 'MusicGroup', label='is-a')
dot.edge('Artist', 'SoloArtist', label='is-a')
dot.edge('Artist', 'Producer', label='is-a')
dot.edge('Event', 'Composition', label='is-a')
dot.edge('Event', 'Performance', label='is-a')
dot.edge('Event', 'Recording', label='is-a')
dot.edge('Event', 'SamplingEvent', label='is-a')

# Primary Relationships
dot.edge('DerivativeSong', 'OriginalSong', label='SAMPLES', color='red', penwidth='2.0')
dot.edge('Song', 'Sample', label='HAS_SAMPLE', color='red')
dot.edge('Sample', 'Song', label='SAMPLED_IN', color='red')
dot.edge('Song', 'Artist', label='CREATED_BY', color='blue')
dot.edge('Song', 'Artist', label='PERFORMED_BY', color='blue')
dot.edge('Song', 'Producer', label='PRODUCED_BY', color='blue')
dot.edge('Song', 'Genre', label='BELONGS_TO_GENRE', color='green')
dot.edge('Song', 'TimePeriod', label='RELEASED_IN', color='green')
dot.edge('Song', 'Album', label='PART_OF', color='purple')
dot.edge('Song', 'Popularity', label='HAS_POPULARITY', color='orange')
dot.edge('Artist', 'Artist', label='INFLUENCED', color='blue', constraint='false')
dot.edge('Artist', 'Artist', label='COLLABORATED_WITH', color='blue', constraint='false')

# Secondary Relationships
dot.edge('Song', 'Label', label='RELEASED_BY', color='purple')
dot.edge('Album', 'Label', label='RELEASED_BY', color='purple')
dot.edge('Sample', 'SampleTechnique', label='USES_TECHNIQUE', color='brown')
dot.edge('Song', 'Instrument', label='RECORDED_USING', color='brown')
dot.edge('DerivativeSong', 'OriginalSong', label='DERIVED_FROM', color='red', style='dashed')
dot.edge('Sample', 'SamplingEvent', label='SAMPLED_AT_EVENT', color='brown')

# Add a legend
with dot.subgraph(name='cluster_legend') as c:
    c.attr(label='Legend', style='filled', color='white')
    c.node('legend_sampling', 'Sampling Relationships', shape='plaintext', fillcolor='white')
    c.node('legend_artist', 'Artist Relationships', shape='plaintext', fillcolor='white')
    c.node('legend_categorization', 'Categorization', shape='plaintext', fillcolor='white')
    c.node('legend_production', 'Production Relationships', shape='plaintext', fillcolor='white')
    c.node('legend_hierarchy', 'Hierarchy', shape='plaintext', fillcolor='white')
    
    c.edge('legend_sampling', 'legend_sampling', color='red', label='')
    c.edge('legend_artist', 'legend_artist', color='blue', label='')
    c.edge('legend_categorization', 'legend_categorization', color='green', label='')
    c.edge('legend_production', 'legend_production', color='purple', label='')
    c.edge('legend_hierarchy', 'legend_hierarchy', color='black', label='')

# Render the graph with improved layout
dot.attr(overlap='false', splines='ortho')
dot.render('/home/ubuntu/music_sampling_ontology/ontology_diagram_improved', format='png', cleanup=True)
print("Improved ontology diagram created at: /home/ubuntu/music_sampling_ontology/ontology_diagram_improved.png")
