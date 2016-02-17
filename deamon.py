from pickle import loads, dumps
from rufous import Broker
from example import add

db = Broker()
def deamon():
    """
    Deamon to run task
    """
    while 1:
        key = None
        print "data"
        try:
            func, key, args, kwargs = loads(db.pull())
            result = func(*args, **kwargs)
            db.done(key, dumps(result))
            print result
        except Exception, e:
            result = e
            print str(e)
            db.failed(key, dumps(result))



if __name__ == "__main__":
    deamon()