from yoyo import step

# -- Enum tables ---------------------------------------------------------------

step(
    """
    CREATE TABLE relationship_kind_enum (
        value TEXT PRIMARY KEY NOT NULL
    )
    """,
    "DROP TABLE IF EXISTS relationship_kind_enum",
)

step(
    """
    INSERT INTO relationship_kind_enum (value) VALUES
        ('miscellaneous'),
        ('property'),
        ('enumeration'),
        ('multidef'),
        ('contradiction'),
        ('influence')
    """,
)

# -- Disciplines ---------------------------------------------------------------

step(
    """
    CREATE TABLE disciplines_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        name TEXT NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version)
    )
    """,
    "DROP TABLE IF EXISTS disciplines_versioned",
)

step(
    """
    CREATE VIEW disciplines AS
    SELECT dv.*
    FROM disciplines_versioned dv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM disciplines_versioned
        GROUP BY id
    ) latest ON dv.id = latest.id AND dv.version = latest.max_version
    WHERE dv.deleted = 0
    """,
    "DROP VIEW IF EXISTS disciplines",
)

# -- Tags ----------------------------------------------------------------------

step(
    """
    CREATE TABLE tags_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        name TEXT NOT NULL,
        discipline_id INTEGER,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version),
        FOREIGN KEY (discipline_id) REFERENCES disciplines_versioned(id)
    )
    """,
    "DROP TABLE IF EXISTS tags_versioned",
)

step(
    """
    CREATE VIEW tags AS
    SELECT tv.*
    FROM tags_versioned tv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM tags_versioned
        GROUP BY id
    ) latest ON tv.id = latest.id AND tv.version = latest.max_version
    WHERE tv.deleted = 0
    """,
    "DROP VIEW IF EXISTS tags",
)

# -- Ideas ---------------------------------------------------------------------

step(
    """
    CREATE TABLE ideas_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        name TEXT NOT NULL,
        contents TEXT,
        managed INTEGER NOT NULL DEFAULT 0,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version)
    )
    """,
    "DROP TABLE IF EXISTS ideas_versioned",
)

step(
    """
    CREATE VIEW ideas AS
    SELECT iv.*
    FROM ideas_versioned iv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM ideas_versioned
        GROUP BY id
    ) latest ON iv.id = latest.id AND iv.version = latest.max_version
    WHERE iv.deleted = 0
    """,
    "DROP VIEW IF EXISTS ideas",
)

step(
    """
    CREATE UNIQUE INDEX ideas_versioned_name_unique
    ON ideas_versioned(name)
    WHERE version = (
        SELECT MAX(version) FROM ideas_versioned iv2 WHERE iv2.id = ideas_versioned.id
    ) AND deleted = 0
    """,
)

# -- Idea-Tag junction ---------------------------------------------------------

step(
    """
    CREATE TABLE idea_tags (
        id INTEGER PRIMARY KEY,
        idea_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (idea_id) REFERENCES ideas_versioned(id),
        FOREIGN KEY (tag_id) REFERENCES tags_versioned(id),
        UNIQUE (idea_id, tag_id)
    )
    """,
    "DROP TABLE IF EXISTS idea_tags",
)

# -- Idea-Discipline junction --------------------------------------------------

step(
    """
    CREATE TABLE idea_disciplines (
        id INTEGER PRIMARY KEY,
        idea_id INTEGER NOT NULL,
        discipline_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (idea_id) REFERENCES ideas_versioned(id),
        FOREIGN KEY (discipline_id) REFERENCES disciplines_versioned(id),
        UNIQUE (idea_id, discipline_id)
    )
    """,
    "DROP TABLE IF EXISTS idea_disciplines",
)

# -- Relationships -------------------------------------------------------------

