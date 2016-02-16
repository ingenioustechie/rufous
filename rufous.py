import redis
from docopt import docopt
from json import loads

def roufos(func):
    def delay(*args, **kwargs):
        key = str(uuid4())
        task = dumps((func, key, args, kwargs))
        broker.push(task, key)
        return Worker(key)
    func.delay = delay
    return func


class Worker(object):
    def __init__(self, key):
        self.key = key
        self._result = None

    @property
    def result(self):
        if self._r is None:
            r = redis.get(self.key)
            if r is not None:
                self._result = loads(r)
        return self._result


class Broker(object):
    """A Broker Database connection."""

    def __init__(self, name, namespace='queue', connection_url=None):
        # If no connection_url was provided, fallback to default
        self.connection_url = connection_url or "redis://127.0.0.1:6379/1"

        host, port, db = self.__keys(self.connection_url)

        # Connect to the Brokker.
        # redis://127.0.0.1:6379/1
        POOL = redis.ConnectionPool(host=host, port=port, db=db)
        self.db = redis.Redis(connection_pool=POOL)
        self.__key = '%s:%s' %(namespace, name)
        self.__done = '%s:%s:done' %(namespace, name)
        self.__waiting_key = '%s:%s:wait' %(namespace, name)
        self.__fail_key = '%s:%s:fail' %(namespace, name)

    def __keys(self, connection_url):

        try:
            host, portDb = "redis://127.0.0.1:6379/1".split("//")[1].split(":")
            port, db = portDb.split("/")
        except:
            raise ValueError('You must provide a connection_url.')

        return host, port, db

    def push(self, task, key):
        """ Push item into the Queue"""
        self.db.rpush(self.__key, task)

    def pull(self, task):
        """ Push item into the Queue"""
        item = self.db.rpoplpush(self.__key, self.__waiting_key)
        return item

    def done(self, task, result):
        """ Push item into the Queue"""
        self.db.rpush(self.__done, task)


    def size(self):
        """Return the size of the queue."""
        return self.db.llen(self.key)


def cli():
    doc="""Rofous: Simple Messaging"
    Usage:
      roufos.py <method> 
      roufos.py (-h | --help)
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
if __name__ == '__main__':
    cli()
