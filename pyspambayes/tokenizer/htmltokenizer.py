STOPWORDS=u"""
DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"

var

it as the you a for
"""
import BeautifulSoup
import re

class HTMLTokenizer(object):
    def __init__(self,stopwords=None):
        self.stopwords= stopwords or [
           word.lower() for word in STOPWORDS.split()
        ]

    def tokenize(self,text):
        try:
            soup = BeautifulSoup.BeautifulSoup(text)
        except UnicodeEncodeError: #BeautifulSoup doesn't like unicode tag names
            soup = BeautifulSoup.BeautifulSoup(text.encode('ascii','ignore'))

        texts = soup.findAll(text=True)

        def visible(element):
            if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
                return False
            elif re.match('<!--.*-->', str(element)):
                return False
            return True

        visible_texts = filter(visible, texts)
        stripped=" ".join([t.strip() for t in visible_texts if t.strip()!=''])

        tokens=[]
        for token in stripped.split():
            #at least three characters
            if len(token)<3:
                continue

            if len(token)>20:
                token=token[:20]

            #remove ending punctuation
            if token[-1] in ".;,:?!":
                token=token[:-1]

            #stip stop words
            if token.lower() in self.stopwords:
                continue

            tokens.append(token)


        return tokens
