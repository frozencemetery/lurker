import socket
import ircutil
import re

MESSAGE = re.compile(ircutil.MESSAGE)

# class for any kind of error we might run across
class IrcError(Exception) :
    def __init__(self, value) :
        self.value = value

    def __str__(self) :
        return repr(self.value)

# interface for listeners
class IrcListener(object) : 
    # called when someone sends us a private message
    def on_priv_msg(self, sender, recipient, message) :
        pass

# represents a connection to a single irc server. attach classes which 
#  implement IrcListener to make it do a thing
class IrcConnection(IrcListener) :
    
    def __init__(self, server, port, nick="lurker",\
            realname="Helper P. Lurkington") :
        self.server = server
        self.port = port
        self.nick = nick
        self.realname = realname

        self.initialize_listeners()
        self.add_listener(self)

    # make new listener queues
    def initialize_listeners(self) :
        self.OnMsg = []

    # connect to the specified server
    def connect(self) :
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try : 
            self.socket.connect((self.server, self.port))
        except Error as e :
            raise IrcError(e)
        self.start_recv_loop()

    # continually read lines until we get a newline.
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

    # given a line, parse it into major tokens and process it, or throw an
    #  exception
    def interpret_line(self, line) :
        line_match = re.match(MESSAGE, line)
        if line_match :
            prefix, command, params = line_match.groups()
            self.process_command(command, prefix, params)
        else :
            raise IrcError("Invalid line: " + line)
    
    # evaluate a command. note that params begins with a space
    def process_command(self,command, prefix, params) :
        print "Command:",command,"Prefix:",prefix,"Params",params

    def add_listener(self, listener) :
        assert(issubclass(type(listener),IrcListener))
        self.OnMsg += listener

# Default: if this was run on its own, connect to foonetic.net
if __name__ == "__main__" :
    conn = IrcConnection("irc.foonetic.net",6667)
    conn.connect()

