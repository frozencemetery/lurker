import random
import re
import select
import socket
# yeah we do want both
import thread
import threading
import time

import ircutil
from ircutil import UncasedDict, IrcSender, wrap, IrcError

debug = ircutil.debug
verbose = ircutil.verbose
warn = ircutil.warn
prnt = ircutil.prnt

MESSAGE = re.compile(ircutil.MESSAGE)
PARAMGRP = re.compile(ircutil.PARAMGRP)
PREFIXGRP = re.compile(ircutil.PREFIXGRP)
SPACE = re.compile(ircutil.SPACE)
NICK = re.compile(ircutil.NICK)

ssl_enabled = False
try:
    import ssl
except ImportError:
    warn("Couldn't import SSL library -- no SSL support will be provided")
    pass
else:
    ssl_enabled = True
    pass

# interface for listeners
class IrcListener(object):
    # called when the owner is created
    def on_start(self, owner):
        pass

    # called once we are connected to the irc server
    def on_connect(self, owner):
        pass

    # called when we can start doing things like join channel
    def on_register(self, owner):
        pass

    # called when a channel we in has a mode change
    def on_chan_mode(self, owner, sender, channel, mode):
        pass

    # called when someone sends a message to a channel we're in
    def on_chan_msg(self, owner, sender, channel, message, isact):
        pass

    # called when someone joins a channel
    def on_join(self, owner, sender, channel):
        pass

    # called when someone sends us a notice
    def on_notice(self, owner, sender, recipient, message):
        pass

    # any command that has a ### identifier (RPL_foo, ERR_foo, etc)
    def on_numeric_cmd(self, owner, sender, command, params):
        pass

    # called when we get a ping
    def on_ping(self, owner, sender, contents):
        pass

    # called when someone sends us a private message
    def on_priv_msg(self, owner, sender, message, isact):
        pass

    # called after we've registered with NICK and USER
    def on_register(self, owner):
        pass

    # called when the server sets our mode to something
    def on_user_mode(self, owner, sender, mode):
        pass

    # called when someone changes their nick
    def on_nick(self, owner, sender, newnick):
        pass

    # called when someone changes a channel topic
    def on_topic(self, owner, sender, channel, topic):
        pass

    # called when someone leaves a channel
    def on_part(self, owner, sender, channel, message):
        pass

    # called when someone quits a server
    def on_quit(self, owner, sender, message):
        pass

    # called when the server times out
    def on_err(self):
        pass
    pass

class BasicBehavior(IrcListener):
    def __init__(self, autochannels=["#lurkertest"]):
        # each element of autochannel should be a string name, or a 2-tuple of
        # a name and password
        self.autochannels = autochannels
        pass

    def on_register(self, owner):
        for channel in self.autochannels:
            if type(channel) == str:
                owner.send.join(channel)
                pass
            else:
                owner.send.join(*channel) # unpacks arguments
                pass
            pass
        pass

# manages all reads in a single non-blocking thread
class SocketManager(threading.Thread):
    def __init__(self):
        self.sockets = {} # keys = sockets, vals = f()
        self.queue = [] # keyval pairs
        self.delqueue = [] # sockets to be removed
        self.disconnect = False
        threading.Thread.__init__(self)
        pass

    def run(self):
        while True:
            readable, writable, error = select.select(
                self.sockets.keys(), [], self.sockets.keys(), 1)
            for sock in readable:
                self.sockets[sock]()
                pass
            for sock in error:
                self.sockets[sock]()
                pass
            while len(self.queue) > 0:
                self.sockets[self.queue[0][0]] = self.queue[0][1]
                self.queue = self.queue[1:]
                pass
            while len(self.delqueue) > 0:
                sock = self.delqueue[0]
                self.delqueue = self.delqueue[1:]
                if sock in self.sockets.keys():
                    del(self.sockets[sock])
                    pass
                pass
            if self.disconnect:
                return
            pass
        pass

    @classmethod
    def add(cls, sock, act):
        self = cls.singleton()
        self.queue.append([sock,act])
        pass

    @classmethod
    def remove(cls, sock):
        self = cls.singleton()
        self.delqueue.append(sock)
        pass

    @classmethod
    def exit(cls):
        cls.singleton().disconnect = True
        pass

    @classmethod
    def singleton(cls):
        try:
            return cls._singleton
        except:
            cls._singleton = cls()
            cls._singleton.start()
            return cls._singleton
        pass

class PingDetector(threading.Thread):
    def __init__(self, connection):
        self.connection = connection
        threading.Thread.__init__(self)
        pass

    def run(self):
        while True:
            time.sleep(300)
            ping_str = "PD" + str(random.randrange(10,10000000))
            try:
                if self.connection.connected:
                    if self.connection.last_recv > (time.time() - 9):
                        continue
                    self.connection.send.ping(ping_str)
                else:
                    prnt("[PD] Client not connected yet, waiting")
                    continue
                pass
            except Exception as e:
                prnt("[PD] Error while pinging! Reconnecting (%s)" % e)
                self.connection.disconnect()
                self.connection.reconnect_attempt()
                pass
            time.sleep(30)
            if self.connection.last_pong != ping_str:
                prnt("[PD] Pingout (sent = %s, recvd = %s)! Reconnecting" %
                     (ping_str, self.connection.last_pong))
                self.connection.disconnect()
                self.connection.reconnect_attempt()
                pass
            pass
        pass
    pass

