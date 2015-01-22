#!/usr/bin/python2

import socket

class Socket(socket.socket):
    linesep = '\n'

    def __init__(self, host, port):
        socket.socket.__init__(self)
        self.connect((host, port))
        self._postinit()

    def _postinit(self):
        self.setblocking(0)
        self.send_buffer = bytearray()
        self.recive_buffer = bytearray()

    @staticmethod
    def from_accept(accept_return):
        (old_socket, address) = accept_return
        socket = Socket.__new__(Socket)

        for field in old_socket.__slots__:
            if field.startswith('__'):
                   continue
            value = getattr(old_socket, field)
            setattr(socket, field, value)

        socket._postinit()
        return socket

    def write(self, data):
        self.send_buffer.extend(data)

    def writeln(self, line):
        ba = bytearray(line)
        ba.extend(self.linesep)
        self.write(ba)

    def hasln(self):
        return '\n' in self.recive_buffer
    
    def readln(self):
        line_sep = self.recive_buffer.find('\n')
        line = self.recive_buffer[:line_sep]
        line = line.strip('\r')
        del self.recive_buffer[:line_sep +1]
        return str(line)

    def transport_in(self):
        try: incomming = self.recv(1024)
        except socket.error: return
        self.recive_buffer.extend(incomming)
        return len(incomming) != 0
    
    def is_sending(self):
        return len(self.send_buffer) != 0
    
    def transport_out(self):
        sent_len = self.send(self.send_buffer)
        del self.send_buffer[:sent_len]

class ListenerSocket(socket.socket):
    def __init__(self, bind_addr, port):
        socket.socket.__init__(self)
        # set socket-level option reuseaddr to true
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.bind((bind_addr, port))
        self.listen(5)

    def accept(self):
        socket = super(ListenerSocket, self).accept()
        socket = Socket.from_accept(socket)
        return socket

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
