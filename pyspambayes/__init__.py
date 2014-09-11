#!/usr/bin/python
# implementation of http://en.wikipedia.org/wiki/Naive_Bayes_spam_filtering
import string
import math

from tokenstore import TokenStoreBase

class SpamBayes(object):
    def __init__(self,tokenizer_function=None,tokenstore=None,spam_bias=0.5):
        """
        :param tokenizer: a function which gets the full input text and splits it up into individual tokens
        :param tokenstore: the backend used for storing the tokens, should provide the same interface as TokenStoreBase
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
        """
        overwrite this to capture the verbose output
        :param message:
        :return:
        """
        print message

    def single_token_spam_probability(self,token):
        """Compute the probability that a message containing a given token is spam
        ( "spamicity of a word" )
        """
        pr_s = self.spam_bias # probability that any given message is spam
        pr_h = 1-pr_s # probability that any given message is ham

        spam_count = self.tokenstore.get_spam_count(token) # number of known spams containing this token
        ham_count = self.tokenstore.get_ham_count(token) # number of known hams containing this token

        # "Dealing with rare words"
        if spam_count + ham_count<self.token_minimum:
            pr_s_w=0.5
        else:
            pr_w_s = float(spam_count) / self.tokenstore.get_total_spam_count() #  the probability that the token appears in spam messages
            pr_w_h = float(ham_count) / self.tokenstore.get_total_ham_count() #   the probability that the token appears in ham messages

            divisor=( pr_w_s *  pr_s  + pr_w_h * pr_h )
            if divisor<self.calc_minimum:
                divisor=self.calc_minimum
            pr_s_w =  pr_w_s * pr_s / divisor

        if self.verbose:
                self.info("Token '%s' : seen in %s spams, %s hams => spamicity= %.4f"%(token,spam_count,ham_count,pr_s_w))

        return pr_s_w

    def spam_probability(self,text):
        """
        :param text:
        :return: the probability that the given text is spam. float value between 0.0 and 1.0
        """
        tokens=self.tokenizer_function(text)
        if self.verbose:
            self.info("Got %s tokens"%len(tokens))
        total=0
        for t in tokens:
            spamicity = self.single_token_spam_probability(t)
            if spamicity<self.calc_minimum:
                spamicity=self.calc_minimum


            #make sure we get at least a very small amount
            x=1-spamicity
            if x<self.calc_minimum:
                x=self.calc_minimum


            n = math.log(x) - math.log(spamicity)
            total+=n
            #if self.verbose:
            #    self.info("n=%.4f"%n)
            #    self.info("total is now %.4f"%total)

        probability=1.0/(1+math.pow(math.e,total))
        return round(probability,4)

    def learn_ham(self,text):
        """
        learn the input text as ham
        :param text:
        :return:
        """
        self.tokenstore.learn_ham(self.tokenizer_function(text))

    def learn_spam(self,text):
        """
        learn the input text as spam
        :param text:
        :return:
        """
        self.tokenstore.learn_spam(self.tokenizer_function(text))

if __name__=='__main__':
    ba=SpamBayes()

    import random
    for _ in range(10):
        text=" ".join([str(random.randint(10,30)) for x in range(10)])
        ba.learn_ham(text)
        print "learned text as ham: ",text
    for _ in range(10):
        text=" ".join([str(random.randint(20,40)) for x in range(10)])
        ba.learn_spam(text)
        print "learned text as spam: ",text
    print ""
    test="21 25 29"
    print "calculating probabilitiy of text '%s' "%test
    print "Spam probability: %s%%"%(ba.spam_probability(test)*100)