step(
    """
    CREATE TABLE relationships_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        underlying_idea_id INTEGER NOT NULL,
        kind TEXT NOT NULL REFERENCES relationship_kind_enum(value),
        metadata TEXT,
        from_idea_id INTEGER NOT NULL,
        to_idea_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version),
        FOREIGN KEY (underlying_idea_id) REFERENCES ideas_versioned(id),
        FOREIGN KEY (from_idea_id) REFERENCES ideas_versioned(id),
        FOREIGN KEY (to_idea_id) REFERENCES ideas_versioned(id),
        CHECK (underlying_idea_id != from_idea_id),
        CHECK (underlying_idea_id != to_idea_id),
        CHECK (from_idea_id != to_idea_id)
    )
    """,
    "DROP TABLE IF EXISTS relationships_versioned",
)

step(
    """
    CREATE VIEW relationships AS
    SELECT rv.*
    FROM relationships_versioned rv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM relationships_versioned
        GROUP BY id
    ) latest ON rv.id = latest.id AND rv.version = latest.max_version
    WHERE rv.deleted = 0
    """,
    "DROP VIEW IF EXISTS relationships",
)

# -- Sources -------------------------------------------------------------------

step(
    """
    CREATE TABLE sources_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        underlying_idea_id INTEGER NOT NULL,
        slug TEXT NOT NULL,
        fact_sheet TEXT,
        meta_title TEXT NOT NULL,
        meta_authors TEXT NOT NULL DEFAULT '[]',
        meta_original_year INTEGER,
        original_year_is_circa INTEGER,
        edition_year INTEGER,
        edition_year_is_circa INTEGER,
        edition TEXT,
        translators TEXT NOT NULL DEFAULT '[]',
        publisher TEXT NOT NULL DEFAULT '',
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version),
        FOREIGN KEY (underlying_idea_id) REFERENCES ideas_versioned(id)
    )
    """,
    "DROP TABLE IF EXISTS sources_versioned",
)

step(
    """
    CREATE VIEW sources AS
    SELECT sv.*
    FROM sources_versioned sv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM sources_versioned
        GROUP BY id
    ) latest ON sv.id = latest.id AND sv.version = latest.max_version
    WHERE sv.deleted = 0
    """,
    "DROP VIEW IF EXISTS sources",
)

# -- Hierarchies ---------------------------------------------------------------

step(
    """
    CREATE TABLE hierarchies_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        name TEXT NOT NULL,
        notes TEXT,
        check_tags TEXT NOT NULL DEFAULT '[]',
        discipline_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version),
        FOREIGN KEY (discipline_id) REFERENCES disciplines_versioned(id)
    )
    """,
    "DROP TABLE IF EXISTS hierarchies_versioned",
)

step(
    """
    CREATE VIEW hierarchies AS
    SELECT hv.*
    FROM hierarchies_versioned hv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM hierarchies_versioned
        GROUP BY id
    ) latest ON hv.id = latest.id AND hv.version = latest.max_version
    WHERE hv.deleted = 0
    """,
    "DROP VIEW IF EXISTS hierarchies",
)

# -- Hierarchy-Idea membership -------------------------------------------------

step(
    """
    CREATE TABLE hierarchy_ideas (
        id INTEGER PRIMARY KEY,
        hierarchy_id INTEGER NOT NULL,
        idea_id INTEGER NOT NULL,
        parent_id INTEGER,
        relationship_id INTEGER,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (hierarchy_id) REFERENCES hierarchies_versioned(id),
        FOREIGN KEY (idea_id) REFERENCES ideas_versioned(id),
        FOREIGN KEY (parent_id) REFERENCES hierarchy_ideas(id),
        FOREIGN KEY (relationship_id) REFERENCES relationships_versioned(id),
        UNIQUE (hierarchy_id, parent_id, idea_id)
    )
    """,
    "DROP TABLE IF EXISTS hierarchy_ideas",
)

# -- Timelines -----------------------------------------------------------------

