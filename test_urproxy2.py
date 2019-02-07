import math
import sys
import time
from urutils.urproxy import URProxy
import socket


def callback(msg):
    print(int.from_bytes(msg, byteorder='big'))


IPROBOT = "192.168.7.235"
IPCOMPUTER = "192.168.7.114"
OUTPUTPORT = 55555
INPUTPORT = 4000

robot = URProxy(IPROBOT)

robot.setInputProxy(hostip=IPCOMPUTER,
                    port=INPUTPORT,
                    preloadscript=True)

robot.setOutputProxy(hostip=IPCOMPUTER,
                     port=OUTPUTPORT,
                     callback=callback,
                     preloadscript=True)


prog_test = [
    'while True:',
    'if input_data[0]>0:',
    'x = input_data[1]',
    'output(x)',
    'movej([0, -1.57, +1.57, -1.57, x, +1.57], 0.5, 0.5)',
    'end',
    'sleep(1)',
    'end'
]
robot.load(prog_test)


###########################################################################

try:
    t = 0
    w = 0.1
    d = 0.5
    while True:
        t += 1
        x = float(-math.pi/2 + d*math.sin(w*t))
        robot.input("({})".format('%.2f' % x))
        time.sleep(0.5)
except KeyboardInterrupt:
    stored_exception = sys.exc_info()

if stored_exception:
    robot.do("movej", ([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5))
    robot.closeall()

sys.exit()
