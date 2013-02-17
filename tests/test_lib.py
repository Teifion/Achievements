import unittest

try:
    from ...tests import test_lib
    DBTestClass = test_lib.DBTestClass
except Exception:
    class DBTestClass(unittest.TestCase):
        def get_app(self, auth):
            pass
