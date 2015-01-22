#!/usr/bin/python2

from select import select
import re
import os
from sockets import *
from helpers import set_reflex

class IrcConnection(Socket):
    def __init__(self, host, nick, channels=[]):
        Socket.__init__(self, host, 6667)
        self.nick = nick
        self.user = (nick, 8, nick)
        for chan in channels:
            self.writeln("join %s" % chan)

    def join(self, channel):
        self.writeln("join " + chan)

    @set_reflex
    def nick(self, nick):
        self.writeln("nick " + nick)

    @set_reflex
    def user(self, args):
        self.writeln("user %s %s * :%s" % args)

def logmsg(prefix, channel, msg):
    with open(channel, 'a') as log:
        log.write("%s privmsg %s %s\n" % (prefix, channel, msg))

class IrcProxy(object):
    def add_client(socket):
        pass

    def remove_client(socket):
        pass


def main():
    def wait_for_work():
        select(clients + irc_servers + [incomming], sending_clients, [])

    def get_incomming():
        return select([incomming], [], [], 0)[0]

    def handle_upstream(socket):
        #service message? do stuff
        #else send to logger
        pass

    def handle_downstream(socket):
        #send to server and send to logger
        pass

    incomming = ListenerSocket('localhost', 9876)
    
    #os.chdir(os.path.expanduser("~/irclogs"))
    # Set up the irc connection
    irc_servers = [IrcConnection("irc.freenode.net", "teleirctester")]
    #irc.join("##teleirc-testing")
    
    clients = []
    while True:
        wait_for_work()

        for socket in get_incomming():
            connection = socket.accept()
            clients.append(connection)

        for socket in select([irc], [], [], 0)[0]:
            if socket.hasln():
                handle_upstream(socket)

        read_ready, write_ready, _ = select(clients, sending_clients, [], 0)

        for socket in read_ready:
            had_data = socket.transport_in()
            if not had_data:
                socket.close()
                clients.remove(socket)

            if socket.hasln():
                handle_downstream(socket)

        for socket in write_ready:
            socket.transport_out()

        sending_clients = filter(Socket.is_sending, clients)
        
        
if __name__ == '__main__':
    main()