step(
    """
    CREATE TABLE timelines_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        name TEXT NOT NULL,
        notes TEXT,
        check_tags TEXT NOT NULL DEFAULT '[]',
        discipline_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version),
        FOREIGN KEY (discipline_id) REFERENCES disciplines_versioned(id)
    )
    """,
    "DROP TABLE IF EXISTS timelines_versioned",
)

step(
    """
    CREATE VIEW timelines AS
    SELECT tv.*
    FROM timelines_versioned tv
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM timelines_versioned
        GROUP BY id
    ) latest ON tv.id = latest.id AND tv.version = latest.max_version
    WHERE tv.deleted = 0
    """,
    "DROP VIEW IF EXISTS timelines",
)

# -- Timeline-Idea membership --------------------------------------------------

step(
    """
    CREATE TABLE timeline_ideas (
        id INTEGER PRIMARY KEY,
        timeline_id INTEGER NOT NULL,
        idea_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        end_date TEXT,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (timeline_id) REFERENCES timelines_versioned(id),
        FOREIGN KEY (idea_id) REFERENCES ideas_versioned(id),
        UNIQUE (timeline_id, idea_id, date, end_date)
    )
    """,
    "DROP TABLE IF EXISTS timeline_ideas",
)

# -- Analyses ------------------------------------------------------------------

step(
    """
    CREATE TABLE analyses_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        title TEXT NOT NULL,
        contents TEXT NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version)
    )
    """,
    "DROP TABLE IF EXISTS analyses_versioned",
)

step(
    """
    CREATE VIEW analyses AS
    SELECT av.*
    FROM analyses_versioned av
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM analyses_versioned
        GROUP BY id
    ) latest ON av.id = latest.id AND av.version = latest.max_version
    WHERE av.deleted = 0
    """,
    "DROP VIEW IF EXISTS analyses",
)

# -- Analysis attachment junction tables ----------------------------------------

step(
    """
    CREATE TABLE analysis_ideas (
        id INTEGER PRIMARY KEY,
        analysis_id INTEGER NOT NULL,
        idea_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (analysis_id) REFERENCES analyses_versioned(id),
        FOREIGN KEY (idea_id) REFERENCES ideas_versioned(id),
        UNIQUE (analysis_id, idea_id)
    )
    """,
    "DROP TABLE IF EXISTS analysis_ideas",
)

step(
    """
    CREATE TABLE analysis_hierarchies (
        id INTEGER PRIMARY KEY,
        analysis_id INTEGER NOT NULL,
        hierarchy_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (analysis_id) REFERENCES analyses_versioned(id),
        FOREIGN KEY (hierarchy_id) REFERENCES hierarchies_versioned(id),
        UNIQUE (analysis_id, hierarchy_id)
    )
    """,
    "DROP TABLE IF EXISTS analysis_hierarchies",
)

step(
    """
    CREATE TABLE analysis_timelines (
        id INTEGER PRIMARY KEY,
        analysis_id INTEGER NOT NULL,
        timeline_id INTEGER NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (analysis_id) REFERENCES analyses_versioned(id),
        FOREIGN KEY (timeline_id) REFERENCES timelines_versioned(id),
        UNIQUE (analysis_id, timeline_id)
    )
    """,
    "DROP TABLE IF EXISTS analysis_timelines",
)

# -- Attachments ---------------------------------------------------------------

step(
    """
    CREATE TABLE attachments_versioned (
        id INTEGER NOT NULL,
        version INTEGER NOT NULL,
        mime TEXT NOT NULL,
        inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        deleted INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (id, version)
    )
    """,
    "DROP TABLE IF EXISTS attachments_versioned",
)

step(
    """
    CREATE VIEW attachments AS
    SELECT av.*
    FROM attachments_versioned av
    INNER JOIN (
        SELECT id, MAX(version) AS max_version
        FROM attachments_versioned
        GROUP BY id
    ) latest ON av.id = latest.id AND av.version = latest.max_version
    WHERE av.deleted = 0
    """,
    "DROP VIEW IF EXISTS attachments",
)
