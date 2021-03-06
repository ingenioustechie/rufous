import logging
import redis
from pickle import loads, dumps
from uuid import uuid4

logging.basicConfig(
        filename="rufous.log",
        filemode='a',
        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)

log = logging.getLogger("rufous")


def rufous(func):
    broker = Broker()

    def delay(*args, **kwargs):
        key = str(uuid4())
        task = dumps((func, key, args, kwargs))
        broker.push(task)
        log.debug("pushed task id {0}".format(key))
        return key
    func.delay = delay
    return func


class Broker(object):
    """A Broker Database connection."""

    def __init__(self, namespace='queue', connection_url=None):
        # If no connection_url was provided, fallback to default
        self.connection_url = connection_url or "redis://127.0.0.1:6379/1"

        host, port, db = self.__keys(self.connection_url)

        # Connect to the Brokker.
        # redis://127.0.0.1:6379/1
        POOL = redis.ConnectionPool(host=host, port=port, db=db)
        self.db = redis.Redis(connection_pool=POOL)
        self.__key = '%s' % (namespace)
        self.__done_key = '%s:done' % (namespace)
        self.__waiting_key = '%s:wait' % (namespace)
        self.__failed_key = '%s:failed' % (namespace)

    def __keys(self, connection_url):

        try:
            host, portDb = "redis://127.0.0.1:6379/1".split("//")[1].split(":")
            port, db = portDb.split("/")
        except:
            raise ValueError('You must provide a connection_url.')

        return host, port, db

    def push(self, task):
        """ Push item into the Queue"""
        self.db.lpush(self.__key, task)

    def pull(self):
        """ Push item into the Queue"""
        task = self.db.brpoplpush(self.__key, self.__waiting_key)
        return task

    def done(self, key, result):
        """ Push item into the Done/Fail """
        self.db.hset(self.__done_key, key, result)
        # clear wait Queue
        self.__clearWaiting()
        log.debug("Done task id {0}".format(key))

    def failed(self, key, result):
        """ Push item into the Done/Fail """
        self.db.hset(self.__failed_key, key, result)
        # clear wait Queue
        self.__clearWaiting()

    def getResult(self, key):
        """ Get result by from Done/Fail """
        result = self.db.hget(self.__done_key, key)
        if result:
            return True, loads(result)

        result = self.db.hget(self.__waiting_key, key)
        if result:
            return False, loads(result)

        return None, None

    def __clearWaiting(self):
        """ Clears waiting tasks """
        task = self.db.lpop(self.__waiting_key)
        func, key, args, kwargs = loads(task)

        # check in done task
        item = self.db.hget(self.__done_key, key)
        if not item:
            # check in failed task
            item = self.db.hget(self.__failed_key, key)
            if not item:
                # If task is not in done/failed store it again
                self.db.rpush(self.__waiting_key, task)

    def queueSize(self):
        """Return the size of the queue."""
        return self.db.llen(self.key)

    def waitingSize(self):
        """Return the size of the queue."""
        return self.db.hlen(self.__waiting_key)
