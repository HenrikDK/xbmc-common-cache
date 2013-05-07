import nose
import BaseTestCase
from mock import Mock, patch
import sys

#Setup socket
sys.modules["socket"] = __import__("mock")
sys.modules["socket"].socket = Mock()
sys.modules["socket"].error = {"text": "socket_error", "errno": 11 }
sys.modules["socket"].socket.gethostname.return_value = "hostname"
sys.modules["socket"].AF_INET = "INET"
sys.modules["socket"].AF_UNIX = "UNIX"
sys.modules["socket"].SOCK_STREAM = "STREAM"

import StorageServer


class TestStorageServer(BaseTestCase.BaseTestCase):
    def test_startDB_should_use_sql2(self):
        storage = StorageServer.StorageServer()
        storage.modules = {"sqlite": True }

        dummy_socket = Mock()
        sys.modules["sqlite"].connect.return_value = dummy_socket

        ret = storage._startDB()
        print repr(ret)
        sys.modules["sqlite"].connect.assert_called_with('testing/commoncache.db')
        assert(ret == True)

    def test_startDB_should_use_sql3(self):
        storage = StorageServer.StorageServer()
        storage.modules = {"sqlite3": True }
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log

        dummy_socket = Mock()
        sys.modules["sqlite3"].connect.return_value = dummy_socket

        ret = storage._startDB()
        print repr(ret)
        sys.modules["sqlite3"].connect.assert_called_with('testing/commoncache.db', check_same_thread=False)
        assert(ret == True)

    def test_startDB_should_fail_on_no_sql_supported(self):
        storage = StorageServer.StorageServer()
        storage.modules = ""
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log

        ret = storage._startDB()
        print repr(ret)
        assert(ret == False)

    def test_aborting_should_call_xbmc_abortRequested(self):
        sys.modules["__main__"].xbmc.abortRequested = "Mock"
        storage = StorageServer.StorageServer()
        storage.instance = False
        storage.die = False
        ret = storage._aborting()
        assert(ret == "Mock")

    def test_aborting_should_die_when_set_in_instance_mode(self):
        storage = StorageServer.StorageServer()
        storage.instance = True
        storage.die = True
        ret = storage._aborting()
        assert(ret == True)

    def test__sock_init_should_set_socket_for_win32(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.return_value = "59994"
        storage.platform = "win32"

        storage._sock_init()

        print repr(storage.socket)
        assert(storage.socket == ('127.0.0.1', 59994))

    def test__sock_init_should_set_socket_for_posix(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.platform = "posix"
        storage.xbmcvfs = Mock()
        storage.xbmcvfs.exists.return_value = True

        storage._sock_init(check_stale=True)

        assert(storage.socket == "testing/commoncache.socket")
        storage.xbmcvfs.delete.assert_called_with("testing/commoncache.socket")

    def test_recieveData_should_get_and_eval_and_return_data(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._recv = Mock()
        storage._recv.return_value = "'mock_data'"

        result = storage._recieveData()

        print repr(result)
        storage._recv.assert_called_with(False)
        assert(result == "mock_data")

    def test_runCommand_should_call_sqlGet(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = "mock_result"

        storage._runCommand({"action": "get", "table": "mock_table", "name": "mock_name"})
        storage._sqlGet.assert_called_with('mock_table', 'mock_name')
        storage._send.assert_called_with(False, "'mock_result'")

    def test_runCommand_should_call_sqlGetMulti(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._sqlGetMulti = Mock()
        storage._sqlGetMulti.return_value = "mock_result"

        storage._runCommand({"action": "get_multi", "table": "mock_table", "name": "mock_name", "items": "mock_items"})
        storage._sqlGetMulti.assert_called_with('mock_table', 'mock_name', 'mock_items')
        storage._send.assert_called_with(False, "'mock_result'")

    def test_runCommand_should_call_sqlSetMulti(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._sqlSetMulti = Mock()
        storage._sqlSetMulti.return_value = "mock_result"

        storage._runCommand({"action": "set_multi", "table": "mock_table", "name": "mock_name", "data": "data"})
        storage._sqlSetMulti.assert_called_with('mock_table', 'mock_name', 'data')
        storage._send.assert_called_with(False, "'mock_result'")

    def test_runCommand_should_call_sqlSet(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._sqlSet = Mock()
        storage._sqlSet.return_value = "mock_result"

        storage._runCommand({"action": "set", "table": "mock_table", "name": "mock_name", "data": "data"})
        storage._sqlSet.assert_called_with('mock_table', 'mock_name', "data")
        storage._send.assert_called_with(False, "'mock_result'")

    def test_runCommand_should_call_sqlDel(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._sqlDel = Mock()
        storage._sqlDel.return_value = "mock_result"

        storage._runCommand({"action": "del", "table": "mock_table", "name": "mock_name"})
        storage._sqlDel.assert_called_with('mock_table', 'mock_name')
        storage._send.assert_called_with(False, "'mock_result'")

    def test_runCommand_should_call_lock(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._lock = Mock()
        storage._lock.return_value = "mock_result"

        storage._runCommand({"action": "lock", "table": "mock_table", "name": "mock_name"})
        storage._lock.assert_called_with('mock_table', 'mock_name')
        storage._send.assert_called_with(False, "'mock_result'")

    def test_runCommand_should_call_unlock(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._send = Mock()
        storage._unlock = Mock()
        storage._unlock.return_value = "mock_result"

        storage._runCommand({"action": "unlock", "table": "mock_table", "name": "mock_name", "items": "mock_items"})
        storage._unlock.assert_called_with('mock_table', 'mock_name')
        storage._send.assert_called_with(False, "'mock_result'")

    def test_run_should_init_for_win32(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.platform = "win32"

        storage.conn = Mock()
        storage.xbmc = Mock()
        storage._recieveData = Mock()
        storage._runCommand = Mock()
        storage._aborting = Mock()
        storage._aborting.return_value = True

        dummy_socket = Mock()
        dummy_socket.accept.return_value = ("bla", "127.0.0.1" )
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.return_value = "59994"
        sys.modules["socket"].socket.return_value = dummy_socket

        storage._startDB = Mock()

        storage.run()

        storage._startDB.assert_called_with()
        dummy_socket.bind.assert_called_with(('127.0.0.1', 59994))
        dummy_socket.listen.assert_called_with(1)
        dummy_socket.setblocking.assert_called_with(0)

    def test_run_should_init_and_unlink_stale_file_for_posix(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.platform = "linux2"

        storage.conn = Mock()
        storage._aborting = Mock()
        storage._aborting.return_value = True
        storage.xbmcvfs = Mock()
        storage.xbmcvfs.exists.return_value = True
        storage._recieveData = Mock()
        storage._runCommand = Mock()

        dummy_socket = Mock()
        dummy_socket.accept.return_value = ("bla", "127.0.0.1" )
        sys.modules["socket"].socket.return_value = dummy_socket

        storage._startDB = Mock()

        sock = Mock()
        recv_list = ["then receive this string\r\n", "first this. "]
        sock.recv.side_effect = lambda x: recv_list.pop()

        storage.run()
        storage._startDB.assert_called_with()
        dummy_socket.bind.assert_called_with('testing/commoncache.socket')
        dummy_socket.listen.assert_called_with(1)
        dummy_socket.setblocking.assert_called_with(0)
        storage.xbmcvfs.delete.assert_called_with('testing/commoncache.socket')

    def test_run_should_loop_when_recieving_no_data(self):
        patcher = patch("socket.error")
        patcher.start()
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.platform = "win32"
        storage._recieveData = Mock()
        storage._runCommand = Mock()

        storage._aborting = Mock()
        abortrequests = [True, False]
        storage._aborting.side_effect = lambda: abortrequests.pop()
        storage.conn = Mock()

        dummy_socket = Mock()
        import socket
        print repr(socket.error)

        dummy_socket.accept.return_value = {'text': 'socket_error', 'errno': 11}
        dummy_socket.accept.side_effect = socket.error
        sys.modules["socket"].socket.return_value = dummy_socket
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.return_value = "59994"
        storage.soccon = Mock()
        storage.platform = "win32"

        storage._startDB = Mock()

        storage.run()
        patcher.stop()

        dummy_socket.bind.assert_called_with(('127.0.0.1', 59994))
        dummy_socket.listen.assert_called_with(1)
        dummy_socket.setblocking.assert_called_with(0)

    def test_run_should_get_data_and_run_command(self):
        patcher = patch("socket.error")
        patcher.start()
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.platform = "win32"
        storage._recieveData = Mock()
        storage._recieveData.return_value = "mock_return"
        storage._runCommand = Mock()

        storage._aborting = Mock()
        abortrequests = [True, False]
        storage._aborting.side_effect = lambda: abortrequests.pop()
        storage.conn = Mock()

        dummy_socket = Mock()
        dummy_socket.bind = Mock()
        dummy_socket.listen = Mock()
        dummy_socket.setblocking = Mock()
        dummy_socket.accept = Mock()
        dummy_socket.accept.return_value = (True, "mock")
        sys.modules["socket"].socket.return_value = dummy_socket
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.return_value = "59994"

        storage.soccon = Mock()
        storage.platform = "win32"

        storage._startDB = Mock()

        storage.run()
        patcher.stop()

        storage._recieveData.assert_called_with()
        storage._runCommand.assert_called_with("mock_return")

    def ttest_run_win32_recieved_no_data_going_to_sleep(self):
        patcher = patch("socket.socket")
        patcher.start()

        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.platform = "win32"
        storage._aborting = Mock()
        storage._recieveData = Mock()
        storage._runCommand = Mock()

        storage._aborting.side_effect = [False, False, True]
        storage.conn = Mock()

        import socket
        tmp = socket.error
        tmp.errno = 12
        tmp.filename = "some"
        con = socket.socket()
        con.accept.side_effect = tmp
        dummy_socket = Mock()
        #patcher(socket.socket().accept()).side_effect = socket.error

        #dummy_socket.accept.return_value = socket.error({'text': 'socket_error', 'errno': 11})
        #dummy_socket.accept.side_effect = socket.error
        #sys.modules["socket"].socket.return_value = dummy_socket

        storage.soccon = Mock()
        storage.platform = "win32"

        storage._startDB = Mock()

        storage.run()
        patcher.stop()

        dummy_socket.bind.assert_called_with(('127.0.0.1', 59994))
        dummy_socket.listen.assert_called_with(1)
        dummy_socket.setblocking.assert_called_with(0)
        #assertRaises(socket.error, dummy_socket.accept)
        assert(False)

    def test__recv_should_recieve_and_assemble_socket_transfer(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._sqlExecute = Mock()
        storage.curs = [[repr(("cache", 200))]]
        sock = Mock()
        recv_list = ["then receive this string\r\n", "first this. "]
        sock.recv.side_effect = lambda x: recv_list.pop()
        ret = storage._recv(sock)
        print "D" + repr(sock.send.call_args_list)
        assert(sock.send.call_args_list[0][0][0] == ('ACK\r\n          ') )
        assert(sock.send.call_args_list[1][0][0] == ('COMPLETE\r\n     ') )

        print "E" + repr(sock.recv.call_args_list)
        assert(sock.recv.call_args_list[0][0][0] == (4096) )
        assert(sock.recv.call_args_list[1][0][0] == (4096) )

        print repr(ret)
        assert(ret == "first this. then receive this string")

    def test_send_should_split_message_in_chunks_and_transfer_chunks(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._sqlExecute = Mock()
        storage.curs = [[repr(("cache", 200))]]
        sock = Mock()
        sock.send.return_value = ""
        sock.recv.return_value = "COMPLETE\r\n"

        ret = storage._send(sock, ("X" * 4096 ) + "send this string")

        print repr(ret)
        print repr(sock.send.call_args_list)

        sock.send.assert_any_call("X" * 4096)
        sock.send.assert_any_call('send this string\r\n')
        sock.recv.assert_called_with(15)
        assert(ret == True)

    def ttest_send_over_time(self):  # Fix this
        import socket
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._sqlExecute = Mock()
        storage.curs = [[repr(("cache", 200))]]
        sock = Mock()
        sock.send.return_value = ""
        print repr(socket)
        print repr(socket.error)
        sock.recv.return_value = ""
        #sock.recv.side_effect = socket.error("string", 35)
        sock.recv.side_effect = {"text": "string", "errno": 35}

        ret = storage._send(sock, "send this string")
        print "D" + repr(sock.send.call_args_list)
        print "E" + repr(sock.recv.call_args_list)
        sock.send.assert_called_with('send this string\r\n')
        sock.recv.assert_called_with(15)
        print repr(ret)
        assert(ret == True)

    def test__lock_should_lock(self):
        patcher = patch("time.time")
        patcher.start()
        import time
        patcher(time.time).return_value = 3600 * 48

        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._sqlExecute = Mock()
        storage.conn = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = ""
        ret = storage._lock("Mock", "unique")
        patcher.stop()

        print repr(ret)

        storage._sqlExecute.assert_called_with('INSERT INTO Mock VALUES ( %s , %s )', ('unique', 3600 * 48) )
        storage.conn.commit.assert_called_with()
        assert(ret == "true")

    def test__lock_should_remove_stale_lock(self):
        patcher = patch("time.time")
        patcher.start()
        import time
        patcher(time.time).return_value = 3600 * 48

        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._sqlExecute = Mock()
        storage.conn = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = "0.0"
        ret = storage._lock("Mock", "exists")
        patcher.stop()

        print repr(ret)

        assert(storage._sqlExecute.call_args_list[0][0] == ('DELETE FROM Mock WHERE name = %s', ('exists',)) )
        assert(storage._sqlExecute.call_args_list[1][0] == ('INSERT INTO Mock VALUES ( %s , %s )', ('exists', 3600 * 48)) )
        storage.conn.commit.assert_called_with()
        assert(ret == "true")

    def test__lock_should_fail_when_already_locked(self):
        import time
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._sqlExecute = Mock()
        storage.conn = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = str(time.time() + time.time())
        ret = storage._lock("Mock", "exists")
        print repr(ret)
        assert(ret == "false")

    def test__unlock_should_unlock(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage.conn = Mock()
        ret = storage._unlock("Mock", "exists")
        storage._sqlExecute.assert_called_with('DELETE FROM Mock WHERE name = %s', ('exists',) )
        storage._checkTable.assert_called_with('Mock')
        storage.conn.commit.assert_called_with()

        print repr(ret)
        assert(ret == "true")

    def test__sqlDel_should_delete(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage.conn = Mock()
        ret = storage._sqlDel("Mock", "exists")
        storage._sqlExecute.assert_called_with('DELETE FROM Mock WHERE name LIKE %s', 'exists')
        storage._checkTable.assert_called_with('Mock')
        storage.conn.commit.assert_called_with()

        print repr(ret)
        assert(ret == "true")

    def test__sqlSetMulti_should_insert(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = ""
        storage.conn = Mock()
        ret = storage._sqlSetMulti("Mock", "exists", {"test0": "cache0", "test1": "cache1", "test2": "cache2" } )
        assert(storage._sqlExecute.call_args_list[0][0] == ('INSERT INTO Mock VALUES ( %s , %s )', ('existstest1', 'cache1')) )
        assert(storage._sqlExecute.call_args_list[1][0] == ('INSERT INTO Mock VALUES ( %s , %s )', ('existstest0', 'cache0')) )
        assert(storage._sqlExecute.call_args_list[2][0] == ('INSERT INTO Mock VALUES ( %s , %s )', ('existstest2', 'cache2')) )
        storage.conn.commit.assert_called_with()
        storage._checkTable.assert_called_with('Mock')

        print repr(ret)
        assert(ret == "")

    def test__sqlSetMulti_should_update_existing(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = "cache"
        storage.conn = Mock()
        ret = storage._sqlSetMulti("Mock", "exists", {"test0": "cache0", "test1": "cache1", "test2": "cache2" } )
        assert(storage._sqlExecute.call_args_list[0][0] == ('UPDATE Mock SET data = %s WHERE name = %s', ('cache1', 'existstest1')) )
        assert(storage._sqlExecute.call_args_list[1][0] == ('UPDATE Mock SET data = %s WHERE name = %s', ('cache0', 'existstest0')) )
        assert(storage._sqlExecute.call_args_list[2][0] == ('UPDATE Mock SET data = %s WHERE name = %s', ('cache2', 'existstest2')) )
        storage.conn.commit.assert_called_with()
        storage._checkTable.assert_called_with('Mock')

        print repr(ret)
        assert(ret == "")

    def test__sqlGetMulti_should_get_multiple_items(self):
        storage = StorageServer.StorageServer()
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.curs = [[repr(("cache", 200))]]
        ret = storage._sqlGetMulti("Mock", "exists", ["test0", "test1", "test2"])
        print repr(ret)
        assert(storage._sqlExecute.call_args_list[0][0] == ('SELECT data FROM Mock WHERE name = %s', 'existstest0') )
        assert(storage._sqlExecute.call_args_list[1][0] == ('SELECT data FROM Mock WHERE name = %s', 'existstest1') )
        assert(storage._sqlExecute.call_args_list[2][0] == ('SELECT data FROM Mock WHERE name = %s', 'existstest2') )
        storage._checkTable.assert_called_with('Mock')
        assert(ret == ["('cache', 200)", "('cache', 200)", "('cache', 200)"])

    def test__sqlSet_should_insert(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = ""
        storage.conn = Mock()
        ret = storage._sqlSet("Mock", "exists", "cache")
        storage._sqlExecute.assert_called_with('INSERT INTO Mock VALUES ( %s , %s )', ('exists', 'cache'))
        storage.conn.commit.assert_called_with()
        storage._checkTable.assert_called_with('Mock')

        print repr(ret)
        assert(ret == "")

    def test__sqlSet_should_update(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._checkTable = Mock()
        storage._sqlExecute = Mock()
        storage._sqlGet = Mock()
        storage._sqlGet.return_value = "cache"
        storage.conn = Mock()
        ret = storage._sqlSet("Mock", "exists", "cache")
        storage._sqlExecute.assert_called_with('UPDATE Mock SET data = %s WHERE name = %s', ('cache', 'exists'))
        storage.conn.commit.assert_called_with()
        storage._checkTable.assert_called_with('Mock')

        print repr(ret)
        assert(ret == "")

    def test__sqlGet_should_return_stored_data(self):
        storage = StorageServer.StorageServer()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.curs = [[repr(("cache", 200))]]
        storage._sqlExecute = Mock()
        ret = storage._sqlGet("Mock", "exists")
        print repr(ret)
        storage._sqlExecute.assert_called_with('SELECT data FROM Mock WHERE name = %s', 'exists')
        assert(ret == "('cache', 200)")

    def test__sqlGet_should_return_empty(self):
        storage = StorageServer.StorageServer()
        storage._sqlExecute = Mock()
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.curs = []
        ret = storage._sqlGet("Mock", "exists")
        print repr(ret)
        storage._sqlExecute.assert_called_with('SELECT data FROM Mock WHERE name = %s', 'exists')
        assert(ret == " ")

    def test__sqlExeceute_should_use_sql2(self):
        storage = StorageServer.StorageServer()
        storage.sql2 = True
        storage.sql3 = False
        storage.curs = Mock()
        storage._sqlExecute('SELECT data FROM Mock WHERE name = %s', ('exists', ))
        storage.curs.execute.assert_called_with('SELECT data FROM Mock WHERE name = %s', ('exists', ))

    def test__sqlExeceute_should_use_sql3(self):
        storage = StorageServer.StorageServer()
        storage.sql2 = False
        storage.sql3 = True
        storage.curs = Mock()
        storage._sqlExecute('SELECT data FROM Mock WHERE name = %s', 'exists')
        storage.curs.execute.assert_called_with('SELECT data FROM Mock WHERE name = ?', ('exists', ))

    def test__sqlExeceute_should_convert_to_tupple_for_sql3(self):
        storage = StorageServer.StorageServer()
        storage.sql2 = False
        storage.sql3 = True
        storage.curs = Mock()
        storage._sqlExecute('SELECT data FROM Mock WHERE name = %s', ('exists', ))
        storage.curs.execute.assert_called_with('SELECT data FROM Mock WHERE name = ?', ('exists', ))

    def test_checkTable_should_create_new_table(self):
        storage = StorageServer.StorageServer()
        storage.curs = Mock()
        storage.conn = Mock()
        storage._checkTable("Mock")
        storage.curs.execute.assert_called_with('create table Mock (name text unique, data text)')
        storage.conn.commit.assert_called_with()

    def test__evaluate_should_return_empty_string_on_failure(self):
        storage = StorageServer.StorageServer()
        ret = storage._evaluate("'true")
        assert(ret == "")

    def test__evaluate_should_return_evaled_object(self):
        storage = StorageServer.StorageServer()
        ret = storage._evaluate("'true'")
        assert(ret == "true")

    def test__generateKey_should_strip_method_of(self):
        storage = StorageServer.StorageServer()
        ret = storage._generateKey("<bound method mock_method of <some instance>>")
        print repr(ret)
        assert(ret == 'mock_method|d41d8cd98f00b204e9800998ecf8427e|')

    def test__generateKey_should_strip_function_at(self):
        storage = StorageServer.StorageServer()
        ret = storage._generateKey("<bound function mock_method at <some instance>>")
        print repr(ret)
        assert(ret == 'mock_method|d41d8cd98f00b204e9800998ecf8427e|')

### External Functions ###
    def test_cacheFunction_empty_result_from_sqlGet(self):
        patcher = patch("time.time")
        patcher.start()
        import time
        patcher(time.time).return_value = 3600 * 48
        storage = StorageServer.StorageServer("Mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.temp_cache = Mock()
        storage.temp_cache.return_value = ("called", 200)
        name = repr(storage.temp_cache)
        name = name + "|0c738e77c892db1c7dde71c5af123f74|"

        storage.get = Mock()
        storage.get.return_value = ""
        storage.set = Mock()

        ret = storage.cacheFunction(storage.temp_cache, {"params": "true" })

        valuen = {}
        valuen[name] = {"timestamp": time.time(), "timeout": 86400.0, "res": ('called', 200) }
        patcher.stop()
        storage.get.assert_called_with("cache" + name)
        storage.set.assert_called_with("cache" + name, repr(valuen))

        assert(ret == ('called', 200) )

    def test_cacheFunction_should_call__getCache(self):
        patcher = patch("time.time")
        patcher.start()
        import time
        patcher(time.time).return_value = 3600 * 48
        storage = StorageServer.StorageServer("Mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.temp_cache = Mock()
        storage.temp_cache.return_value = ("called", 200)
        name = repr(storage.temp_cache)
        name = name + "|0c738e77c892db1c7dde71c5af123f74|"

        storage.get = Mock()
        storage.get.return_value = ""
        storage.set = Mock()
        storage._generateKey = Mock()
        storage._generateKey.return_value = "mock_key"
        storage._getCache = Mock()
        storage._getCache.return_value = []

        ret = storage.cacheFunction(storage.temp_cache, {"params": "true" })

        valuen = {}
        valuen[name] = {"timestamp": time.time(), "timeout": 86400, "res": ('called', 200) }
        patcher.stop()
        storage._getCache.assert_called_with('mock_key', {'mock_key': {'timestamp': 172800, 'timeout': 86400.0, 'res': ('called', 200)}})

    def test_cacheFunction_should_call__setCache(self):
        patcher = patch("time.time")
        patcher.start()
        import time
        patcher(time.time).return_value = 3600 * 48
        storage = StorageServer.StorageServer("Mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.temp_cache = Mock()
        storage.temp_cache.return_value = ("called", 200)
        name = repr(storage.temp_cache)
        name = name + "|0c738e77c892db1c7dde71c5af123f74|"

        storage.get = Mock()
        storage.get.return_value = ""
        storage.set = Mock()
        storage._generateKey = Mock()
        storage._generateKey.return_value = "mock_key"
        storage._setCache = Mock()

        ret = storage.cacheFunction(storage.temp_cache, {"params": "true" })

        valuen = {}
        valuen[name] = {"timestamp": time.time(), "timeout": 86400, "res": ('called', 200) }
        patcher.stop()
        storage._setCache.assert_called_with({}, 'mock_key', ('called', 200))

        assert(ret == ('called', 200) )

    def test_cacheFunction_success(self):
        import time
        storage = StorageServer.StorageServer("Mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.temp_cache = Mock()
        storage.temp_cache.return_value = ("called", 200)
        name = repr(storage.temp_cache)
        name = name + "|0c738e77c892db1c7dde71c5af123f74|"
        value = {}
        value[name] = {"timestamp": time.time(), "timeout": 86400, "res": ('cache', 200) }
        print repr(value)

        storage.get = Mock()
        storage.get.return_value = repr(value)
        storage._evaluate = Mock()
        storage._evaluate.return_value = value
        storage.set = Mock()
        ret = storage.cacheFunction(storage.temp_cache, {"params": "true" })

        storage._evaluate.assert_called_with(repr(value))
        storage.get.assert_called_with("cache" + name)

        print repr(ret)
        assert(ret == ('cache', 200) )

    def test_cacheFunction_use_function(self):
        patcher = patch("time.time")
        patcher.start()
        import time
        patcher(time.time).return_value = 3600 * 48
        storage = StorageServer.StorageServer("Mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage.temp_cache = Mock()
        storage.temp_cache.return_value = ("called", 200)
        name = repr(storage.temp_cache)
        name = name + "|1e885925f0a1e6651c928225921091d8|"
        org_value = {}
        org_value[name] = {"timestamp": 0, "timeout": 86400.0, "res": ('cache', 200) }

        storage.get = Mock()
        storage.get.return_value = repr(org_value)
        storage._evaluate = Mock()
        storage._evaluate.return_value = org_value
        storage.set = Mock()

        ret = storage.cacheFunction(storage.temp_cache, {"params": "true" }, ["first", "second", "third"], "fourth")

        valuen = {}
        valuen[name] = {"timestamp": time.time(), "timeout": 86400.0, "res": ('called', 200) }
        patcher.stop()
        storage.get.assert_called_with("cache" + name)
        storage.set.assert_called_with("cache" + name, repr(valuen))

        org_value[name] = {"timestamp": 0, "timeout": 86400.0, "res": ('cache', 200) }  # This need to be set again.
        storage._evaluate.assert_called_with(repr(org_value))

        assert(ret == ('called', 200) )

    def test_cacheClean(self):
        import time
        storage = StorageServer.StorageServer("mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        value = {}
        value["Mockfunction1"] = {"timestamp": time.time() - (3600 * 0.5), "res": ('cache', 200) }
        value["Mockfunction2"] = {"timestamp": time.time() - (3600 * 1), "res": ('cache', 200) }
        storage.get = Mock()
        storage.set = Mock()
        storage.get.return_value = repr(value)
        ret = storage.cacheClean()
        print repr(ret)
        assert(ret == True)
        del(value["Mockfunction2"])
        storage.set.assert_called_with("cache", repr(value))

    def test_cacheDelete(self):
        storage = StorageServer.StorageServer("mock")
        storage._log = Mock()
        storage._log.side_effect = sys.modules["__main__"].log_override.log
        storage._recv = Mock()
        storage._send = Mock()
        storage._recv.return_value = "true"
        storage.cacheDelete("cache")
        storage._send.assert_called_with(storage.soccon, "{'action': 'del', 'table': 'mock', 'name': 'cachecache'}")

    def test_lock_fails(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._recv = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "false"
        storage._recv.return_value = "'false'"
        storage.soccon = "Mocksock"
        ret = storage.lock("no exists")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'lock', 'table': 'Mock', 'name': 'no exists'}")
        storage._evaluate.assert_called_with("'false'")
        print repr(ret)
        assert(ret == False)

    def test_lock_success(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._recv = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "true"
        storage._recv.return_value = "'true'"
        storage.soccon = "Mocksock"
        ret = storage.lock("no exists")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'lock', 'table': 'Mock', 'name': 'no exists'}")
        storage._evaluate.assert_called_with("'true'")
        print repr(ret)
        assert(ret == True)

    def test_unlock_success(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._recv = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "true"
        storage._recv.return_value = "'true'"
        storage.soccon = "Mocksock"
        ret = storage.unlock("exists")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'unlock', 'table': 'Mock', 'name': 'exists'}")
        storage._evaluate.assert_called_with("'true'")
        print repr(ret)
        assert(ret == True)

    def test_unlock_fail(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._recv = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "false"
        storage._recv.return_value = "'false'"
        storage.soccon = "Mocksock"
        ret = storage.unlock("exists")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'unlock', 'table': 'Mock', 'name': 'exists'}")
        storage._evaluate.assert_called_with("'false'")
        print repr(ret)
        assert(ret == False)

    def test_connect_win32(self):
        dummy_socket = Mock()
        dummy_socket.return_value = "connect"
        sys.modules["socket"].socket.return_value = dummy_socket
        sys.modules["socket"].socket.connect.return_value = "connect"
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.return_value = "59994"

        storage = StorageServer.StorageServer()
        storage.soccon = Mock()
        storage.platform = "win32"
        ret = storage._connect()
        assert(ret == True)

    def test_connect_posix(self):
        dummy_socket = Mock()
        dummy_socket.return_value = "connect"
        sys.modules["socket"].socket.return_value = dummy_socket
        sys.modules["socket"].socket.connect.return_value = "connect"
        storage = StorageServer.StorageServer()
        storage.soccon = Mock()
        storage.platform = "linux2"
        ret = storage._connect()
        print repr(ret)
        assert(ret == True)

    def test_sqlSetMulti(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "true"
        storage._recv = Mock()
        storage._recv.return_value = "'some_result"
        storage.soccon = "Mocksock"
        storage.setMulti("exists", "some_result")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'set_multi', 'table': 'Mock', 'data': 'some_result', 'name': 'exists'}")

    def test_sqlGetMulti_found_match(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "some_result"
        storage._recv = Mock()
        storage._recv.return_value = "'some_result'"
        storage.soccon = "Mocksock"
        ret = storage.getMulti("exists", "items")
        storage._connect.assert_called_with()
        storage._evaluate.assert_called_with("'some_result'")
        storage._send.assert_called_with("Mocksock", "{'action': 'get_multi', 'table': 'Mock', 'name': 'exists', 'items': 'items'}")
        assert(ret == "some_result")

    def test_sqlGetMulti_no_match(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = ""
        storage._recv = Mock()
        storage._recv.return_value = "''"
        storage.soccon = "Mocksock"
        ret = storage.getMulti("no exists", "items")
        storage._connect.assert_called_with()
        storage._evaluate.assert_called_with("''")
        storage._send.assert_called_with("Mocksock", "{'action': 'get_multi', 'table': 'Mock', 'name': 'no exists', 'items': 'items'}")
        assert(ret == "")

    def test_sqlSet(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._recv = Mock()
        storage._recv.return_value = "'some_result"
        storage.soccon = "Mocksock"
        storage.set("exists", "some_result")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'set', 'table': 'Mock', 'data': 'some_result', 'name': 'exists'}")

    def test_sqlGet_found_match(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "some_result"
        storage._recv = Mock()
        storage._recv.return_value = "'some_result'"
        storage.soccon = "Mocksock"
        ret = storage.get("exists")
        storage._connect.assert_called_with()
        storage._evaluate.assert_called_with("'some_result'")
        storage._send.assert_called_with("Mocksock", "{'action': 'get', 'table': 'Mock', 'name': 'exists'}")
        assert(ret == "some_result")

    def test_sqlGet_no_match(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = ""
        storage._recv = Mock()
        storage._recv.return_value = "''"
        storage.soccon = "Mocksock"
        ret = storage.get("no exists")
        storage._connect.assert_called_with()
        storage._send.assert_called_with("Mocksock", "{'action': 'get', 'table': 'Mock', 'name': 'no exists'}")
        storage._evaluate.assert_called_with("''")
        print "D:" + repr(ret)
        assert(ret == "")

    def test_delete(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._recv = Mock()
        storage._recv.return_value = "''"
        storage.soccon = "Mocksock"
        storage.delete("mock_del")

        storage._connect.assert_called_with()
        storage._send.assert_called_with('Mocksock', "{'action': 'del', 'table': 'Mock', 'name': 'mock_del'}")
        storage._recv.assert_called_with("Mocksock")

    def test_set(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = ""
        storage._recv = Mock()
        storage._recv.return_value = "''"
        storage.soccon = "Mocksock"
        ret = storage.set("mock_set", "mock_data")

        storage._connect.assert_called_with()
        storage._send.assert_called_with('Mocksock', "{'action': 'set', 'table': 'Mock', 'data': 'mock_data', 'name': 'mock_set'}")

    def test_get(self):
        storage = StorageServer.StorageServer("Mock")
        storage._connect = Mock()
        storage._send = Mock()
        storage._evaluate = Mock()
        storage._evaluate.return_value = "true"
        storage._recv = Mock()
        storage._recv.return_value = "'true'"
        storage.soccon = "Mocksock"
        ret = storage.get("mock_get")

        print repr(ret)

        storage._connect.assert_called_with()
        storage._send.assert_called_with('Mocksock', "{'action': 'get', 'table': 'Mock', 'name': 'mock_get'}")
        storage._recv.assert_called_with("Mocksock")
        storage._evaluate.assert_called_with("'true'")
        assert(ret == "true")

    def test_log_should_call_xbmc_with_properly_formated_message(self):
        sys.modules["__main__"].xbmc.log = Mock()
        sys.modules["__main__"].xbmc.LOGNOTICE = 0
        description = "Logging"
        storage = StorageServer.StorageServer()
        storage._log(description)
        assert (sys.modules["__main__"].xbmc.log.call_count >=1)

    def test_checkInstanceMode_linux(self):
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.return_value = "true"

        ret = StorageServer.checkInstanceMode()

        print repr(ret)
        assert(ret == False)

    def test_checkInstanceMode_ios(self):
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.side_effect = ["false", "1"]

        StorageServer.run_async = Mock()
        ret = StorageServer.checkInstanceMode()

        print repr(ret)
        assert(ret == True)
        assert(StorageServer.run_async.call_count == 1)


if __name__ == "__main__":
        nose.runmodule()
