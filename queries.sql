-- Ideas -----------------------------------------------------------------------

-- name: idea_create :one
INSERT INTO ideas_versioned (id, version, name, contents, managed)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM ideas_versioned), 1, ?, ?, ?)
RETURNING id;

-- name: idea_get_by_id :one
SELECT * FROM ideas WHERE id = ?;

-- name: idea_get_by_name :one
SELECT * FROM ideas WHERE name = ?;

-- name: idea_list :many
SELECT * FROM ideas ORDER BY name;

-- name: idea_update :exec
INSERT INTO ideas_versioned (id, version, name, contents, managed)
SELECT ideas.id,
       ideas.version + 1,
       ?, ?, ?
FROM ideas WHERE ideas.id = ?;

-- name: idea_delete :exec
INSERT INTO ideas_versioned (id, version, name, contents, managed, deleted)
SELECT ideas.id,
       (SELECT MAX(version) + 1 FROM ideas_versioned WHERE ideas_versioned.id = ideas.id),
       ideas.name, ideas.contents, ideas.managed, 1
FROM ideas WHERE ideas.id = ?;

-- name: idea_bump_version :exec
INSERT INTO ideas_versioned (id, version, name, contents, managed)
SELECT ideas.id,
       ideas.version + 1,
       ideas.name, ideas.contents, ideas.managed
FROM ideas WHERE ideas.id = ?;

-- Tags ------------------------------------------------------------------------

-- name: tag_create :one
INSERT INTO tags_versioned (id, version, name)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM tags_versioned), 1, ?)
RETURNING id;

-- name: tag_get_by_id :one
SELECT * FROM tags WHERE id = ?;

-- name: tag_list :many
SELECT * FROM tags ORDER BY name;

-- name: tag_update :exec
INSERT INTO tags_versioned (id, version, name)
SELECT tags.id,
       tags.version + 1,
       ?
FROM tags WHERE tags.id = ?;

-- name: tag_delete :exec
INSERT INTO tags_versioned (id, version, name, deleted)
SELECT tags.id,
       (SELECT MAX(version) + 1 FROM tags_versioned WHERE tags_versioned.id = tags.id),
       tags.name, 1
FROM tags WHERE tags.id = ?;

-- Idea-Tag junction -----------------------------------------------------------

-- name: idea_tag_add :exec
INSERT INTO idea_tags (idea_id, idea_version, tag_id, deleted)
VALUES (?, ?, ?, 0);

-- name: idea_tag_remove :exec
INSERT INTO idea_tags (idea_id, idea_version, tag_id, deleted)
VALUES (?, ?, ?, 1);

-- name: idea_tag_list :many
SELECT DISTINCT jt.tag_id
FROM idea_tags jt
WHERE jt.idea_id = ?
  AND jt.deleted = 0
  AND jt.idea_version = (
      SELECT MAX(it2.idea_version)
      FROM idea_tags it2
      WHERE it2.idea_id = jt.idea_id AND it2.tag_id = jt.tag_id
  );

-- Relationships ---------------------------------------------------------------

-- name: relationship_create :one
INSERT INTO relationships_versioned (id, version, underlying_idea_id, kind, metadata, from_idea_id, to_idea_id)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM relationships_versioned), 1, ?, ?, ?, ?, ?)
RETURNING id;

-- name: relationship_get_by_id :one
SELECT * FROM relationships WHERE id = ?;

-- name: relationship_list :many
SELECT * FROM relationships ORDER BY id;

-- name: relationship_list_by_from :many
SELECT * FROM relationships WHERE from_idea_id = ? ORDER BY id;

-- name: relationship_list_by_to :many
SELECT * FROM relationships WHERE to_idea_id = ? ORDER BY id;

-- name: relationship_list_by_involving :many
SELECT * FROM relationships
WHERE from_idea_id = ? OR to_idea_id = ? OR underlying_idea_id = ?
ORDER BY id;

-- name: relationship_update :exec
INSERT INTO relationships_versioned (id, version, underlying_idea_id, kind, metadata, from_idea_id, to_idea_id)
SELECT relationships.id,
       relationships.version + 1,
       relationships.underlying_idea_id,
       ?, ?,
       relationships.from_idea_id,
       relationships.to_idea_id
FROM relationships WHERE relationships.id = ?;

