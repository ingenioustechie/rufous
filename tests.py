import unittest
from rufous import Broker
from example import add


class TestRufous(unittest.TestCase):

    def test_push(self):
        """ Test push """
        key = add.delay(3, 4)
        result, value = Broker().getResult(key)

        self.assertTrue(result)
        self.assertEqual(value, 7)

    def test_queueSize_count(self):
        pass

    def test_waiting_count(self):
        pass

    def test_pull(self):
        pass

    def test_done_count(self):
        pass

    def test_failed(self):
        pass

if __name__ == '__main__':
    unittest.main()
