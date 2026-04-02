-- name: idea_create :execlastid
INSERT INTO ideas_versioned (id, version, name, contents, managed)
VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM ideas_versioned), 1, ?, ?, ?);

-- name: idea_get_by_id :one
SELECT * FROM ideas WHERE id = ?;

-- name: idea_get_by_name :one
SELECT * FROM ideas WHERE name = ?;

-- name: idea_list :many
SELECT * FROM ideas ORDER BY name;
