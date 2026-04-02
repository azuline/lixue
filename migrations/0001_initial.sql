-- initial
-- depends:

-- Enum tables -----------------------------------------------------------------

CREATE TABLE relationship_kind_enum (
    value TEXT PRIMARY KEY NOT NULL
);

INSERT INTO relationship_kind_enum (value) VALUES
    ('miscellaneous'),
    ('property'),
    ('enumeration'),
    ('multidef'),
    ('contradiction'),
    ('influence');

-- Tags ------------------------------------------------------------------------

CREATE TABLE tags_versioned (
    id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    name TEXT NOT NULL,
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version)
);

CREATE VIEW tags AS
SELECT tv.*
FROM tags_versioned tv
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM tags_versioned
    GROUP BY id
) latest ON tv.id = latest.id AND tv.version = latest.max_version
WHERE tv.deleted = 0;

-- Ideas -----------------------------------------------------------------------

CREATE TABLE ideas_versioned (
    id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    name TEXT NOT NULL,
    contents TEXT,
    managed BOOLEAN NOT NULL DEFAULT 0,
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version)
);

CREATE VIEW ideas AS
SELECT iv.*
FROM ideas_versioned iv
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM ideas_versioned
    GROUP BY id
) latest ON iv.id = latest.id AND iv.version = latest.max_version
WHERE iv.deleted = 0;

-- Idea-Tag junction -----------------------------------------------------------

CREATE TABLE idea_tags (
    idea_id INTEGER NOT NULL,
    idea_version INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (idea_id, idea_version, tag_id),
    FOREIGN KEY (idea_id, idea_version) REFERENCES ideas_versioned(id, version),
    FOREIGN KEY (tag_id) REFERENCES tags_versioned(id)
);

-- Relationships ---------------------------------------------------------------

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
    deleted BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version),
    FOREIGN KEY (underlying_idea_id) REFERENCES ideas_versioned(id),
    FOREIGN KEY (from_idea_id) REFERENCES ideas_versioned(id),
    FOREIGN KEY (to_idea_id) REFERENCES ideas_versioned(id),
    CHECK (underlying_idea_id != from_idea_id),
    CHECK (underlying_idea_id != to_idea_id),
    CHECK (from_idea_id != to_idea_id)
);

CREATE VIEW relationships AS
SELECT rv.*
FROM relationships_versioned rv
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM relationships_versioned
    GROUP BY id
) latest ON rv.id = latest.id AND rv.version = latest.max_version
WHERE rv.deleted = 0;

-- Sources ---------------------------------------------------------------------

CREATE TABLE sources_versioned (
    id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    underlying_idea_id INTEGER NOT NULL,
    slug TEXT NOT NULL,
    fact_sheet TEXT,
    meta_title TEXT NOT NULL,
    meta_authors TEXT NOT NULL DEFAULT '[]',
    meta_original_year INTEGER,
    original_year_is_circa BOOLEAN,
    edition_year INTEGER,
    edition_year_is_circa BOOLEAN,
    edition TEXT,
    translators TEXT NOT NULL DEFAULT '[]',
    publisher TEXT NOT NULL DEFAULT '',
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version),
    FOREIGN KEY (underlying_idea_id) REFERENCES ideas_versioned(id)
);

CREATE VIEW sources AS
SELECT sv.*
FROM sources_versioned sv
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM sources_versioned
    GROUP BY id
) latest ON sv.id = latest.id AND sv.version = latest.max_version
WHERE sv.deleted = 0;

-- Hierarchies -----------------------------------------------------------------

CREATE TABLE hierarchies_versioned (
    id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    name TEXT NOT NULL,
    notes TEXT,
    check_tags TEXT NOT NULL DEFAULT '[]',
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (id, version)
);

CREATE VIEW hierarchies AS
SELECT hv.*
FROM hierarchies_versioned hv
INNER JOIN (
    SELECT id, MAX(version) AS max_version
    FROM hierarchies_versioned
    GROUP BY id
) latest ON hv.id = latest.id AND hv.version = latest.max_version
WHERE hv.deleted = 0;

-- Hierarchy-Idea membership ---------------------------------------------------

CREATE TABLE hierarchy_ideas (
    hierarchy_id INTEGER NOT NULL,
    hierarchy_version INTEGER NOT NULL,
    idea_id INTEGER NOT NULL,
    parent_idea_id INTEGER,
    relationship_id INTEGER,
    deleted BOOLEAN NOT NULL DEFAULT 0,
    inserted_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    PRIMARY KEY (hierarchy_id, hierarchy_version, idea_id),
    FOREIGN KEY (hierarchy_id, hierarchy_version) REFERENCES hierarchies_versioned(id, version),
    FOREIGN KEY (idea_id) REFERENCES ideas_versioned(id),
    FOREIGN KEY (parent_idea_id) REFERENCES ideas_versioned(id),
    FOREIGN KEY (relationship_id) REFERENCES relationships_versioned(id)
);
