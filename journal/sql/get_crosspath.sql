WITH RECURSIVE cable_path (location_id, id, destination_id, main_src_id, level) AS
  (SELECT location_id,
          id,
          destination_id,
          id AS main_src_id,
          0
   FROM journal_crosspoint
   WHERE destination_id IS NULL
     UNION ALL
     SELECT j.location_id,
            j.id,
            j.destination_id,
            cp.main_src_id,
            cp.level + 1
     FROM journal_crosspoint j
     INNER JOIN cable_path cp ON cp.id = j.destination_id)

SELECT id,
       location_id,
       destination_id as parent,
       main_src_id,
       level
FROM cable_path
WHERE main_src_id in {}
ORDER BY main_src_id, level, id