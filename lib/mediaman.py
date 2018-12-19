from time import sleep
import os, subprocess, sys

import json, xbmc


class MediaControl:

    def __init__(self):
        self.m_currpos = 0
        self.m_prevpos = 0
        self.m_accel = 2
        self.m_slow = 1
        self.m_fast = 3

        self.m_skipcountdown = 0.0
        self.m_skipbounce = 0.5
        self.m_canskip = True

        self.m_skipstepreset = 0.0
        self.m_skipstep = 1

        self.m_looplength = 0.1

    def ChangeVolume(self, p_value):
        if p_value != 0:
            l_rpc = '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["volume"]}, "id": 1}'
            l_currvol = json.loads(xbmc.executeJSONRPC(l_rpc))["result"]["volume"]
            l_targetvol = l_currvol + p_value
            if l_targetvol < 0:
                l_targetvol = 0
            elif l_targetvol > 100:
                l_targetvol = 100

            xbmc.executebuiltin("SetVolume(%s,showvolumebar)" % l_targetvol)

    def DoSerialCommand(self, p_serialcommand):
        l_com = str(p_serialcommand).replace("media:", "")
        if l_com.startswith("rot"):
            if l_com.endswith("+"):
                self.m_currpos += 1
            elif l_com.endswith("-"):
                self.m_currpos -= 1
        elif l_com == "toggleplay":
            self.MediaPlayPause()
        elif l_com == "togglestop":
            self.MediaStop()
        elif l_com == "next":
            self.MediaNext()
        elif l_com == "prev":
            self.MediaPrevious()
        elif l_com.startswith("skip"):
            if l_com == "skipfwd":
                self.MediaSkip(1)
            elif l_com == "skipbwd":
                self.MediaSkip(-1)
        elif l_com == "togglemute":
            self.MediaToggleMute()
        elif l_com == "toggleclear":
            self.MediaClearList()

    def MediaPlayPause(self):
        xbmc.Player().pause()
    def MediaPause(self):
        if xbmc.Player().isPlaying():
            xbmc.Player().pause()
    def MediaPlay(self):
        xbmc.Player().play()
    def MediaStop(self):#
        xbmc.Player().stop()
    def MediaNext(self):
        xbmc.Player().playnext()
    def MediaPrevious(self):
        xbmc.Player().playprevious()
    def MediaSkip(self, p_direction):
        if self.m_canskip:
            skip = 2.0
            if self.m_skipstep > 10:
                skip = 20.0
                self.m_skipbounce = 1.0
            elif self.m_skipstep > 5:
                skip = 10.0
                self.m_skipbounce = 0.7
            elif self.m_skipstep > 2:
                skip = 5.0
                self.m_skipbounce = 0.5

            if p_direction > 0:
                xbmc.executebuiltin("Seek(%s)" % skip)
            elif p_direction < 0:
                xbmc.executebuiltin("Seek(-%s)" % skip)
            self.m_canskip = False
            self.m_skipcountdown = self.m_skipbounce
            self.m_skipstepreset = 2.0
            self.m_skipstep += 1

    def MediaToggleMute(self):
        xbmc.executebuiltin('Mute')
    def MediaClearList(self):
        xbmc.Player().stop()
        xbmc.executebuiltin("Playlist.Clear")



    def Check(self):
        l_diff = self.m_currpos - self.m_prevpos
        l_step = self.m_slow
        if abs(l_diff) >= self.m_accel:
            # print("fast spin detected")
            l_step = self.m_fast
        if l_diff != 0:
            # print("loop")
            self.ChangeVolume(l_diff * l_step)
        self.m_prevpos = self.m_currpos

        if self.m_skipcountdown > 0:
            self.m_skipcountdown -= self.m_looplength
        else:
            self.m_canskip = True

        if self.m_skipstepreset > 0:
            self.m_skipstepreset -= self.m_looplength
        else:
            self.m_skipstep = 1
            self.m_skipbounce = 0.5

    def Loop(self, monitor):
        while not monitor.abortRequested():
            self.Check()
            if monitor.waitForAbort(self.m_looplength):
                # Abort was requested while waiting. We should exit
                xbmc.log("Serial Media Controller: media loop stopped")
                break
