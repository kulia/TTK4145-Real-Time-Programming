#!/usr/bin/python

from select import select
from sockets import *

def handle_clientmsg(client):
    line = client.readln()
    print("Handling line: %s" % line)

def main():
    def wait_for_work():
        select(clients + [listener], sending_sockets, [])

    def get_incomming():
        return select([listener], [], [], 0)[0]

    def get_readable():
        return select(clients, [], [], 0)[0]

    def get_writeable():
        return select([], sending_sockets, [], 0)[1]

    listener = ListenerSocket('localhost', 9876)
    
    clients = []
    sending_sockets = []

    while True:
        wait_for_work()

        for socket in get_incomming():
            connection = socket.accept()
            clients.append(connection)

        for socket in get_readable():
            had_data = socket.transport_in()
            print("Buffer content: %s" % socket.recive_buffer)
            if not had_data:
                socket.close()
                clients.remove(socket)

            if socket.hasln():
                handle_clientmsg(socket)

        for socket in get_writeable():
            socket.transport_out()

        sending_sockets = filter(Socket.is_sending, clients)
        
if __name__ == '__main__':
    main()
