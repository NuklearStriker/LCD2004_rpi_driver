#!/usr/bin/env python3
#--------------------------------------
#  Test script for LCD2004 library
#--------------------------------------

import LCD2004
import time

if __name__ == '__main__':

  screen = LCD2004.LCD2004()
    
  try:
    while True:

      # Send some centred test
      screen.lcd_string("--------------------",screen.LCD_LINE_1,2)
      screen.lcd_string("Rasbperry Pi",screen.LCD_LINE_2,2)
      screen.lcd_string("Model B",screen.LCD_LINE_3,2)
      screen.lcd_string("--------------------",screen.LCD_LINE_4,2)

      time.sleep(3) # 3 second delay

      screen.clearScreen()

      screen.lcd_string("Raspberrypi-spy",screen.LCD_LINE_1,1)
      screen.lcd_string(".co.uk",screen.LCD_LINE_2,3)
      screen.lcd_string("",screen.LCD_LINE_3,2)
      screen.lcd_string("20x4 LCD Module Test",screen.LCD_LINE_4,2)

      time.sleep(3) # 3 second delay

      screen.clearScreen()

      time.sleep(3) # 3 second delay
  except KeyboardInterrupt:
    pass
  finally:
    screen.clearScreen()
    screen.lcd_string("Goodbye!",screen.LCD_LINE_1,2)
    del screen
