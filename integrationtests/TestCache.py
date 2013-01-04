import BaseTestCase
import nose
import sys
import os
import time
from mock import patch


class TestCacheCore(BaseTestCase.BaseTestCase):
    import StorageServer

    def setUp(self):
        time.sleep(4)
        if os.path.exists("./tmp/commoncache.db"):
            print "DELETING db"
            os.remove("./tmp/commoncache.db")
        #if os.path.exists("./tmp/commoncache.socket"):
        #    print "DELETING socket"
        #    os.remove("./tmp/commoncache.socket")

        super(self.__class__, self).setUp()
        reload(self.StorageServer)
        time.sleep(1)

    def assert_log(self, search):
        log_calls = sys.modules["__main__"].xbmc.log.call_args_list
        match = False
        for call in log_calls:
            call = call[0][0]
            print "searching for %s in %s" % (search, call)
            if call == search:
                match = True

        assert(match)

    def test_cache_should_calculate_hash(self):
        cache = self.StorageServer.StorageServer("integrationtest")

        def test(*args, **kwargs):
            return ("mock", 200 )
        result = cache.cacheFunction(test, {"some": "arguments"}, ["string", "list"])
        time.sleep(1)

        self.assert_log("[" + sys.modules["__main__"].plugin + "] 'get' : 'cachetest|7bb05d21dfcdad71b8b123b7baf47827|'")
        assert(result == ("mock", 200 ) )

    def test_cache_should_save_cache(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.cacheDelete("TestCacheCore.pi_count|d41d8cd98f00b204e9800998ecf8427e|")

        result = cache.cacheFunction(self.pi_count)

        time.sleep(1)
        print repr(result)
        self.assert_log("[" + sys.modules["__main__"].plugin + "] '_setCache' : 'Saving cache: TestCacheCore.pi_count|d41d8cd98f00b204e9800998ecf8427e|[31415926535897932384626433832795028841971L]'")

    def test_cache_should_return_cache(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.cacheDelete("TestCacheCore.pi_count|d41d8cd98f00b204e9800998ecf8427e|")
        cache.cacheFunction(self.pi_count)

        result = cache.cacheFunction(self.pi_count)
        time.sleep(1)
        print repr(result)
        self.assert_log("[" + sys.modules["__main__"].plugin + "] '_getCache' : 'Done, found cache : TestCacheCore.pi_count|d41d8cd98f00b204e9800998ecf8427e|'")

    def test_lock_should_lock(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.unlock("test")

        result = cache.lock("test")
        time.sleep(1)
        cache.unlock("test")

        print repr(result)
        assert(result)

    def test_lock_should_not_lock(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.unlock("test")
        cache.lock("test")

        result = cache.lock("test")
        time.sleep(1)
        cache.unlock("test")

        print repr(result)
        assert(not result)

    def test_unlock_should_unlock(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.unlock("test")
        cache.lock("test")

        result = cache.unlock("test")
        time.sleep(1)

        print repr(result)
        assert(result)

    def test_sqlSet_should_update(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.set("test", "mock-updated")
        cache.set("test", "mock-updated")
        cache.set("test", "mock-updated")

        time.sleep(1)

        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSet' : 'Update : mock-updated'")

    def test_sqlDel_should_remove_with_wildcards(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        cache.set("deltest1", "mock-updated")
        cache.set("deltest2", "mock-updated")
        cache.set("deltest3", "mock-updated")

        result_pre = cache.getMulti("deltest", ["1", "2", "3"])
        cache.delete("deltest%")
        result_post = cache.getMulti("deltest", ["1", "2", "3"])

        time.sleep(1)
        print repr(result_pre)
        print repr(result_post)
        assert(result_pre == ["mock-updated", "mock-updated", "mock-updated"])
        assert(result_post == ["", "", ""])

    def test_sqlSetMulti_should_set_multi(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        save_data = {"mock1": "val1", "mock2": "val2", "mock3": "val3"}

        cache.setMulti("itest", save_data)
        time.sleep(1)

        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSetMulti' : 'Insert : itestmock3'")
        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSetMulti' : 'Insert : itestmock2'")
        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSetMulti' : 'Insert : itestmock1'")

    def test_sqlSetMulti_should_update_multi(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        save_data = {"mock1": "val1", "mock2": "val2", "mock3": "val3"}

        cache.setMulti("utest", save_data)
        cache.setMulti("utest", save_data)
        time.sleep(1)

        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSetMulti' : 'Update : utestmock3'")
        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSetMulti' : 'Update : utestmock2'")
        self.assert_log("[StorageServer-" + sys.modules["__main__"].version + "] '_sqlSetMulti' : 'Update : utestmock1'")

    def test_sqlGetMulti(self):
        cache = self.StorageServer.StorageServer("integrationtest")
        save_data = {"mock1": "val1", "mock2": "val2", "mock3": "val3"}
        cache.setMulti("test", save_data)
        result = cache.getMulti("test", ["mock1", "mock2", "mock3"])
        time.sleep(1)

        print repr(result)
        assert(result == ["val1", "val2", "val3"] )

    def pi_count(self):
        def arccot(x, unity):
            sum = xpower = unity // x
            n = 3
            sign = -1
            while 1:
                xpower = xpower // (x * x)
                term = xpower // n
                if not term:
                    break
                sum += sign * term
                sign = -sign
                n += 2
            return sum

        digits = 40
        unity = 10 ** (digits + 10)
        pi = 4 * (4 * arccot(5, unity) - arccot(239, unity))
        return [pi // 10 ** 10]

if __name__ == "__main__":
    nose.runmodule()
