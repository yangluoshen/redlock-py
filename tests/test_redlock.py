# coding: utf-8

import sys
sys.path.append('.')
import unittest

from redlock import Redlock, MultipleRedlockException


class TestRedlock(unittest.TestCase):

    def setUp(self):
        try:
            self.redlock = Redlock([{"host": "localhost"}])
            self.dstlock = Redlock([{"host": "localhost", "port": 6379, "socket_timeout": 0.5},
                                    {"host": "localhost", "port": 6380, "socket_timeout": 0.5},
                                    {"host": "localhost", "port": 6381, "socket_timeout": 0.5}])
        except Exception as e:
            pass

    '''
    def test_distribute_locks(self):

        import time
        while True:
            if not self.dstlock.lock("fizz", 1000):
                print ("lock failed")
            else:
                print("lock success")

            time.sleep(1)
    '''

    def test_lock(self):
        lock = self.redlock.lock("pants", 100)
        self.assertEqual(lock.resource, "pants")
        self.redlock.unlock(lock)
        lock = self.redlock.lock("pants", 10)
        self.redlock.unlock(lock)

    def test_blocked(self):
        lock = self.redlock.lock("pants", 1000)
        bad = self.redlock.lock("pants", 10)
        self.assertFalse(bad)
        self.redlock.unlock(lock)

    def test_bad_connection_info(self):
        with self.assertRaises(Warning):
            Redlock([{"cat": "hog"}])

    def test_py3_compatible_encoding(self):
        lock = self.redlock.lock("pants", 1000)
        key = self.redlock.servers[0].get("pants")
        self.assertEqual(lock.key, key)

    def test_ttl_not_int_trigger_exception_value_error(self):
        with self.assertRaises(ValueError):
            self.redlock.lock("pants", 1000.0)

    def test_multiple_redlock_exception(self):
        ex1 = Exception("Redis connection error")
        ex2 = Exception("Redis command timed out")
        exc = MultipleRedlockException([ex1, ex2])
        exc_str = str(exc)
        self.assertIn('connection error', exc_str)
        self.assertIn('command timed out', exc_str)

if __name__ == '__main__':
    unittest.main()
