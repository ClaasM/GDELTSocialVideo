"""
Takes all found videos and filters for those that pass the classifier as "relevant"
TODO and some more other filtering
TODO write documentation
"""
import os
from urllib.parse import urlparse

import pandas as pd
import pickle
import psycopg2
from src import util

if __name__ == "__main__":

    platform = "youtube"  # Only doing this for youtube now
    clf_path = os.environ["MODEL_PATH"] + "svmrbf_1536694057"
    trained_on = ["youtube_video_std_dev", "youtube_video_distinct_to_sum"]

    conn = psycopg2.connect(database="gdelt_social_video", user="postgres")
    c = conn.cursor()
    # Create the new column
    c.execute('ALTER TABLE hosts ADD COLUMN IF NOT EXISTS %s_relevant BOOL' % platform)
    # Create indices if they do not exist to speed things up a little
    c.execute('''CREATE INDEX IF NOT EXISTS articles_hostname_index ON public.articles (hostname);''')
    conn.commit()

    # Compute the features the same way as in the modeling doc
    # TODO make it DRY!
    hosts = pd.read_sql_query('SELECT * FROM hosts WHERE %s_video_count > 0' % platform, con=conn)
    hosts = hosts[["hostname",
                   "article_count",
                   "%s_video_sum" % platform,
                   "%s_video_sum_distinct" % platform,
                   "%s_video_count" % platform,
                   "%s_video_std_dev" % platform,
                   "%s_relevant" % platform]]
    hosts["%s_video_average" % platform] = \
        hosts["%s_video_sum" % platform] / hosts["article_count"]
    hosts["%s_video_average_distinct" % platform] = \
        hosts["%s_video_sum_distinct" % platform] / hosts["article_count"]
    hosts["%s_video_distinct_to_sum" % platform] = \
        hosts["%s_video_sum_distinct" % platform] / hosts["%s_video_sum" % platform]
    hosts["%s_video_percentage" % platform] = \
        hosts["%s_video_count" % platform] / hosts["article_count"]

    print(len(hosts))

    # Load the classifier
    clf = pickle.load(open(clf_path,"rb"))
    prediction = clf.predict(hosts[trained_on])
    classifications = {True:0, False:0}
    for index, row in hosts.iterrows():
        # print(platform, prediction[index], row["hostname"])
        # Website url may not be unique depending on the table, but it doesn't matter in this case
        classifications[prediction[index]]+=1
        c.execute('UPDATE hosts SET %s_relevant=%s WHERE hostname=\'%s\''
                  % (platform, prediction[index], row["hostname"]))
        conn.commit()
    print(classifications)