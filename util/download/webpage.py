from multiprocessing.pool import Pool

pool = Pool(10)

def download_and_save(id, url):
    """
    Queues an image for download if it does not exist
    :param id: Name of the file
    :param url: URL of the image
    :return:
    """

    def fetch_url(row):
        index, article = row
        global count, data_count
        count += 1
        print(count / data_count)
        try:
            doc = urllib.request.urlopen(article.DocumentIdentifier).read()
            bs_doc = BeautifulSoup(doc)

            # remove some tags that aren't rendered, including their content
            # From https://www.w3schools.com/tags/ref_byfunc.asp
            programming_tags = ['script', 'noscript', 'applet', 'embed', 'object', 'param']
            meta_tags = ['head', 'meta', 'base', 'basefont']
            other_tags = ['data', 'style']
            [x.extract() for x in bs_doc.findAll(programming_tags + meta_tags + other_tags)]

            # Keep only the remaining text (removing all tags etc.)
            text = bs_doc.get_text()  # re.sub('<[^<]+?>', '', str(doc))[:100]

            # Tokenize the text
            tokens = nltk.word_tokenize(text)

            # Keep only tokens that are words and more than a letter
            alpha_tokens = [token for token in tokens if token.isalpha() and len(token) > 1]

            # Keep only tokens that are either all caps or no caps or start with a capital letter
            pattern = re.compile("(^[A-Z]?[a-z]+$)|(^[A-Z]+$)")
            word_tokens = [token for token in alpha_tokens if pattern.match(token)]

            # Done preprocessing. Save tokens
            file = open("%s/%s" % (article_path, article.DATE), "wb+")
            pickle.dump(word_tokens, file)  # Date is unique(?) TODO find out

            # Download the corresponding image
            # (for the whole dataset, we'll have to classify and then discard, unless I get proper storage)
            urllib.request.urlretrieve(article.ImageURL, "%s/%s" % (image_path, article.DATE))

        except Exception as e:
            print(e, article.DocumentIdentifier)


    .map(fetch_url, df.iterrows())

    return