#!/usr/bin/env python3
#--------------------------------------
#
#  Author : Kevin LECLERCQ
#  Date   : 06/04/2022
#
#  LCD2004 Screen display driver for Raspberry PI
#
#  Derived from 20x4 LCD Test Script with backlight control and text justification from Matt Hawkins https://www.raspberrypi-spy.co.uk/
#  Derived from node-red-contrib-pcf8574-lcd https://github.com/NuklearStriker/node-red-contrib-pcf8574-lcd
#
#--------------------------------------

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time

class LCD2004(object):
    def __init__(self):
      # Define GPIO to LCD mapping
      self.LCD_RS = 7
      self.LCD_E  = 8
      self.LCD_D4 = 25
      self.LCD_D5 = 24
      self.LCD_D6 = 23
      self.LCD_D7 = 18
      self.LED_ON = 15
      
      #Configuring GPIO for LCD Mapping
      GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
      GPIO.setup(self.LCD_E, GPIO.OUT)  # E
      GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
      GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
      GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
      GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
      GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7
      GPIO.setup(self.LED_ON, GPIO.OUT) # Backlight enable

      # Define some device constants
      self.LCD_WIDTH = 20    # Maximum characters per line
      self.LCD_CHR = True
      self.LCD_CMD = False

      self.LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
      self.LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
      self.LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
      self.LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line
      
      self.CLEARDISPLAY   = 0x01
      self.RETURNHOME     = 0x02
      self.ENTRYMODESET   = 0x04
      self.DISPLAYCONTROL = 0x08
      self.CURSORSHIFT    = 0x10
      self.FUNCTIONSET    = 0x20
      self.SETCGRAMADDR   = 0x40
      self.SETDDRAMADDR   = 0x80

      # flags for display entry mode
      self.ENTRYRIGHT          = 0x00
      self.ENTRYLEFT           = 0x02
      self.ENTRYSHIFTINCREMENT = 0x01
      self.ENTRYSHIFTDECREMENT = 0x00

      # flags for display on/off control
      self.DISPLAYON  = 0x04
      self.DISPLAYOFF = 0x00
      self.CURSORON   = 0x02
      self.CURSOROFF  = 0x00
      self.BLINKON    = 0x01
      self.BLINKOFF   = 0x00

      # flags for display/cursor shift
      self.DISPLAYMOVE = 0x08
      self.CURSORMOVE  = 0x00
      self.MOVERIGHT   = 0x04
      self.MOVELEFT    = 0x00

      # flags for function set
      self._8BITMODE = 0x10
      self._4BITMODE = 0x00
      self._2LINE    = 0x08
      self._1LINE    = 0x00
      self._5x10DOTS = 0x04
      self._5x8DOTS  = 0x00

      # flags for backlight control
      self.BACKLIGHT   = 0x08
      self.NOBACKLIGHT = 0x00

      # Timing constants
      self.E_PULSE = 0.0005
      self.E_DELAY = 0.0005
      
      self.screenConf = {
        'backlight'  : self.NOBACKLIGHT, #BACKLIGHTOFF
        'entrySide'  : self.ENTRYLEFT, #ENTRYLEFT
        'entryShift' : self.ENTRYSHIFTDECREMENT, #ENTRYSHIFTDECREMENT
        'blink'      : self.BLINKOFF, #BLINKON
        'cursor'     : self.CURSOROFF, #CURSORON
        'display'    : self.DISPLAYON, #DISPLAYON
        'dataLength' : self._4BITMODE, #4BITSMODE
        'nbLine'     : self._2LINE, #2LINE
        'font'       : self._5x10DOTS #5x10DOTS
      }
      
      # Initialise display
      self.lcd_init()
      
      # Toggle backlight on-off-on
      self.lcd_backlight(True)
      time.sleep(0.5)
      self.lcd_backlight(False)
      time.sleep(0.5)
      self.lcd_backlight(True)
      time.sleep(0.5)
    
    def __del__(self):
      # body of destructor
      GPIO.cleanup()

    def lcd_init(self):
      # Initialise display
      self.write(0x33,self.LCD_CMD) # 110011 Initialise
      self.write(0x32,self.LCD_CMD) # 110010 Initialise
      self.writeFunctionSet()
      self.writeDisplayControl()
      self.writeEntrySet()
      self.write(0x01,self.LCD_CMD) # 000001 Clear display
      time.sleep(self.E_DELAY)
      
    def writeFunctionSet(self):
      self.functionSet = self.FUNCTIONSET | self.screenConf['dataLength'] | self.screenConf['nbLine'] | self.screenConf['font']
      self.write(self.functionSet, self.LCD_CMD)
    
    def writeDisplayControl(self):
      self.displayControl = self.DISPLAYCONTROL | self.screenConf['display'] | self.screenConf['cursor'] | self.screenConf['blink']
      self.write(self.displayControl, self.LCD_CMD)
    
    def writeEntrySet(self):
      self.entrySet = self.ENTRYMODESET | self.screenConf['entrySide'] | self.screenConf['entryShift']
      self.write(self.entrySet, self.LCD_CMD)
    
    def write(self, bits, mode):
      # Send byte to data pins
      # bits = data
      # mode = True  for character
      #        False for command

      GPIO.output(self.LCD_RS, mode) # RS

      # High bits
      GPIO.output(self.LCD_D4, False)
      GPIO.output(self.LCD_D5, False)
      GPIO.output(self.LCD_D6, False)
      GPIO.output(self.LCD_D7, False)
      if bits&0x10==0x10:
        GPIO.output(self.LCD_D4, True)
      if bits&0x20==0x20:
        GPIO.output(self.LCD_D5, True)
      if bits&0x40==0x40:
        GPIO.output(self.LCD_D6, True)
      if bits&0x80==0x80:
        GPIO.output(self.LCD_D7, True)

      # Toggle 'Enable' pin
      self.lcd_toggle_enable()

      # Low bits
      GPIO.output(self.LCD_D4, False)
      GPIO.output(self.LCD_D5, False)
      GPIO.output(self.LCD_D6, False)
      GPIO.output(self.LCD_D7, False)
      if bits&0x01==0x01:
        GPIO.output(self.LCD_D4, True)
      if bits&0x02==0x02:
        GPIO.output(self.LCD_D5, True)
      if bits&0x04==0x04:
        GPIO.output(self.LCD_D6, True)
      if bits&0x08==0x08:
        GPIO.output(self.LCD_D7, True)

      # Toggle 'Enable' pin
      self.lcd_toggle_enable()

    def lcd_toggle_enable(self):
      # Toggle enable
      time.sleep(self.E_DELAY)
      GPIO.output(self.LCD_E, True)
      time.sleep(self.E_PULSE)
      GPIO.output(self.LCD_E, False)
      time.sleep(self.E_DELAY)

    def lcd_string(self, message, line, style):
      # Send string to display
      # style=1 Left justified
      # style=2 Centred
      # style=3 Right justified

      if style==1:
        message = message.ljust(self.LCD_WIDTH," ")
      elif style==2:
        message = message.center(self.LCD_WIDTH," ")
      elif style==3:
        message = message.rjust(self.LCD_WIDTH," ")

      self.write(line, self.LCD_CMD)

      for i in range(self.LCD_WIDTH):
        self.write(ord(message[i]),self.LCD_CHR)

    # Toggle backlight on-off-on
    def lcd_backlight(self, flag):
      GPIO.output(self.LED_ON, flag)

    # Clear the screen
    def clearScreen(self):
      self.write(self.CLEARDISPLAY, self.LCD_CMD)

    # Place cursor to 0,0
    def home(self):
      self.write(self.RETURNHOME, self.LCD_CMD)

    # Turn blink of cursor off
    def blinkOff():
      self.screenConf['blink'] = self.BLINKOFF
      self.writeDisplayControl()

    # Turn blink of cursor on
    def blinkOn():
      self.screenConf['blink'] = self.BLINKON
      self.writeDisplayControl()

    # Turn cursor off
    def cursorOff():
      self.screenConf['cursor'] = self.CURSOROFF
      self.writeDisplayControl()

    # Turn cursor on
    def cursorOn():
      self.screenConf['cursor'] = self.CURSORON
      self.writeDisplayControl()

    # Turn display off
    def screenOff():
      self.screenConf['display'] = self.DISPLAYOFF
      self.writeDisplayControl()
      self.lcd_backlight(False)

    # Turn display on
    def screenOn():
      self.screenConf['display'] = self.DISPLAYON
      self.writeDisplayControl()
      self.lcd_backlight(True)
