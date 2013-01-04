# -*- coding: utf-8 -*-
import nose
import BaseTestCase
from mock import Mock
import storageserverdummy as StorageServer


class Teststorageserverdummy(BaseTestCase.BaseTestCase):
    def test_cacheFunction_should_call_funct(self):
        temp_funct = Mock()
        temp_funct.return_value = "mock_return"
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.cacheFunction(temp_funct, "mock_args")
        print repr(temp_funct.call_args_list)
        temp_funct.assert_called_with('mock_args')
        assert(result == "mock_return")

    def test_set_data(self):
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.set("name", "data")
        assert(result == "")

    def test_get(self):
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.get("name")
        assert(result == "")

    def test_setMulti(self):
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.setMulti("name", "data")
        assert(result == "")

    def test_getMulti(self):
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.getMulti("name", "data")
        assert(result == "")

    def test_lock(self):
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.lock("name")
        assert(result == False)

    def test_sqlSet(self):
        cache = StorageServer.StorageServer("Mock", 1)
        result = cache.unlock("name")
        assert(result == False)

if __name__ == '__main__':
    nose.runmodule()
