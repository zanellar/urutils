import time
import socket
import threading


class RobotIOProxy(object):

    EOC = "\n"

    def __init__(self, hostip, port):
        self.ip = hostip
        self.port = port

        # Open connection to robot
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.ip, self.port))
        self.socket.listen(1)

        # Variables
        self.client_socket = None
        self.callback = None
        self.last_message = None
        self.message_thread = None

    def _waitMessage(self):
        print("Connecting to client ...")
        client_socket, addr = self.socket.accept()
        print("Connected! ({}, {})".format(self.ip, self.port))
        while self.message_thread.isAlive():
            # print("Waiting for message...")
            self.last_message = client_socket.recv(1024)
            # print("Received:", self.last_message)
            time.sleep(0.001)       # BUG required ???????????????????????
            try:
                if self.callback is not None:
                    self.callback(self.last_message)
            except Exception as e:
                print(e)

    def sendData(self, datastr, ack=True):
        if self.client_socket is None:
            print("Connecting to client ...")
            self.client_socket, addr = self.socket.accept()

        print("Sending ...", datastr)
        self.client_socket.send(bytes(datastr, 'utf-8'))

    def registerCallback(self, callback):
        self.callback = callback

    def connectClient(self):
        self.message_thread = threading.Thread(
            target=self._waitMessage
        )
        self.message_thread.start()

    def close(self):
        self.socket.close()
        if self.client_socket is not None:
            self.client_socket.close()
        if self.message_thread is not None:
            self.message_thread.join()

##############################################################################################
##############################################################################################
##############################################################################################


class RobotCommandProxy(object):

    EOC = "\n"

    def __init__(self, robotip, port):
        self.ip = robotip
        self.port = port

        # Open connection to robot
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.connect((self.ip, self.port))
        except:
            print("NO connection ({}, {})".format(self.ip, port))
        else:
            print("Connected! ({}, {})".format(self.ip, port))

        # Variables
        self.is_ready = True

    def sendCommand(self, cmd_str, ack=False):
        self.is_ready = False
        print("sending...", cmd_str)

        # Format command
        command = cmd_str + RobotCommandProxy.EOC

        # Send command
        self.socket.send(command.encode())

        res = self.socket.recv(1024)
        self.is_ready = True

        if ack:
            print("Received", repr(res))

    def sendProgram(self, prg_list, ack=True):
        prg_str = "def myProg():" + RobotCommandProxy.EOC
        identspace = " "
        for line in prg_list:
            prg_str += identspace + line + RobotCommandProxy.EOC
        prg_str = prg_str + "end" + RobotCommandProxy.EOC
        self.sendCommand(prg_str, ack=ack)

    def close(self):
        # Close connection to robot
        self.socket.close()


##############################################################################################
##############################################################################################
##############################################################################################