-- name: relationship_delete :exec
INSERT INTO relationships_versioned (id, version, underlying_idea_id, kind, metadata, from_idea_id, to_idea_id, deleted)
SELECT relationships.id,
       (SELECT MAX(version) + 1 FROM relationships_versioned rv WHERE rv.id = relationships.id),
       relationships.underlying_idea_id, relationships.kind, relationships.metadata,
       relationships.from_idea_id, relationships.to_idea_id, 1
FROM relationships WHERE relationships.id = ?;

-- Sources ---------------------------------------------------------------------

-- name: source_create :one
INSERT INTO sources_versioned (id, version, underlying_idea_id, slug, meta_title, meta_authors, meta_original_year, original_year_is_circa, edition_year, edition_year_is_circa, edition, translators, publisher)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM sources_versioned), 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
RETURNING id;

-- name: source_get_by_id :one
SELECT * FROM sources WHERE id = ?;

-- name: source_get_by_slug :one
SELECT * FROM sources WHERE slug = ?;

-- name: source_list :many
SELECT * FROM sources ORDER BY meta_title;

-- name: source_update :exec
INSERT INTO sources_versioned (id, version, underlying_idea_id, slug, fact_sheet, meta_title, meta_authors, meta_original_year, original_year_is_circa, edition_year, edition_year_is_circa, edition, translators, publisher)
SELECT sources.id,
       sources.version + 1,
       sources.underlying_idea_id,
       ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
FROM sources WHERE sources.id = ?;

-- name: source_delete :exec
INSERT INTO sources_versioned (id, version, underlying_idea_id, slug, fact_sheet, meta_title, meta_authors, meta_original_year, original_year_is_circa, edition_year, edition_year_is_circa, edition, translators, publisher, deleted)
SELECT sources.id,
       (SELECT MAX(version) + 1 FROM sources_versioned sv WHERE sv.id = sources.id),
       sources.underlying_idea_id, sources.slug, sources.fact_sheet, sources.meta_title, sources.meta_authors,
       sources.meta_original_year, sources.original_year_is_circa, sources.edition_year,
       sources.edition_year_is_circa, sources.edition, sources.translators, sources.publisher, 1
FROM sources WHERE sources.id = ?;

-- Hierarchies -----------------------------------------------------------------

-- name: hierarchy_create :one
INSERT INTO hierarchies_versioned (id, version, name, notes, check_tags)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM hierarchies_versioned), 1, ?, ?, ?)
RETURNING id;

-- name: hierarchy_get_by_id :one
SELECT * FROM hierarchies WHERE id = ?;

-- name: hierarchy_list :many
SELECT * FROM hierarchies ORDER BY name;

-- name: hierarchy_update :exec
INSERT INTO hierarchies_versioned (id, version, name, notes, check_tags)
SELECT hierarchies.id,
       hierarchies.version + 1,
       ?, ?, ?
FROM hierarchies WHERE hierarchies.id = ?;

-- name: hierarchy_delete :exec
INSERT INTO hierarchies_versioned (id, version, name, notes, check_tags, deleted)
SELECT hierarchies.id,
       (SELECT MAX(version) + 1 FROM hierarchies_versioned hv WHERE hv.id = hierarchies.id),
       hierarchies.name, hierarchies.notes, hierarchies.check_tags, 1
FROM hierarchies WHERE hierarchies.id = ?;

-- name: hierarchy_bump_version :exec
INSERT INTO hierarchies_versioned (id, version, name, notes, check_tags)
SELECT hierarchies.id,
       hierarchies.version + 1,
       hierarchies.name, hierarchies.notes, hierarchies.check_tags
FROM hierarchies WHERE hierarchies.id = ?;

-- Hierarchy-Idea membership ---------------------------------------------------

-- name: hierarchy_idea_add :exec
INSERT INTO hierarchy_ideas (hierarchy_id, hierarchy_version, idea_id, parent_idea_id, relationship_id, deleted)
VALUES (?, ?, ?, ?, ?, 0);

-- name: hierarchy_idea_remove :exec
INSERT INTO hierarchy_ideas (hierarchy_id, hierarchy_version, idea_id, deleted)
VALUES (?, ?, ?, 1);

-- name: hierarchy_idea_list :many
SELECT DISTINCT jt.idea_id, jt.parent_idea_id, jt.relationship_id
FROM hierarchy_ideas jt
WHERE jt.hierarchy_id = ?
  AND jt.deleted = 0
  AND jt.hierarchy_version = (
      SELECT MAX(hi2.hierarchy_version)
      FROM hierarchy_ideas hi2
      WHERE hi2.hierarchy_id = jt.hierarchy_id AND hi2.idea_id = jt.idea_id
  );
