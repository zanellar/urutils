import sys
import time
from urutils.urproxy import URProxy
import socket


''' Example of program to send an input float data to the robot'''


IPROBOT = "192.168.7.235"
IPCOMPUTER = "192.168.7.114"
INPUTPORT = 4000

robot = URProxy(IPROBOT)

robot.setInputProxy(hostip=IPCOMPUTER,
                    port=INPUTPORT,
                    n_inputs=1,
                    preloadscript=True)


prog_test = [
    'while True:',
    'if input_data[0]>0:',
    'x = input_data[1]',
    'movej([0, -1.57, +1.57, -1.57, x, +1.57], 0.5, 0.5)',
    'end',
    'sleep(1)',
    'end'
]
robot.load(prog_test)

###########################################################################

try:
    while True:
        x = float(input("x="))
        robot.input("({})".format(x))
        time.sleep(0.01)
except KeyboardInterrupt:
    stored_exception = sys.exc_info()

if stored_exception:
    robot.do("movej", ([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5))
    robot.closeall()

sys.exit()
