/* Groups and counts the number of crawls by status */

SELECT left(status, 14), count(status) FROM crawled_websites GROUP BY left(status, 14) ORDER BY count(status) DESC;