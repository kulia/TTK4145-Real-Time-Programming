from mysocket import Socket, ListenerSocket
from select import select
import sys

server_address = ('localhost', 10000)

class Elevator(Socket):
	def __init__():
		self.busy = False

	@staticmethod
	def from_socket(socket):
		socket.__class__ = Elevator
		return Elevator.__init__(socket)

class ElevatorListener(ListenerSocket):
	def accept(self):
		socket = ListenerSocket.accept(self)
		elevator = Elevator.from_socket(socket)
		return elevator

elevators = []

def handle_elevator_msg(elevator):
	# recieved a line from an elevator
	print(elevator.readln())

def main():
	def wait_for_work():
		select(elevators + [listener], sending_sockets, [])

	def get_incomming():
		return select([listener], [], [], 0)[0]

	def get_readable():
		return select(elevators, [], [], 0)[0]

	def get_writeable():
		return select([], sending_sockets, [], 0)[1]

	listener = ElevatorListener(*server_address)

	sending_sockets = []

	while True:
		wait_for_work()

		for socket in get_incomming():
			connection = socket.accept()
			elevators.append(connection)

		for socket in get_readable():
			had_data = socket.transport_in()
			if not had_data:
				socket.close()
				elevators.remove(socket)

			if socket.hasln():
				handle_elevator_msg(socket)

		for socket in get_writeable():
			socket.transport_out()

		sending_sockets = filter(Socket.is_sending, elevators)

if __name__ == '__main__':
	main()