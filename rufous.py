import redis
from docopt import docopt
from pickle import loads, dumps
from uuid import uuid4


def rufous(func):
    broker = Broker()
    def delay(*args, **kwargs):
        key = str(uuid4())
        task = dumps((func, key, args, kwargs))
        broker.push(task)
        return Worker(key)
    func.delay = delay
    return func


class Worker(object):
    def __init__(self, key):
        self.key = key
        self._result = None

    @property
    def result(self):
        print("Result got called")
        print self.key
        if self._r is None:
            r = redis.get(self.key)
            if r is not None:
                self._result = loads(r)
        return self._result


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
        self.__key = '%s' %(namespace)
        self.__done_key = '%s:done' %(namespace)
        self.__waiting_key = '%s:wait' %(namespace)
        self.__failed_key = '%s:failed' %(namespace)

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

    def failed(self, key, result):
        """ Push item into the Done/Fail """
        self.db.hset(self.__failed_key, key, result)

    def __clearWaiting(self):
        """ Clears waiting tasks """
        task = self.db.lpull(self.__waiting_key)
        func, key, args, kwargs = loads(task[1])

        # check in done task
        item = self.db.hget(self.__done_key, key)
        if not item:
            # check in failed task
            item = self.db.hget(self.__failed_key, key)
            if not item:
                # If task is not in done/failed store it again
                self.db.rpush(self.__waiting_key, task)

    def size(self):
        """Return the size of the queue."""
        return self.db.llen(self.key)

    def waitingSize(self):
        """Return the size of the queue."""
        return self.db.hlen(self.__waiting_key)


def cli():
    doc="""Rofous: Simple Messaging"
    Usage:
      rufous.py <method> 
      rufous.py (-h | --help)
    Options:
      -h --help     Show this screen.
      --url=<url>   The Brokker URL to use. Defaults to $DATABASE_URL.
    Notes:
      - You may specify a Brokker connection string with --url, by default
      	It will connect to the localhost with 6379 port.
    """
    # Parse the command-line arguments.
    # arguments = docopt(doc)

    # Create the Database.
    db = Broker("test")

    

    # method = arguments['<method>']
    # params = arguments['<params>']

    # # Can't send an empty list if params aren't expected.
    # try:
    #     params = dict([i.split('=') for i in params])
    # except ValueError:
    #     print('Parameters must be given in key=value format.')
    #     exit(64)

# Run the CLI when executed directly.
# if __name__ == '__main__':
#     cli()


@rufous
def add(a, b):
    return a+b

add.delay(1, 4)