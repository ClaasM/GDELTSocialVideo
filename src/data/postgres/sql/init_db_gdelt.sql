-- GDELT-specific

CREATE TABLE IF NOT EXISTS events (-- They are called "export" in the GDELT dataset, but events makes more sense
  -- Event ID and date attributes
  global_event_id          BIGINT PRIMARY KEY NOT NULL,
  sql_date                 INT    NOT NULL,
  month_year               INT    NOT NULL,
  year                     INT    NOT NULL,
  fraction_date            FLOAT  NOT NULL,
  -- Actor attributes
  actor1_code              TEXT,
  actor1_name              TEXT,
  actor1_country_code      TEXT,
  actor1_known_group_code  TEXT,
  actor1_ethnic_code       TEXT,
  actor1_religion1_code    TEXT,
  actor1_religion2_code    TEXT,
  actor1_type1_code        TEXT,
  actor1_type2_code        TEXT,
  actor1_type3_code        TEXT,
  actor2_code              TEXT,
  actor2_name              TEXT,
  actor2_country_code      TEXT,
  actor2_known_group_code  TEXT,
  actor2_ethnic_code       TEXT,
  actor2_religion1_code    TEXT,
  actor2_religion2_code    TEXT,
  actor2_type1_code        TEXT,
  actor2_type2_code        TEXT,
  actor2_type3_code        TEXT,
  -- Event action attributes
  is_root_event            BOOL   NOT NULL,
  event_code               TEXT   NOT NULL, -- These are "---" in very rare cases
  event_base_code          TEXT   NOT NULL,
  event_root_code          TEXT   NOT NULL,
  quad_class               INT    NOT NULL,
  goldstein_scale          FLOAT, -- This is null in very rare cases (TODO statistic)
  num_mentions             INT    NOT NULL,
  num_sources              INT    NOT NULL,
  num_articles             INT    NOT NULL,
  avg_tone                 FLOAT  NOT NULL,
  -- Event geography (actor 1)
  actor1_geo_type          INT    NOT NULL,
  actor1_geo_full_name     TEXT,
  actor1_geo_country_code  TEXT,
  actor1_geo_ADM1_code     TEXT,
  actor1_geo_ADM2_code     TEXT,
  actor1_geo_lat           FLOAT,
  actor1_geo_long          FLOAT,
  actor1_geo_feature_id    TEXT,
  -- Event geography (actor 2)
  actor2_geo_type          INT    NOT NULL,
  actor2_geo_fullName      TEXT,
  actor2_geo__country_code TEXT,
  actor2_geo_ADM1_code     TEXT,
  actor2_geo_ADM2_code     TEXT,
  actor2_geo_lat           TEXT,
  actor2_geo_long          TEXT,
  actor2_geo_feature_id    TEXT,
  -- Event geography (action)
  action_geo_type          INT    NOT NULL,
  action_geo_full_name     TEXT,
  action_geo_country_code  TEXT,
  action_geo_ADM1_code     TEXT,
  action_geo_ADM2_code     TEXT,
  action_geo_lat           TEXT,
  action_geo_long          TEXT,
  action_geo_feature_id    TEXT,
  -- Data management
  date_added               TEXT   NOT NULL,
  source_url               TEXT   NOT NULL -- Can't be a foreign key to Articles since it isn't actually always a url
);

CREATE TABLE IF NOT EXISTS mentions (
  -- Columns from the dataset
  global_event_id     BIGINT NOT NULL,
  event_time_date     BIGINT NOT NULL,
  mention_time_date   BIGINT NOT NULL,
  mention_type        INT    NOT NULL,
  mention_source_name TEXT, -- This is sometimes null (GDELT dataset impurities)
  mention_identifier  TEXT   NOT NULL,
  sentence_id         INT    NOT NULL,
  actor1_char_offset  INT    NOT NULL,
  actor2_char_offset  INT    NOT NULL,
  action_char_offset  INT    NOT NULL,
  in_raw_text         BOOL   NOT NULL,
  confidence          FLOAT  NOT NULL,
  mention_doc_len     INT    NOT NULL,
  mention_doc_tone    FLOAT  NOT NULL
);

-- INDICES
-- Indices are only created where they are really needed, because they take up space and slow down inserts/deletes
CREATE INDEX IF NOT EXISTS mentions_global_event_id_index
  ON public.mentions (global_event_id);
CREATE INDEX IF NOT EXISTS  mentions_mention_identifier_index
  ON public.mentions (mention_identifier);
CREATE INDEX IF NOT EXISTS  mentions_mention_source_name_index
  ON public.mentions (mention_source_name);
CREATE INDEX IF NOT EXISTS  events_source_url_index
  ON public.events (source_url);