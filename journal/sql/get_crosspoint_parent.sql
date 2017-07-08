WITH RECURSIVE
Rec (id, source_id, location_id)
AS (
      SELECT *, id AS main_id
        FROM journal_crosspoint
       WHERE source_id IS NULL
    UNION ALL
      SELECT cp.*, r.main_id AS main_id
        FROM Rec r
        JOIN journal_crosspoint cp ON (r.id = cp.source_id)
)
SELECT main_id
  FROM Rec
 WHERE id = {}
 