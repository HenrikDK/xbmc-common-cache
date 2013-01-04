import sys
import time


class MockCacheDepends:
    def mock(self):
        import platform
        sys.path.append("../plugin/")

        # Setup default test various values
        sys.modules["__main__"].version = "1.5.0"
        sys.modules["__main__"].plugin = "StorageClient Beta-1.5.0"
        sys.modules["__main__"].dbg = True
        try:
            plat = platform.uname()
        except:
            plat = ('', '', '', '', '', '')

        if plat[0] == "FreeBSD":
            sys.modules["__main__"].dbglevel = 10
        else:
            sys.modules["__main__"].dbglevel = 10

    def mockXBMC(self):
        from mock import Mock
        sys.path.append("../xbmc-mocks/")
        import xbmc
        import xbmcaddon
        import xbmcgui
        import xbmcplugin
        import xbmcvfsdummy as xbmcvfs

        # Setup basic xbmc dependencies
        sys.modules["__main__"].xbmcaddon = Mock(spec=xbmcaddon)
        sys.modules["__main__"].xbmc = Mock(spec=xbmc)
        sys.modules["__main__"].xbmc.translatePath.return_value = "./tmp/"
        sys.modules["__main__"].xbmc.abortRequested = False
        sys.modules["__main__"].xbmc.log = Mock()
        sys.modules["__main__"].xbmc.log.side_effect = self.log
        sys.modules["__main__"].xbmcvfs = xbmcvfs

        sys.modules["__main__"].xbmcaddon.Addon().getAddonInfo.return_value = "tmp"
        sys.modules["__main__"].xbmcaddon.Addon().getSetting.side_effect = ["false", "2"]

    def log(self, description, level=0):
        import inspect
        try:
            print "%s [%s] %s : '%s'" % (time.strftime("%H:%M:%S"), "BlipTv IntegrationTest", inspect.stack()[3][3], description.decode("utf-8", "ignore"))
        except:
            print "%s [%s] %s : '%s'" % (time.strftime("%H:%M:%S"), "BlipTv IntegrationTest", inspect.stack()[3][3], description)

    def execute(self, function, *args):
        return function(*args)
