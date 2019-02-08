import math
import sys
import time
from urutils.urproxy import URProxy
import socket

# p[-0.486818,-0.110876,0.430771,-3.12873,-0.00872855,-0.000941246]


def callback(msg):
    decodepose(msg)


def decodepose(data):
    y = data.decode("utf-8").split("p[")[1].split("]")[0].split(",")
    w = [float(i) for i in y]
    return w


IPROBOT = "192.168.7.235"
IPCOMPUTER = "192.168.7.114"
OUTPUTPORT = 55555
INPUTPORT = 4000

robot = URProxy(IPROBOT)

robot.setInputProxy(hostip=IPCOMPUTER,
                    port=INPUTPORT,
                    preloadscript=False,
                    n_inputs=1)

robot.setOutputProxy(hostip=IPCOMPUTER,
                     port=OUTPUTPORT,
                     callback=callback,
                     preloadscript=True,
                     datadef='get_actual_tcp_pose()')

prog_test = [
    'while True:',
    'tcp_pose = get_actual_tcp_pose()',
    'output(tcp_pose)',
    'speedl([0.001, 0, 0, 0, 0, 0], 10, 10)',
    'sleep(0.01)',
    'end'
]
robot.load(prog_test)


###########################################################################

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    stored_exception = sys.exc_info()

if stored_exception:
    robot.do("movej", ([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5))
    robot.closeall()

sys.exit()
