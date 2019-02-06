import time
import socket
import threading


class RobotClient(object):

    EOC = "\n"

    def __init__(self, host, port):
        self.host = host
        self.port = port

        # Open connection to robot
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)

        # Variables
        self.callback = None
        self.last_message = None
        self.message_thread = None

    def _waitMessage(self):
        print("Connecting to client ...")
        client_socket, addr = self.socket.accept()
        print("Connected! Waiting for message...")
        while self.message_thread.isAlive():
            print("Waiting for message...")
            self.last_message = client_socket.recv(1024)
            time.sleep(0.001)       # BUG required ???????????????????????
            try:
                if self.callback is not None:
                    self.callback(self.last_message)
            except Exception as e:
                print(e)

    def registerCallback(self, callback):
        self.callback = callback

    def connectClient(self):
        self.message_thread = threading.Thread(
            target=self._waitMessage
        )
        self.message_thread.start()

    def close(self):
        self.socket.close()
        self.message_thread.join()


class RobotServer(object):

    EOC = "\n"

    def __init__(self, host, port):
        self.host = host
        self.port = port

        # Open connection to robot
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

        # Variables
        self.is_ready = True

    def sendCommand(self, cmd_str):
        self.is_ready = False
        print("sending...", cmd_str)

        # Format command
        command = cmd_str + RobotServer.EOC

        # Send command
        self.socket.send(command.encode())

        data = self.socket.recv(1024)
        self.is_ready = True
        # print("Received", repr(data))

    def close(self):
        # Close connection to robot
        self.socket.close()

    def sendProgram(self, prg_list):
        prg_str = "def myProg():" + RobotServer.EOC
        identspace = " "
        for line in prg_list:
            prg_str += identspace + line + RobotServer.EOC
        prg_str = prg_str + "end" + RobotServer.EOC
        self.sendCommand(prg_str)


class RobotCommand(object):

    def __init__(self, server_addrs, client_addrs):
        self.server_addrs = server_addrs
        self.robot_server = RobotServer(
            host=server_addrs["host"],  # "192.168.7.235",
            port=server_addrs["port"]  # 30002
        )
        self.client_addrs = client_addrs
        self.robot_client = RobotClient(
            host=client_addrs["host"],  # "0.0.0.0",
            port=client_addrs["port"]  # 55555
        )
        self.robotfeedback = None
        self.callback = None
        self._prog_feedback_list = []

    def _robotFeedback(self, msg, callback=None):
        self.robotfeedback = msg
        if callback is not None:
            callback(msg)
        elif self.callback is not None:
            self.callback(msg)

    def setFeedback(self, host, port, callback=None):
        if callback is not None:
            self.callback = callback
        self.robot_client.registerCallback(self._robotFeedback)
        self.robot_client.connectClient()
        self._prog_feedback_list = self._loadFeedbackRobot(host, port)

    def do(self, command, args):
        ''' e.g. robot.do("movej",([0,0,0,0,0,0,1],1,1))
        @param: command <str>
        @param: args <tuple>
        '''
        try:
            self.robot_server.sendCommand("{}{}".format(command, args))
        except:
            print("Syntax Error")

    def load(self, proglist):
        ''' list of istructions
        @param: proglist    <list> of <strings> '''
        try:
            self.robot_server.sendProgram(self._prog_feedback_list + proglist + ["join thrd"])
        except:
            print("Syntax Error")

    def closeall(self):
        self.robot_server.close()
        self.robot_client.close()

    def _loadFeedbackRobot(self, host, port):
        _prog = [

            'global feedback_data = 0',
            'global trigger = False',

            # Continuous feedback thread
            'thread feedbackThread():',
            # cycle to open socket
            'sock = False',
            'while sock == False:',
            'sock = socket_open(\"{}\",{},"socket_0")'.format(host, port),
            'sleep(0.01)',
            'end',  # end while
            # cycle to send the feedback
            'i = 0',
            'while True:',
            'if trigger:',
            # send
            'socket_send_int(feedback_data,"socket_0")',  # TODO: int, string, byte
            'trigger = False',
            'end',  # end if
            'sleep(0.01)',
            'i = i + 1',
            'end',  # end while
            # close socket
            'socket_close("socket_0")',
            'end',  # end thread

            # Callable feedback function
            'def feedback(data):',
            'feedback_data = data',
            'trigger = True',
            'end',

            ####

            "thrd = run feedbackThread()"
        ]
        return _prog
