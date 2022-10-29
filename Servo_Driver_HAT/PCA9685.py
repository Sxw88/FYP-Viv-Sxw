import time
import math
import smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("[*]servo: Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("[*]servo: I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("[*]servo: I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("[*]servo: Setting PWM frequency to %d Hz" % freq)
      print("[*]servo: Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("[*]servo: Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("[*]servo: channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
    
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        # Pulse width in micro-seconds (us)
                                    # PWM frequency is 50HZ,the period is 20000us or 0.02 seconds
                                    # Assuming range of output is 0-4096 (12-bit)
    print("Set PWM Pulse   : " + str(pulse))
    if int(pulse) != 0:
      print("Rounded Pulse   : " + str(int(pulse)))
    
    self.setPWM(channel, 0, int(pulse))

    # Table below shows pulse length and percent power for reference
    """
    PULSE HIGH TIME             PERCENT POWER           DIRECTION

    1000 us                     100%                    Clockwise
    1100 us                     80%                     Clockwise
    1200 us                     60%                     Clockwise
    1300 us                     40%                     Clockwise
    1400 us                     20%                     Clockwise
    1500 us                     0%                      Stopped
    1600 us                     20%                     Anticlockwise
    1700 us                     40%                     Anticlockwise
    1800 us                     60%                     Anticlockwise
    1900 us                     80%                     Anticlockwise
    2000 us                     100%                    Anticlockwise

    """

