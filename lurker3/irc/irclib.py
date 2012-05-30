import socket
import ircutil
import re

MESSAGE = re.compile(ircutil.MESSAGE)
class IrcError(Exception) :
    def __init__(self, value) :
        self.value = value

    def __str__(self) :
        return repr(self.value)

class IrcListener : # interface
    def onPrivMsg(self, message, sender) :
        pass

    def onChanMsg(self, message, sender, channel) :
        pass

class IrcConnection(IrcListener) :
    
    def __init__(self, server, port, nick="lurker", realname="Helper P. Lurkington") :
        self.server = server
        self.port = port
        self.nick = nick
        self.realname = realname

        self.initialize_listeners()

    def initialize_listeners(self) :
        self.OnMsg = []

    def connect(self) :
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try : 
            self.socket.connect((self.server, self.port))
        except Error as e :
            raise IrcError(e)
        self.start_recv_loop()

    def start_recv_loop(self) :
        line_buffer = ""
        while True :
            try :
                line_buffer += self.socket.recv(256)
            except Exception as e :
                raise IrcError(e)
            lines = line_buffer.split('\r\n')
            for line in lines[:-1] :
                try :
                    self.interpret_line(line + '\r\n')
                except IrcError as ie :
                    print ie
            line_buffer = lines[-1]

    def interpret_line(self, line) :
        line_match = re.match(MESSAGE, line)
        if line_match :
            prefix, command, params = line_match.groups()
            self.process_command(command, prefix, params)
        else :
            raise IrcError("Invalid line: " + line)
    
    def process_command(self,command, prefix, params) :
        print "Command:",command,"Prefix:",prefix,"Params",params
