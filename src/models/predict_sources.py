"""
Takes all found videos and filters for those that pass the classifier as "relevant"
The classifier is trained in the Source Exploration and Classification Notebook.
"""
import os
from urllib.parse import urlparse

import pandas as pd
import pickle
import psycopg2
from src import util

def run():
    platform = "youtube"  # Only doing this for youtube now
    clf_path = os.path.join(os.environ["MODEL_PATH"], "svmrbf_1549217180")
    trained_on = ["youtube_average", "youtube_distinct_to_sum"]
    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    # Create the new column
    # c.execute('ALTER TABLE sources ADD COLUMN IF NOT EXISTS %s_relevant BOOL' % platform)
    # Create indices if they do not exist to speed things up a little
    c.execute('''CREATE INDEX IF NOT EXISTS articles_source_name_index ON public.articles (source_name);''')
    conn.commit()

    # Compute the features the same way as in the modeling doc
    hosts = pd.read_sql_query('SELECT * FROM sources WHERE %s_count > 0' % platform, con=conn)
    hosts = hosts[["source_name",
                   "article_count",
                   "%s_sum" % platform,
                   "%s_sum_distinct" % platform,
                   "%s_count" % platform,
                   "%s_std_dev" % platform,
                   "%s_relevant" % platform]]
    hosts["%s_average" % platform] = \
        hosts["%s_sum" % platform] / hosts["article_count"]
    hosts["%s_average_distinct" % platform] = \
        hosts["%s_sum_distinct" % platform] / hosts["article_count"]
    hosts["%s_distinct_to_sum" % platform] = \
        hosts["%s_sum_distinct" % platform] / hosts["%s_sum" % platform]
    hosts["%s_percentage" % platform] = \
        hosts["%s_count" % platform] / hosts["article_count"]

    print(len(hosts))

    # Load the classifier
    clf = pickle.load(open(clf_path, "rb"))
    prediction = clf.predict(hosts[trained_on])
    classifications = {True: 0, False: 0}
    for index, row in hosts.iterrows():
        # print(platform, prediction[index], row["hostname"])
        # Website url may not be unique depending on the table, but it doesn't matter in this case
        classifications[prediction[index]] += 1
        c.execute('UPDATE sources SET %s_relevant=%s WHERE source_name=\'%s\''
                  % (platform, prediction[index], row["source_name"]))
        conn.commit()
    print(classifications)

if __name__ == "__main__":
    run()