RECONNECT_DELAY = 15
# represents a connection to a single irc server. attach classes which
# implement IrcListener to make it do a thing
class IrcConnection(IrcListener):
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
    use_ssl = False
    reconnect_delay = 0

    def __init__(self, server, port, nick="lurker", user="lurker",
                 realname="Helper P. Lurkington", use_ssl=False):
        global ssl_enabled
        self.server = server
        self.port = port
        self.nick = nick
        self.user = user
        self.realname = realname
        self.connected = False
        self.registered = False
        self.use_ssl = use_ssl
        self.reconnect_delay = RECONNECT_DELAY
        self.last_recv = 0
        self.last_pong = ""
        if use_ssl and not ssl_enabled:
            warn(("No SSL support, but it was requested for sever {0}:{1}! "
                  "Proceeding with no SSL").format(server, port))
            pass

        self.initialize_sender()
        self.initialize_listeners()
        self.add_listener(self)
        self.pinger = PingDetector(self)
        self.pinger.daemon = True
        self.pinger.start()
        pass

    # make new listener queues
    def initialize_listeners(self):
        self.Listeners = []
        pass

    # make the send object
    def initialize_sender(self):
        self.send = IrcSender(self)
        send = self.send
        send.raw = (lambda msg: self.socket.send(msg + '\r\n'))
        send.multi = (lambda *args:
                      send.raw(" ".join(str(arg) for arg in args)))
        send.pong = (lambda cnt: send.multi("PONG",":"+cnt))
        send.ping = (lambda cnt: send.multi("PING",":"+cnt))
        send.privmsg = (lambda dst, msg: send.multi("PRIVMSG",dst,":"+msg))
        send.action = (lambda dst, act:
                       send.privmsg(dst,ircutil.toaction(act)))
        send.user = (lambda usr, mode, realname:
                     send.multi("USER",usr,mode,"*",":"+realname))
        send.nick = (lambda nick: send.multi("NICK",nick))
        send.join = (lambda chan, pw="": send.multi("JOIN",chan,pw))
        pass

    def disconnect(self):
        # exit gracefully TODO
        prnt("== Disconnecting from remote server %s..." % self.server)
        SocketManager.remove(self.socket)
        self._disconnect = True
        self.connected = False
        self.registered = False
        self.socket.close()
        prnt("== Disconnected. Socket closed.")
        pass

    def begin_reconnect(self):
        thread.start_new_thread(self.reconnect_attempt, ())
        pass

    def reconnect_attempt(self):
        time.sleep(self.reconnect_delay)
        self.reconnect_delay *= 2
        if self.reconnect_delay > 15 * 60:
            self.reconnect_delay = 15 * 60
        prnt("== Attempting reconnect")
        self.connect()
        pass

    def connect(self):
        global ssl_enabled
        verbose("Calling on_start")
        for l in self.Listeners : wrap(l.on_start,self)
        prnt("== Connecting to remote server %s:%s..." %
             (self.server, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.use_ssl and ssl_enabled:
            self.socket = ssl.wrap_socket(self.socket)
            # ca_certs="/etc/ssl/certs/ca-certificates.crt",
            # cert_reqs=ssl.CERT_REQUIRED)
            # Once I understand what's going wrong with the cert
            # verification, I'll uncomment these lines
            pass
        try:
            self.socket.connect((self.server, self.port))
            pass
        except Exception as e :
            prnt("== Exception connecting to irc; retry in %d seconds: %s" %
                 (self.reconnect_delay, e))
            self.begin_reconnect()
            return
        prnt("== Connection successful.")
        self.reconnect_delay = RECONNECT_DELAY
        self.start_recv_loop()
        pass

    # continually read lines until we get a newline.
    def start_recv_loop(self):
        self.line_buffer = ""
        SocketManager.add(self.socket, self.on_recv)
        pass

    # actually called on a recv or an error
    def on_recv(self):
        try:
            buff = self.socket.recv(256)
            if buff == '':
                # empty == some kind of error, probably die
                prnt("No data from server; attempting reconnect")
                self.disconnect()
                self.begin_reconnect()
                return
            self.line_buffer += buff
            pass
        except Exception as e:
            prnt("Error recieving data; attempting reconnect: %s" % e)
            self.disconnect()
            self.begin_reconnect()
            return
        self.last_recv = time.time()
        lines = self.line_buffer.split('\r\n')
        for line in lines[:-1]:
            try:
                self.interpret_line(line + '\r\n')
                pass
            except IrcError as ie:
                warn("Caught",ie)
                pass
            pass
        self.line_buffer = lines[-1]
        pass

    # given a line, parse it into major tokens and process it, or throw an
    # exception
    def interpret_line(self, line):
        line_match = re.match(MESSAGE, line)
        if line_match:
            prefix, command, params = line_match.groups()
            try:
                self.process_command(command, prefix, params)
                pass
            except IrcError as ie:
                raise ie
            except Exception as e: 
                raise IrcError(e)
            pass
        else:
            raise IrcError("Invalid line: " + line)
        pass

    # evaluate a command. note that params begins with a space
    def process_command(self,command, prefix, params):
        if not(self.connected):
            self.connected = True
            verbose("Calling on_connect")
            for l in self.Listeners:
                wrap(l.on_connect, self)
                pass
            pass

        debug("Command:",command,"Prefix:",prefix,"Params",params)
        paramgroups = re.match(PARAMGRP, params).groups()
        paramlist = []
        if not(paramgroups[0] == None):
            paramlist.extend(re.split(SPACE, paramgroups[0])[:-1])
            pass
        if not(paramgroups[1] == None):
            paramlist.append(paramgroups[1])
            pass
        if not(paramgroups[2] == None):
            paramlist.append(paramgroups[2])
            pass
        debug("Parameters:", ", ".join(str(p) for p in paramlist))

        if prefix == None:
            server, nick, user, host = None, None, None, None
            sender = ()
            pass
        else:
            server, nick, user, host = re.match(PREFIXGRP,prefix).groups()
            if server == None:
                sender = (nick, user, host)
                pass
            else:
                sender = (server,)
                pass
            pass

        verbose("Command:", command)
        if command.isdigit():
            for l in self.Listeners:
                wrap(l.on_numeric_cmd, self, sender, int(command), paramlist)
                pass
            pass

        elif command.lower() == "privmsg":
            isact = ircutil.isaction(paramlist[1])
            # either a channel OR personal message
            if re.match(NICK, paramlist[0]):
                for l in self.Listeners:
                    wrap(l.on_priv_msg, self, sender,
                         ircutil.unaction(paramlist[1]), isact)
                    pass
                pass
            else:
                for l in self.Listeners:
                    wrap(l.on_chan_msg, self, sender, paramlist[0],
                         ircutil.unaction(paramlist[1]), isact)
                    pass
                pass
            pass
        elif command.lower() == "mode":
            # either a channel OR user mode
            if re.match(NICK, paramlist[0]):
                if not(self.registered ):
                    self.registered = True
                    debug("Calling on_register")
                    for l in self.Listeners:
                        wrap(l.on_register, self)
                        pass
                    pass
                for l in self.Listeners:
                    wrap(l.on_user_mode, self, sender, paramlist[1])
                    pass
                pass
            else:
                for l in self.Listeners:
                    wrap(l.on_chan_mode, self, sender, paramlist[0],
                         paramlist[1])
                    pass
                pass
            pass
        elif command.lower() == "notice":
            for l in self.Listeners:
                wrap(l.on_notice, self, sender, paramlist[0], paramlist[1])
                pass
            pass
        elif command.lower() == "ping":
            for l in self.Listeners:
                wrap(l.on_ping, self, sender, paramlist[0])
                pass
            pass
        elif command.lower() == "join":
            for l in self.Listeners:
                wrap(l.on_join, self, sender, paramlist[0])
                pass
            pass
        elif command.lower() == "part":
            message = ""
            if len(paramlist) > 1:
                message = paramlist[1]
                pass
            for l in self.Listeners:
                wrap(l.on_part, self, sender, paramlist[0], message)
                pass
            pass
        elif command.lower() == "quit":
            message = ""
            if len(paramlist) > 0:
                message = paramlist[0]
                pass
            for l in self.Listeners:
                wrap(l.on_quit, self, sender, message)
                pass
            pass
        elif command.lower() == "pong":
            self.last_pong = paramlist[1]
            pass
        elif command.lower() == "nick":
            if len(paramlist) > 0:
                message = paramlist[0]
                for l in self.Listeners:
                    wrap(l.on_nick, self, sender, message)
                    pass
                pass
            pass
        elif command.lower() == "topic":
            if len(paramlist) > 1:
                channel = paramlist[0]
                topic = paramlist[1]
                for l in self.Listeners:
                    wrap(l.on_topic, self, sender, channel, topic)
                    pass
                pass
            pass
        else:
            raise IrcError("Unknown command: " + str(command))
        pass

    def add_listener(self, listener):
        assert(issubclass(type(listener),IrcListener))
        self.Listeners.append(listener)
        pass

    def on_connect(self, owner):
        owner.send.user(self.user, 0, self.realname)
        owner.send.nick(self.nick)
        pass

    def on_ping(self, owner, sender, contents):
        owner.send.pong(contents)
        pass

    def on_err(self):
        self.disconnect()
        self.begin_reconnect()
        pass
    pass

def set_debug(val):
    ircutil.__DEBUG = val
    pass

def set_verbose(val):
    ircutil.__VERBOSE = val
    pass

def set_warn(val):
    ircutil.__WARN = val
    pass

def set_silent(val):
    ircutil.__SILENT = val
    pass
