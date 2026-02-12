PRAGMA foreign_keys = ON;

CREATE TABLE matches (
  match_id TEXT PRIMARY KEY,
  kit_id TEXT,
  cm_total REAL,
  segments INTEGER,
  longest_segment REAL,
  predicted_range_low INTEGER,
  predicted_range_high INTEGER,
  maternal_paternal_hint TEXT,
  tree_size INTEGER,
  tree_confidence REAL,
  notes TEXT
);

CREATE TABLE shared_matches (
  match_id_a TEXT,
  match_id_b TEXT,
  shared_strength REAL,
  shared_cm_est REAL,
  shared_segments_est INTEGER
);

CREATE TABLE places (
  place_id TEXT PRIMARY KEY,
  place_name TEXT,
  parish_or_county TEXT,
  state TEXT,
  country TEXT,
  lat REAL,
  lon REAL
);

CREATE TABLE persons (
  person_id TEXT PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  birth_year INTEGER,
  death_year INTEGER,
  sex TEXT,
  birth_place TEXT,
  death_place TEXT,
  place_id_birth TEXT,
  place_id_death TEXT
);

CREATE TABLE relationships (
  child_person_id TEXT,
  parent_person_id TEXT,
  relationship_type TEXT
);

CREATE TABLE match_tree_links (
  match_id TEXT,
  person_id TEXT,
  confidence_level REAL
);
