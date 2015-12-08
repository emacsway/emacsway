SELECT *
FROM
  (SELECT NULL AS entity_id,
          NULL AS `TIMESTAMP`,
          COUNT(*) AS active_entity_count,
          i.owner_id AS owner_id,
          SUM(entity_creations_count) AS entity_creations_count,
          SUM(views_count) AS views_count,
          SUM(internal_shares_count) AS internal_shares_count,
          SUM(comments_count) AS comments_count,
          SUM(external_shares_count) AS external_shares_count,
          SUM(external_likes_count) AS external_likes_count,
          SUM(internal_likes_count) AS internal_likes_count,
          SUM(clicks_count) AS clicks_count
   FROM
     (SELECT NULL AS `TIMESTAMP`,
             NULL AS user_id,
             e.entity_id AS entity_id,
             SUM(IF((event_id IN (%(entity_creations)s)), event_count, 0)) AS entity_creations_count,
             SUM(IF((event_id IN (%(views)s)), event_count, 0)) AS views_count,
             SUM(IF((event_id IN (%(internal_shares)s)), event_count, 0)) AS internal_shares_count,
             SUM(IF((event_id IN (%(comments)s)), event_count, 0)) AS comments_count,
             SUM(IF((event_id IN (%(external_shares)s)), event_count, 0)) AS external_shares_count,
             SUM(IF((event_id IN (%(external_likes)s)), event_count, 0)) AS external_likes_count,
             SUM(IF((event_id IN (%(internal_likes)s)), event_count, 0)) AS internal_likes_count,
             SUM(IF((event_id IN (%(clicks)s)), event_count, 0)) AS clicks_count
      FROM entity_events_daily AS e
      WHERE e.site_id = %(site_id)s
        AND e.category_id = %(category_id)s
        AND e.`timestamp` >= %(min_timestamp)s
        AND e.`timestamp` < %(max_timestamp)s
        AND e.event_id IN (%(entity_creations)s,
                           %(views)s,
                           %(internal_shares)s,
                           %(comments)s,
                           %(external_shares)s,
                           %(external_likes)s,
                           %(internal_likes)s,
                           %(clicks)s)
      GROUP BY e.entity_id
      HAVING created_entity_count >= %(min_entity_creation_count)s
      AND entity_creations_count+views_count+internal_shares_count+comments_count+external_shares_count+external_likes_count+internal_likes_count+clicks_count > 0) AS e
   LEFT JOIN stats_posts_meta AS i ON i.entity_id = e.entity_id
   GROUP BY i.owner_id) AS e LIMIT %(limit)s
OFFSET %(offset)s
