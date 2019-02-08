import sys
import time
from urutils.urproxy import URProxy


''' Example of simple program to move the robot in some joint configurations and get the a status feedback flag'''


def callback(msg):
    print(int.from_bytes(msg, byteorder='big'))


IPROBOT = "192.168.7.235"
IPCOMPUTER = "192.168.7.114"
FEEDBACKPORT = 55555
robot = URProxy(IPROBOT)

robot.setOutputProxy(hostip=IPCOMPUTER,
                     port=FEEDBACKPORT,
                     callback=callback,
                     preloadscript=True,
                     datadef='0')


###########################################################################


robot.do("movej", ([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5))

prog_test = [
    'x = get_actual_joint_positions()',
    'output(1)',
    "sleep(0.5)",
    "movej([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5)",
    "i = 0",
    "while i<5:",
    'output(i)',
    "movej([0, -1.57, +1.57, -1.57, -1.37, +1.57], 0.5, 0.5)",
    "movej([0, -1.57, +1.57, -1.57, -1.77, +1.57], 0.5, 0.5)",
    "i = i + 1",
    'output(-1)',
    "end"   # end while

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
