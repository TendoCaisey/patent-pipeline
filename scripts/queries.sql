
--   Patent Intelligence — SQL Analysis Queries(Writing the queries for each participant)




-- Q1: Top Inventors (who has most patents?)

SELECT
    i.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM relationships r
JOIN inventors i ON r.inventor_id = i.inventor_id
WHERE r.inventor_id IS NOT NULL
GROUP BY i.inventor_id, i.name
ORDER BY patent_count DESC
LIMIT 20;


-- Q2: Top Companies (most patents owned)

SELECT
    c.name,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM relationships r
JOIN companies c ON r.company_id = c.company_id
WHERE r.company_id IS NOT NULL
GROUP BY c.company_id, c.name
ORDER BY patent_count DESC
LIMIT 20;



-- Q3: Countries (most patents produced)

SELECT
    i.country,
    COUNT(DISTINCT r.patent_id) AS patent_count
FROM relationships r
JOIN inventors i ON r.inventor_id = i.inventor_id
WHERE r.inventor_id IS NOT NULL
GROUP BY i.country
ORDER BY patent_count DESC
LIMIT 20;



-- Q4: Trends Over Time (patents per year)
SELECT
    year,
    COUNT(*) AS total_patents
FROM patents
WHERE year IS NOT NULL
GROUP BY year
ORDER BY year ASC;



-- Q5: JOIN Query
-- Patents with their inventors and companies

SELECT
    p.patent_id,
    p.title,
    p.year,
    i.name        AS inventor_name,
    c.name        AS company_name
FROM patents p
LEFT JOIN relationships ri
    ON p.patent_id = ri.patent_id AND ri.inventor_id IS NOT NULL
LEFT JOIN inventors i
    ON ri.inventor_id = i.inventor_id
LEFT JOIN relationships rc
    ON p.patent_id = rc.patent_id AND rc.company_id IS NOT NULL
LEFT JOIN companies c
    ON rc.company_id = c.company_id
LIMIT 50;



-- Q6: CTE Query (WITH statement)
-- Top inventors with their most recent patent

WITH inventor_stats AS (
    SELECT
        i.inventor_id,
        i.name,
        COUNT(DISTINCT r.patent_id)  AS total_patents,
        MAX(p.year)                  AS latest_year
    FROM inventors i
    JOIN relationships r ON i.inventor_id = r.inventor_id
    JOIN patents p       ON r.patent_id   = p.patent_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name
),
top_inventors AS (
    SELECT *
    FROM inventor_stats
    WHERE total_patents >= 3
)
SELECT
    name,
    total_patents,
    latest_year
FROM top_inventors
ORDER BY total_patents DESC
LIMIT 20;



-- Q7: Ranking Query (window functions)
-- Rank inventors by patent count

SELECT
    name,
    patent_count,
    RANK()       OVER (ORDER BY patent_count DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY patent_count DESC) AS dense_rank,
    NTILE(4)     OVER (ORDER BY patent_count DESC) AS quartile
FROM (
    SELECT
        i.name,
        COUNT(DISTINCT r.patent_id) AS patent_count
    FROM relationships r
    JOIN inventors i ON r.inventor_id = i.inventor_id
    WHERE r.inventor_id IS NOT NULL
    GROUP BY i.inventor_id, i.name
) ranked
ORDER BY patent_count DESC
LIMIT 30;