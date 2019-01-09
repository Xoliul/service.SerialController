import xbmc, xbmcgui
import wiringpi, os, time


class PowerMan():
    def __init__(self, p_pwmpin, p_addon):
        #xbmc.Monitor.__init__(self)
        self.m_screenPin = p_pwmpin
        self.m_addon = p_addon

        self.m_AccPowerON = True

        self.m_FirstIdle = False
        self.m_SecondIdle = False
        self.m_ShutdownIdle = False
        self.m_isPlaying = False

        self.m_ScreenSaverOn = False
        self.m_ScreenSaver_StartTime = time.time()

        self.m_currentbrightness =1.0
        self.m_targetbrightness = 1.0
        self.m_downspeed = 0.8
        self.m_upspeed = 3.0

        self.m_lasttime = time.time()

        self.pwmworking = False
        try:
            wiringpi.wiringPiSetupGpio()
            wiringpi.pinMode(self.m_screenPin, wiringpi.PWM_OUTPUT)
            wiringpi.pwmSetMode(wiringpi.PWM_MODE_MS)
            wiringpi.pwmWrite(self.m_screenPin, 1024)
            self.pwmworking = True
        except:
            xbmc.log("PWM Screensaver: failed to setup WiringPi!")



    def OnScreensaverActivated(self):
        #xbmc.Monitor.onScreensaverActivated(self)
        if not self.m_ScreenSaverOn:
            self.m_ScreenSaverOn = True
            self.m_ScreenSaver_StartTime = time.time()

    def OnScreensaverDeactivated(self):
        #xbmc.Monitor.onScreensaverDeactivated(self)
        self.m_ScreenSaverOn = False


    def __GetIdleTimes__(self):
        #this is junk, does not work at all, xbmc does not reset idle on touchscreen or code actions
        #globalidle = xbmc.getGlobalIdleTime()
        l_ss = bool(xbmc.getCondVisibility("System.ScreenSaverActive"))

        if l_ss:
            self.OnScreensaverActivated()
        else:
            self.OnScreensaverDeactivated()


        l_elapsed = int(time.time() - self.m_ScreenSaver_StartTime)
        #xbmcgui.Dialog().notification("Powerman", "elapsed: %s" % l_elapsed, time = 100)

        if self.m_ScreenSaverOn:
            l_firstidle = int(self.m_addon.getSetting("timeout1")) * 60
            if l_elapsed >= l_firstidle:

                self.m_FirstIdle = True
            else:
                self.m_FirstIdle = False

            l_secondidle = int(self.m_addon.getSetting("timeout2")) * 60
            if l_elapsed >= l_secondidle:

                self.m_SecondIdle = True
            else:
                self.m_SecondIdle = False

            self.m_isPlaying = bool(xbmc.getCondVisibility('Player.Playing'))

            l_thirdidle = int(float(self.m_addon.getSetting("shutdowntime")) * 3600.0)
            if l_elapsed >= l_thirdidle:
                self.m_ShutdownIdle = True
            else:
                self.m_ShutdownIdle = False
        else:
            self.m_FirstIdle = False
            self.m_SecondIdle = False
            self.m_ShutdownIdle = False


    def DoSerialCommand(self, p_command):
        l_com = str(p_command).replace("power:", "")
        if l_com == "acc_on":
            self.m_AccPowerON = True
        if l_com == "acc_off":
            self.m_AccPowerON = False
        if l_com == "togglescreen":
            xbmc.executebuiltin("ActivateScreensaver")
        if l_com == "standby":
            xbmc.executebuiltin("Action(Back)")

    def AdjustBrightness(self, p_report=False):
        if self.m_FirstIdle and not self.m_SecondIdle:
            self.m_targetbrightness = float(self.m_addon.getSetting("brightness1"))/100
        elif self.m_SecondIdle:
            self.m_targetbrightness = float(self.m_addon.getSetting("brightness2"))/100
        else:
            self.m_targetbrightness = 1.0


        delta = time.time() - self.m_lasttime
        if self.m_currentbrightness > self.m_targetbrightness:
            self.m_currentbrightness -= delta * self.m_downspeed
            if self.m_currentbrightness < self.m_targetbrightness:
                self.m_currentbrightness = self.m_targetbrightness
                self.SetPWM(self.m_currentbrightness)
        elif self.m_currentbrightness < self.m_targetbrightness:
            self.m_currentbrightness += delta * self.m_upspeed
            if self.m_currentbrightness > self.m_targetbrightness:
                self.m_currentbrightness = self.m_targetbrightness
                self.SetPWM(self.m_currentbrightness)
        if self.m_currentbrightness != self.m_targetbrightness:
            self.SetPWM(self.m_currentbrightness)
        elif p_report:
            print("Target brightness %s stepping towards with delta %s at current %s") % (self.m_targetbrightness, delta, self.m_currentbrightness)
        self.m_lasttime = time.time()

    def SetPWM(self, p_cycle):
        fullcycle = int(p_cycle * 1024)
        wiringpi.pwmWrite(self.m_screenPin, fullcycle)
        try:
            if p_cycle == 0:
                os.system("xset dpms force standby")
            else:
                os.system("xset dpms force on")
        except:
            xbmc.log("Serial Media Controller: Failed to access X Server!")

    def CheckForShutdown(self):
        if bool(self.m_addon.getSetting("doautoshutdown")):
            if not self.m_isPlaying and self.m_ShutdownIdle and not self.m_AccPowerON:
                self.SetPWM(0.0)
                os.system("shutdown now")

    def Loop(self, monitor):
        while not monitor.abortRequested():
            self.__GetIdleTimes__()
            self.AdjustBrightness()
            self.CheckForShutdown()
            if monitor.waitForAbort(0.1):
                try:
                    xbmc.log("Serial Media Controller: power loop stopped")
                    self.SetPWM(float(self.m_addon.getSetting("brightness2"))/100)
                    break
                except:
                    xbmc.log("Serial Media Controller: Failed To Exit Power Loop Gracefully")