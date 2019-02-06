import time
import socket

EOC = "\n"


def sendCommand(cmd_str):
    # Connection to robot
    HOST = "192.168.7.235"    # The remote host
    PORT = 30002		# The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    # Send command
    print(cmd_str)
    command = cmd_str + EOC
    s.send(command.encode())
    data = s.recv(1024)
    s.close()
    print("Received", repr(data))


# URScript command
sendCommand("movej([0, -1.57, +1.57, -1.57, -1.57, +1.57], a=0.5, v=0.5)")
