WITH RECURSIVE
Rec (id, destination_id, location_id)
AS (
      SELECT *, id AS main_id
        FROM journal_crosspoint
       WHERE destination_id IS NULL
    UNION ALL
      SELECT cp.*, r.main_id AS main_id
        FROM Rec r
        JOIN journal_crosspoint cp ON (r.id = cp.destination_id)
)
SELECT main_id
  FROM Rec
 WHERE id = {}
 