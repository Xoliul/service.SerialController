import time, threading, os
import xbmc, xbmcaddon, xbmcgui

import lib.mediaman as mediaman
import lib.serialman as serialman
import lib.powerman as powerman

if __name__ == '__main__':

    g_addon = xbmcaddon.Addon()
    __addonname__ = g_addon.getAddonInfo('name')
    monitor = xbmc.Monitor()

    g_mediaman = mediaman.MediaControl()

    g_pin = int(g_addon.getSetting("pwmpin"))
    g_powerman = powerman.PowerMan(g_pin, g_addon)
    #g_powerman.Setup(g_pin, g_addon)

    g_port = g_addon.getSetting("port")
    g_serialman = serialman.SerialMan(g_mediaman, g_powerman)
    serialconnected = g_serialman.StartConnection(g_port)
    if not serialconnected:
        xbmcgui.Dialog().ok(__addonname__, "Error!", "Failed to open serial connection on port %s" % g_port)
    else:
        thread1 = threading.Thread(target=g_serialman.Loop, args=[monitor])
        thread1.start()
        thread2 = threading.Thread(target=g_mediaman.Loop, args=[monitor])
        thread2.start()
        thread3 = threading.Thread(target=g_powerman.Loop, args=[monitor])
        thread3.start()
