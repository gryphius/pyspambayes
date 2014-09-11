from . import TokenStoreBase
from hashlib import sha1
from redis import StrictRedis
import time

class RedisTokenStore(TokenStoreBase):

    def __init__(self,redis=None):
        self.redis=redis or StrictRedis()
        self.token_prefix='bayes_token_'
        self.total_key='bayes_total'
        self.seen_prefix='bayes_seen_'
        self.expiration=7*24*3600 # one week
        self.recalc_totals_interval=24*3600 # once per day
        self.labels=['spam','ham']

    def recalc_totals(self):
        """from time to time we need to reduce the totals from expired messages"""
        for label in self.labels:
            kset=set()
            pattern=self.seen_prefix+label+'*'
            start,values=self.redis.scan(0,match=pattern)
            while True:
                start,values=self.redis.scan(start,match=pattern)
                for v in values:
                    kset.add(v)
                if start=='0':
                    break

            oldval=self.redis.hget(self.total_key,label)
            newval=len(kset)
            self.redis.hset(self.total_key,label,newval)
            #print "%s changed from %s to %s"%(label,oldval,newval)

    def get_(self,token,what):
        assert what in self.labels
        keyname=self.token_prefix+token
        return self.redis.hget(keyname,what) or 0

    def get_ham_count(self,token):
        return self.get_(token,'ham')

    def get_spam_count(self,token):
        return self.get_(token,'spam')

    def get_total_ham_count(self):
        """get the number of known ham messages"""
        return self.redis.hget(self.total_key,'ham') or 0

    def get_total_spam_count(self):
        """get the number of known spam messages"""
        return self.redis.hget(self.total_key,'spam') or 0

    def learn_(self,tokens,aswhat):
        assert aswhat in self.labels
        digest=sha1()
        pipeline=self.redis.pipeline()
        for t in set(tokens):
            keyname=self.token_prefix+t
            curcount=pipeline.hincrby(keyname,aswhat,1)
            if curcount==1: #only expire on first insert to make sure
                pipeline.expire(keyname,self.expiration)
            digest.update(t.encode('utf-8','ignore'))
        pipeline.hincrby(self.total_key,aswhat,1)
        pipeline.set(self.seen_prefix+aswhat+'_'+digest.hexdigest(),1)
        pipeline.execute()

        last_recalc=self.redis.hget(self.total_key,'last_recalc')
        if last_recalc==None:
            last_recalc=0
        last_recalc=int(last_recalc)
        if not last_recalc or time.time()-last_recalc>self.recalc_totals_interval:
            self.redis.hset(self.total_key,'last_recalc',int(time.time()))
            self.recalc_totals()


    def learn_ham(self,tokens):
        self.learn_(tokens,'ham')

    def learn_spam(self,tokens):
        self.lean_(tokens,'spam')