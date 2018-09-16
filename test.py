import psycopg2

conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
mentions_cursor = conn.cursor()
mentions_cursor.execute("SELECT mention_identifier  FROM mentions WHERE confidence=100")
insert_cursor = conn.cursor()
count = 0
for article in mentions_cursor:
    count += 1
    print(count)
    insert_cursor.execute("""INSERT INTO articles (source_url) VALUES (%s)
                  ON CONFLICT (source_url) DO NOTHING""", [article[0]])
    conn.commit()
