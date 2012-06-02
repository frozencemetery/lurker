import socket
import select
import ircutil
from ircutil import UncasedDict, IrcSender, wrap
import re
import threading
debug = ircutil.debug
verbose = ircutil.verbose
warn = ircutil.warn
prnt = ircutil.prnt
MESSAGE = re.compile(ircutil.MESSAGE)
PARAMGRP = re.compile(ircutil.PARAMGRP)
PREFIXGRP = re.compile(ircutil.PREFIXGRP)
SPACE = re.compile(ircutil.SPACE)
NICK = re.compile(ircutil.NICK)

# class for any kind of error we might run across
class IrcError(Exception) :
    def __init__(self, value) :
        self.value = value
    def __str__(self) :
        if issubclass(type(self.value),Exception) :
            return type(self.value).__name__+": " + str(self.value)
        else :
            return str(self.value)

# interface for listeners
class IrcListener(object) : 
    # called when the owner is created
    def on_start(self, owner) : 
        pass
    # called once we are connected to the irc server
    def on_connect(self, owner) :
        pass
    # called when we can start doing things like join channel
    def on_register(self, owner) :
        pass
    # called when a channel we in has a mode change
    def on_chan_mode(self, owner, sender, channel, mode) :
        pass
    # called when someone joins a channel
    def on_join(self, owner, sender, channel) :
        pass
    # called when someone sends us a notice
    def on_notice(self, owner, sender, recipient, message) :
        pass
    # any command that has a ### identifier (RPL_foo, ERR_foo, etc)
    def on_numeric_cmd(self, owner, sender, command, params) :
        pass
    # called when we get a ping
    def on_ping(self, owner, sender, contents) :
        pass
    # called when someone sends us a private message
    def on_priv_msg(self, owner, sender, recipient, message) :
        pass
    # called after we've registered with NICK and USER
    def on_register(self, owner) :
        pass
    # called when the server sets our mode to something
    def on_user_mode(self, owner, sender, mode) :
        pass
    
# manages all reads in a single non-blocking thread
class SocketManager(threading.Thread) :
    def __init__(self) :
        self.sockets = {} # keys = sockets, vals = f()
        self.queue = [] # keyval pairs
        self.delqueue = [] # sockets to be removed
        self.disconnect = False
        threading.Thread.__init__(self)

    def run(self) : 
        while True :
            readable, writable, error = select.select(self.sockets.keys(),[],[],0.1)
            for sock in readable :
                self.sockets[sock]()
            while len(self.queue) > 0 :
                self.sockets[self.queue[0][0]] = self.queue[0][1]
                self.queue = self.queue[1:]
            while len(self.delqueue) > 0 :
                sock = self.delqueue[0]
                self.delqueue = self.delqueue[1:]
                if sock in self.sockets.keys() :
                    del(self.sockets[sock])
            if self.disconnect : 
                return

    @classmethod
    def add(cls, sock, act) :
        self = cls.singleton()
        self.queue.append([sock,act])

    @classmethod
    def remove(cls, sock) :
        self = cls.singleton()
        self.delqueue.append(sock)
        
    @classmethod
    def exit(cls) : 
        cls.singleton().disconnect = True

    @classmethod
    def singleton(cls) :
        try : 
            return cls._singleton
        except :
            cls._singleton = cls()
            cls._singleton.start()
            return cls._singleton


