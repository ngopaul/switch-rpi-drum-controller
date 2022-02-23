import nxbt
from nxbt import Sticks, Buttons
import keyboard
from time import sleep
import RPi.GPIO as GPIO

# set up GPIO
GPIO.setmode(GPIO.BOARD)
chan0, chan1, chan2, chan3 = 11, 12, 13, 15
GPIO.setup(chan0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(chan1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(chan2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(chan3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Start the NXBT service
nx = nxbt.Nxbt()
switch_addresses = nx.get_switch_addresses()
if not switch_addresses:
  switch_addresses = ['D0:55:09:A8:55:3B']
# Create a Pro controller and wait for it to connect
print("connecting controllers")
controller_0 = nx.create_controller(nxbt.PRO_CONTROLLER, reconnect_address=switch_addresses)
# controller_1 = nx.create_controller(nxbt.PRO_CONTROLLER, reconnect_address=switch_addresses)
nx.wait_for_connection(controller_0)
print("done connecting controller 0")
# nx.wait_for_connection(controller_1)
# print("done connecting controller 1")

stick_keys_c0 = {'w': (Sticks.LEFT_STICK, 0, 100),'a': (Sticks.LEFT_STICK, -100, 0), 's': (Sticks.LEFT_STICK, 0, -100),'d': (Sticks.LEFT_STICK, 100, 0)}
stick_keys_c1 = {'home': (Sticks.LEFT_STICK, 0, 100),'delete': (Sticks.LEFT_STICK, -100, 0), 'end': (Sticks.LEFT_STICK, 0, -100),'page down': (Sticks.LEFT_STICK, 100, 0)}
button_keys_c0 = {'t': Buttons.DPAD_UP,'f': Buttons.DPAD_LEFT,'g': Buttons.DPAD_DOWN,'h': Buttons.DPAD_RIGHT, 'i': Buttons.X,'j': Buttons.Y,'k': Buttons.B,'l': Buttons.A, 'backspace': Buttons.HOME, '\\': Buttons.CAPTURE}
button_keys_c1 = {'up': Buttons.DPAD_UP,'left': Buttons.DPAD_LEFT,'down': Buttons.DPAD_DOWN,'right': Buttons.DPAD_RIGHT, '/': Buttons.X,'7': Buttons.Y,'8': Buttons.B,'9': Buttons.A}

def press_button(button_key):
  if button_key in button_keys_c0:
    print(f" Pressing {button_keys_c0[button_key]} on controller 0")
    nx.press_buttons(controller_0, [button_keys_c0[button_key]])
  elif button_key in button_keys_c1:
    print(f" Pressing {button_keys_c1[button_key]} on controller 1")
    nx.press_buttons(controller_1, [button_keys_c1[button_key]])

def button_wrapper(button_key):
  return lambda channel=None: press_button(button_key)

def tilt_stick(stick_key):
  if stick_key in stick_keys_c0:
    print(f" Tilting stick {stick_keys_c0[stick_key]} on controller 0")
    stick, x, y = stick_keys_c0[stick_key]
    nx.tilt_stick(controller_0, stick, x, y)
  elif stick_key in stick_keys_c1:
    print(f" Tilting stick {stick_keys_c1[stick_key]} on controller 1")
    stick, x, y = stick_keys_c1[stick_key]
    nx.tilt_stick(controller_1, stick, x, y)

def stick_wrapper(stick_key):
  return lambda channel=None: tilt_stick(stick_key)

for button_key in button_keys_c0:
  keyboard.add_hotkey(button_key, button_wrapper(button_key))

for stick_key in stick_keys_c0:
  keyboard.add_hotkey(stick_key, stick_wrapper(stick_key))

GPIO.add_event_detect(chan0, GPIO.RISING, callback=button_wrapper('f'), bouncetime=200) # dpadleft
GPIO.add_event_detect(chan1, GPIO.RISING, callback=button_wrapper('g'), bouncetime=200) # dpaddown
GPIO.add_event_detect(chan2, GPIO.RISING, callback=button_wrapper('k'), bouncetime=200) # b
GPIO.add_event_detect(chan3, GPIO.RISING, callback=button_wrapper('l'), bouncetime=200) # a

print("Waiting on ` (backtick)")
keyboard.wait('`')
print("Cleaning up")
nx.remove_controller(controller_0)
