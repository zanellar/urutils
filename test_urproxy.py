import sys
import time
from utils.urproxy import RobotCommand


def callback(msg):
    print(int.from_bytes(msg, byteorder='big'))


IPROBOT = "192.168.7.235"
IPCOMPUTER = "192.168.7.114"
FEEDBACKPORT = 55555
robot = RobotCommand(
    server_addrs=dict(host=IPROBOT, port=30002),
    client_addrs=dict(host="0.0.0.0", port=FEEDBACKPORT)
)

robot.setFeedback(host=IPCOMPUTER,
                  port=FEEDBACKPORT,
                  callback=callback)


###########################################################################


robot.do("movej", ([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5))

prog_test = [
    'x = get_actual_joint_positions()',
    'feedback(1000*1.235233333)',
    "sleep(0.5)",
    "movej([0, -1.57, +1.57, -1.57, -1.57, +1.57], 0.5, 0.5)",
    "i = 0",
    "while i<5:",
    'feedback(2)',
    "movej([0, -1.57, +1.57, -1.57, -1.37, +1.57], 0.5, 0.5)",
    "movej([0, -1.57, +1.57, -1.57, -1.77, +1.57], 0.5, 0.5)",
    "i = i + 1",
    'feedback(3)',
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