# represents a connection to a single irc server. attach classes which 
#  implement IrcListener to make it do a thing
class IrcConnection(IrcListener) :
    # these are mostly only here to keep track of them in ctags, not for any 
    # functional purpose.
    server = ""
    port = 0
    user = ""
    nick = ""
    realname = ""
    connected = False
    registered = False
    Listeners = []
    socket = None
    send = None
    _disconnect = False
    
    def __init__(self, server, port, nick="lurker",\
            user="lurker", realname="Helper P. Lurkington") :
        self.server = server
        self.port = port
        self.nick = nick
        self.user = user
        self.realname = realname
        self.connected = False
        self.registered = False

        self.initialize_sender()
        self.initialize_listeners()
        self.add_listener(self)

    # make new listener queues
    def initialize_listeners(self) :
        self.Listeners = []

    # make the send object
    def initialize_sender(self) :
        self.send = IrcSender(self)
        send = self.send
        send.raw = lambda msg : self.socket.send(msg + '\r\n')
        send.multi = lambda *args : \
                     send.raw(" ".join(str(arg) for arg in args))
        send.pong = lambda cnt : \
                    send.multi("PONG",":"+cnt)
        send.privmsg = lambda dst, msg : \
                       send.multi("PRIVMSG",dst,":"+msg)
        send.action = lambda dst, act: \
                      send.privmsg(dst,chr(7)+"ACTION"+chr(7)+msg)
        send.user = lambda usr, mode, realname : \
                    send.multi("USER",usr,mode,"*",":"+realname)
        send.nick = lambda nick : \
                    send.multi("NICK",nick)
        send.join = lambda chan, pw="" :\
                    send.multi("JOIN",chan,pw)

    # disconnect
    def disconnect(self) :
        # exit gracefully TODO
        debug("Disconnecting...")
        SocketManager.remove(self.socket)
        self._disconnect = True
        self.socket.close()

    def connect(self) :
        verbose("Calling on_start")
        for l in self.Listeners : wrap(l.on_start,self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try : 
            self.socket.connect((self.server, self.port))
        except Error as e :
            raise IrcError(e)
        self.start_recv_loop()

    # continually read lines until we get a newline.
    def start_recv_loop(self) :
        self.line_buffer = ""
        SocketManager.add(self.socket, self.on_recv)

    def on_recv(self) :
        try :
            self.line_buffer += self.socket.recv(256)
        except Exception as e :
            raise IrcError(e)
        lines = self.line_buffer.split('\r\n')
        for line in lines[:-1] :
            try :
                self.interpret_line(line + '\r\n')
            except IrcError as ie :
                warn("Caught",ie)
        self.line_buffer = lines[-1]

    # given a line, parse it into major tokens and process it, or throw an
    #  exception
    def interpret_line(self, line) :
        line_match = re.match(MESSAGE, line)
        if line_match :
            prefix, command, params = line_match.groups()
            try : 
                self.process_command(command, prefix, params)
            except IrcError as ie : 
                raise ie
            except Exception as e: 
                raise IrcError(e)
        else :
            raise IrcError("Invalid line: " + line)
    
    # evaluate a command. note that params begins with a space
    def process_command(self,command, prefix, params) :
        if not(self.connected) :
            self.connected = True
            verbose("Calling on_connect")
            for l in self.Listeners : wrap(l.on_connect,self)

        debug("Command:",command,"Prefix:",prefix,"Params",params)
        paramgroups = re.match(PARAMGRP, params).groups()
        paramlist = []
        if not(paramgroups[0] == None) : 
            paramlist.extend(re.split(SPACE,paramgroups[0])[:-1])
        if not(paramgroups[1] == None) :
            paramlist.append(paramgroups[1])
        debug("Parameters:",", ".join(str(p) for p in paramlist))

        if prefix == None : 
            server, nick, user, host = None, None, None, None
            sender = ()
        else :
            server, nick, user, host = re.match(PREFIXGRP,prefix).groups()
            if server == None :
                sender = (nick, user, host)
            else :
                sender = (server,)
        
        verbose("Command:",command)
        if command.isdigit() :
            for l in self.Listeners : wrap(l.on_numeric_cmd,\
                    self, sender, int(command), paramlist)
        elif command.lower() == "privmsg" :
            for l in self.Listeners : wrap(l.on_priv_msg,\
                    self, sender, paramlist[0], paramlist[1])
        elif command.lower() == "mode" : 
            # either a channel OR user mode
            if re.match(NICK, paramlist[0]) :
                if not(self.registered ) :
                    self.registered = True
                    debug("Calling on_register")
                    for l in self.Listeners : wrap(l.on_register,\
                            self)
                for l in self.Listeners : wrap(l.on_user_mode,\
                        self, sender, paramlist[1])
            else :
                for l in self.Listeners : wrap(l.on_chan_mode,\
                        self, sender, paramlist[0], paramlist[1])
        elif command.lower() == "notice" :
            for l in self.Listeners : wrap(l.on_notice,\
                    self, sender, paramlist[0], paramlist[1])
        elif command.lower() == "ping" :
            for l in self.Listeners : wrap(l.on_ping,\
                    self, sender, paramlist[0])
        elif command.lower() == "join" :
            for l in self.Listeners : wrap(l.on_join,\
                    self, sender, paramlist[0])
        else :
            raise IrcError("Unknown command: " + str(command))

    def add_listener(self, listener) :
        assert(issubclass(type(listener),IrcListener))
        self.Listeners.append(listener)

    # TODO: Move all these to "BasicBehavior"
    def on_connect(self, owner) :
        owner.send.user(self.user, 0, self.realname)
        owner.send.nick(self.nick)

    def on_ping(self, owner, sender, contents) :
        owner.send.pong(contents)

    def on_register(self, owner) :
        owner.send.join("#lurkertest")

def set_debug(val): 
    ircutil.__DEBUG = val

def set_verbose(val) :
    ircutil.__VERBOSE = val

def set_warn(val) : 
    ircutil.__WARN = val

def set_silent(val) :
    ircutil.__SILENT = val

# Default: if this was run on its own, connect to foonetic.net
if __name__ == "__main__" :
    set_verbose(True)
    set_debug(True)
    set_warn(True)
    conn = IrcConnection("irc.foonetic.net",6667,nick="lurker3",user="lurker3")
    conn.connect()
    stop = False
    raw_input()
    conn.disconnect()
    SocketManager.exit()
