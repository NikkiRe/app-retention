WITH activity AS (
    SELECT DISTINCT user_id, CAST(active_at AS DATE) AS active_date FROM events
), eligible AS (
    SELECT u.*, h.day,
           CAST(date_trunc('week', installed_at) AS DATE) AS cohort,
           CAST(installed_at AS DATE) + CAST(h.day AS INTEGER) AS target_date
    FROM users u CROSS JOIN (VALUES (1), (7), (30)) h(day)
    WHERE CAST(installed_at AS DATE) + CAST(h.day AS INTEGER) <= CAST($cutoff AS DATE)
)
SELECT u.cohort, u.channel, u.onboarded, u.day, count(*) AS eligible_users,
       count(a.user_id) AS retained_users,
       count(a.user_id)::DOUBLE / count(*) AS retention
FROM eligible u LEFT JOIN activity a ON u.user_id = a.user_id AND u.target_date = a.active_date
GROUP BY u.cohort, u.channel, u.onboarded, u.day
ORDER BY u.cohort, u.channel, u.onboarded, u.day
