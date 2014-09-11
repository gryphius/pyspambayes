__author__ = 'gryphius'

class TokenStoreBase(object):
    """
    Simple memory based tokenstore
    The real implementation should overwrite all methods
    """
    def __init__(self):
        self.ham_count=0
        self.spam_count=0

        self.ham_tokens=[]
        self.spam_tokens=[]


    def get_ham_count(self,token):
        """
        :param token: the token to check
        :return: the number of ham messages this token as found in
        """
        return self.ham_tokens.count(token)

    def get_spam_count(self,token):
        """
        :param token: the token to check
        :return: the number of spam messages this token as found in
        """
        return self.spam_tokens.count(token)

    def get_total_ham_count(self):
        """get the number of known ham messages"""
        return self.ham_count

    def get_total_spam_count(self):
        """get the number of known spam messages"""
        return self.spam_count

    def learn_ham(self,tokens):
        for t in set(tokens):
            self.ham_tokens.append(t)
        self.ham_count+=1

    def learn_spam(self,tokens):
        for t in set(tokens):
            self.spam_tokens.append(t)
        self.spam_count+=1