class URProxy(object):

    def __init__(self, robotip):
        self.robot_command_client = RobotCommandProxy(
            robotip=robotip,  # "192.168.7.235" - robot ip
            port=30002  # 30002 - deticated port for istructions
        )
        self.robot_output_server = None
        self.robot_input_server = None
        self.robotoutput = None
        self.callback = None
        self._prog_output_script = None
        self._prog_input_script = None

    def _robotOutput(self, msg, callback=None):
        self.robotoutput = msg
        if callback is not None:
            callback(msg)
        elif self.callback is not None:
            self.callback(msg)

    def setOutputProxy(self, hostip,  port=55555, callback=None, preloadscript=False, datadef=[]):
        self.robot_output_server = RobotIOProxy(
            hostip="0.0.0.0",
            port=port
        )
        if callback is not None:
            self.callback = callback
        self.robot_output_server.registerCallback(self._robotOutput)
        self.robot_output_server.connectClient()
        if preloadscript:
            self._prog_output_script = self._loadDataDef("output_data", datadef) + self._loadOutputScript(hostip, port)

    def setInputProxy(self, hostip, port=4000,  preloadscript=False,  n_inputs=1, datadef=[]):
        self.robot_input_server = RobotIOProxy(
            hostip=hostip,
            port=port
        )
        if preloadscript:
            self._prog_input_script = self._loadInputScript(hostip, port, n_inputs)

    def input(self, data):
        if type(data) is str:
            try:
                self.robot_input_server.sendData(data)
            except Exception as e:
                print(e)
        else:
            print("ERROR: Input data must be string-type")

    def do(self, command, args, ack=True):
        ''' e.g. robot.do("movej",([q1,q2,q3,q4,a5,a6],0.5,0.5)) # joint space
            e.g. robot.do("movel",([x,y,z,rx,ry,rz],0.5,0.25)) # cartesian space
        @param: command <str>
        @param: args <tuple>
        '''
        try:
            if command == "movel":
                # convert the argument pose (list) in format "p[x,y,z,rx,ry,rz]"
                # and concatenate with the others arguments in a string
                args_str = ['p{}'.format(args[0])]
                for x in list(args[1:]):
                    args_str.append(x)
                args = "({})".format(",".join(map(str, args_str)))

            self.robot_command_client.sendCommand("{}{}".format(command, args), ack=ack)
        except:
            print("Syntax Error")

    def load(self, proglist=[]):
        ''' list of istructions. If empy will be loaded only the threads for input/output comunication
        @param: proglist    <list> of <strings> '''
        try:
            if self._prog_input_script is not None:
                print("loading prog_input_script")
                proglist = self._prog_input_script + proglist  # + ["join thrd_input"]
            if self._prog_output_script is not None:
                print("loading prog_output_script")
                proglist = self._prog_output_script + proglist  # + ["join thrd_output"]

            self.robot_command_client.sendProgram(proglist)
        except:
            print("Syntax Error")

    def closeall(self):
        if self.robot_input_server is not None:
            self.robot_input_server.close()
        if self.robot_command_client is not None:
            self.robot_command_client.close()
        if self.robot_output_server is not None:
            self.robot_output_server .close()

    def _loadDataDef(self, varname, datadef):
        _prog = [
            'global {} = {}'.format(varname, datadef)
        ]
        return _prog

    def _loadInputScript(self, ip, port, n_inputs):
        _prog = [
            'global input_data = {}'.format([0.0]*(n_inputs+1)),
            ########################################
            # Continuous input thread
            ########################################
            'thread inputThread():',
            # cycle to open socket
            'sockInflg = False',
            'while sockInflg == False:',
            'sockInflg = socket_open(\"{}\",{},"socket_input")'.format(ip, port),
            'sleep(0.01)',
            'end',  # end while
            # cycle to receive the input
            'while True:',
            'input_data = socket_read_ascii_float({}, "socket_input",1)'.format(n_inputs),
            'sleep(0.000001)',
            'end',   # end while
            # close socket
            'socket_close("socket_input")',
            'end',  # end thread

            ########################################

            "thrd_input = run inputThread()"
        ]
        return _prog

    def _loadOutputScript(self, ip, port):
        _prog = [

            'global trigger_output = False',

            ########################################
            # Continuous output thread
            ########################################
            'thread outputThread():',
            # cycle to open socket
            'sockOutflg = False',
            'while sockOutflg == False:',
            'sockOutflg = socket_open(\"{}\",{},"socket_output")'.format(ip, port),
            'sleep(0.01)',
            'end',  # end while
            # cycle to send the output
            'i = 0',
            'while True:',
            'if trigger_output:',
            # send
            'trigger_output = False',
            'socket_send_string(output_data,"socket_output")',  # TODO: int, string, byte
            'end',  # end if
            'sleep(0.01)',
            'i = i + 1',
            'end',  # end while
            # close socket
            'socket_close("socket_output")',
            'end',  # end thread

            ########################################
            "thrd_output = run outputThread()"

            ########################################
            # Callable output function
            ########################################
            'def output(data):',
            'output_data = data',
            'trigger_output = True',
            'end',

        ]
        return _prog
