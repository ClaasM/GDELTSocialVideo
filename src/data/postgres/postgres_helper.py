import psycopg2

"""
TODO stuff like required columns, indexing, etc.
"""

SUCCESS = "Success"
from psycopg2.extensions import AsIs


class PostgresHelper:
    def __init__(self, ):
        self.conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
        self.c = self.conn.cursor()

    def is_crawled(self, website_url):
        """Checks if a website_url has already been successfully crawled."""
        try_again = ['500', '403']
        self.c.execute('SELECT status FROM articles WHERE website_url=%s', [website_url])
        result = self.c.fetchone()
        # If the status is a 3 digit status code we don't crawl again since thats unlikely to change,
        # except for those status codes that are marked as "try_again".
        # Any other issue (i.e. connectivity issues) lead to a re-crawl.
        crawled_successfully = result and len(result) > 0 and (result[0] == SUCCESS or (len(result[0]) == 3 and result[0] not in try_again))
        #if not crawled_successfully:
        #    print("Recrawling %s" % result[0])
        return crawled_successfully

        # return result and len(result) > 0 and result[0]==SUCCESS

    def has_videos(self, website_url):
        self.c.execute('SELECT 1 FROM found_videos WHERE website_url=%s LIMIT 1', [website_url])
        return len(self.c.fetchall()) > 0

    def save_crawled(self, website_url, status=SUCCESS):
        # print("New Status %s" % status)
        self.c.execute('''INSERT INTO articles (website_url, status) VALUES (%s, %s) ON CONFLICT (website_url) DO UPDATE
                          SET status = excluded.status;''', (website_url, status))
        self.conn.commit()

    def save_mention_with_video(self, event_id, website_url):
        self.c.execute('INSERT INTO mentions (event_id, website_url) VALUES (%s, %s)', (event_id, website_url))
        self.conn.commit()

    def save_found_video_url(self, website_url, platform, video_url):
        self.c.execute('INSERT INTO found_videos (website_url, platform, video_url) VALUES (%s,%s,%s)',
                       (website_url, platform, video_url))
        self.conn.commit()

    def get_columns_where(self, table, columns, key, value):
        query = 'SELECT (%s) FROM %s WHERE %s=\'%s\'' % (','.join(columns), table, key, value)
        self.c.execute(query)
        return self.c.fetchone()[0]

    def disconnect(self):
        self.conn.close()


def dict_insert_string(table, _dict):
    columns = _dict.keys()
    values = [_dict[column] for column in columns]
    return 'insert into %s (%s) values %s' % (table, AsIs(','.join(columns)), tuple(values))

def dict_set_string(_dict):
    set_str = ""
    for key in _dict.keys():
        set_str += str(key) + "=" + str(_dict[key]) + ","
    return set_str[:-1]

def dict_mogrifying_string(_dict):
    set_str = ""
    for key in _dict.keys():
        set_str += str(key) + "=%(" + str(key) + ")s,"
    return set_str[:-1]