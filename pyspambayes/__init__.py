#!/usr/bin/python
# implementation of http://en.wikipedia.org/wiki/Naive_Bayes_spam_filtering
import string
import math

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
        for t in tokens:
            self.ham_tokens.append(t)
        self.ham_count+=1

    def learn_spam(self,tokens):
        for t in tokens:
            self.spam_tokens.append(t)
        self.spam_count+=1

class SpamBayes(object):
    def __init__(self,tokenizer_function=None,tokenstore=None,spam_bias=0.5):
        """
        :param tokenizer:
        :param tokenstore:
        :param spam_bias: the overall probability, that any given message is spam. use 0.5 for "no assumption", use 0.8 for "80% of my messages are usually spam"
        :return:
        """
        self.spam_bias=spam_bias
        self.tokenizer_function=tokenizer_function or string.split
        self.tokenstore=tokenstore or TokenStoreBase()
        self.verbose=True

        self.calc_minimum=0.00000001 # work around division by zero etc
        self.token_minimum=3 # don't make any assumptions about token seen less than this amount

    def info(self,message):
        print message

    def single_token_spam_probability(self,token):
        """Compute the probability that a message containing a given word is spam
        ( "spamicity of a word" )
        """
        pr_s = self.spam_bias # probability that any given message is spam
        pr_h = 1-pr_s # probability that any given message is spam

        spam_count = self.tokenstore.get_spam_count(token)
        ham_count = self.tokenstore.get_ham_count(token)

        "Dealing with rare words"
        if spam_count + ham_count<self.token_minimum:
            return 0.5

        pr_w_s = float(spam_count) / self.tokenstore.get_total_spam_count() #  the probability that the token appears in spam messages
        pr_w_h = float(ham_count) / self.tokenstore.get_total_ham_count() #   the probability that the token appears in ham messages

        divisor=( pr_w_s *  pr_s  + pr_w_h * pr_h )
        if divisor<self.calc_minimum:
            divisor=self.calc_minimum
        pr_s_w =  pr_w_s * pr_s / divisor
        return pr_s_w

    def spam_probability(self,text):
        tokens=self.tokenizer_function(text)
        if self.verbose:
            self.info("Got %s tokens"%len(tokens))
        total=0
        for t in tokens:
            spamicity = self.single_token_spam_probability(t)
            if spamicity<self.calc_minimum:
                spamicity=self.calc_minimum
            if self.verbose:
                self.info("Spamicity of token '%s' is : %.4f"%(t,spamicity))

            #make sure we get at least a very small amount
            x=1-spamicity
            if x<self.calc_minimum:
                x=self.calc_minimum


            n = math.log(x) - math.log(spamicity)
            total+=n
            if self.verbose:
                self.info("n=%.4f"%n)
                self.info("total is now %.4f"%total)

        probability=1.0/(1+math.pow(math.e,total))
        return round(probability,4)

    def learn_ham(self,text):
        self.tokenstore.learn_ham(self.tokenizer_function(text))

    def learn_spam(self,text):
        self.tokenstore.learn_spam(self.tokenizer_function(text))

if __name__=='__main__':
    ba=SpamBayes()

    import random
    #test = spam
    for _ in range(10):
        text=" ".join([str(random.randint(10,30)) for x in range(10)])
        ba.learn_ham(text)
        print "learned text as ham: ",text
    for _ in range(10):
        text=" ".join([str(random.randint(20,40)) for x in range(10)])
        ba.learn_spam(text)
        print "learned text as spam: ",text

    test="21 25 29"
    print "Spam probabilitiy: of text  ",test
    print ba.spam_probability(test)




