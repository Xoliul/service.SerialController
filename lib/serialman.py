from serial import Serial
#from serial.tools import list_ports
import xbmc


class SerialMan():
    def __init__(self, p_mediaman, p_powerman):
        self.m_mediaman = p_mediaman
        self.m_powerman = p_powerman
        self.SerialWorking = False

    def StartConnection(self, p_port='/dev/ttyS0', p_baudrate=9600):
        try:
            self.SerialConnection = Serial(port=p_port, baudrate=p_baudrate, timeout=0.05)
            self.SerialConnection.flushInput()
            self.SerialWorking = True
            return True
        except Exception, e:
            xbmc.log("Serial Service Failed to open Serial port:\n" + str(e))

            return False

    def Loop(self, monitor):
        if self.SerialWorking:
            while not monitor.abortRequested():
                # check Serial
                #if (self.SerialConnection.is_open):
                line = self.SerialConnection.readline()
                sertxt = line.decode('utf-8').strip()
                if not (str(sertxt).startswith("log:")):
                    if not (str(sertxt).startswith("power")):
                        self.m_mediaman.DoSerialCommand(sertxt)
                    else:
                        self.m_powerman.DoSerialCommand(sertxt)
                else:
                    xbmc.log("Arduino Serial log" + str(sertxt))
                if monitor.abortRequested():
                    try:
                        xbmc.log("Serial Media Controller: Serial loop stopped, closing connection")
                        self.SerialConnection.close()
                        break
                    except:
                        xbmc.log("Serial Media Controller: Failed To Exit Gracefully")