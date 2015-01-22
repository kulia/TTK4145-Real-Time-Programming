from mysocket import Socket, ListenerSocket
from select import select
import sys
from random import choice

server_address = ('localhost', 10000)

class Elevator(Socket):
	def __init__(self):
		self.floor = None;
		self.dir = None;
		self.orders = set()
		

	@staticmethod
	def from_socket(socket):
		socket.__class__ = Elevator
		Elevator.__init__(socket)
		return socket

class ElevatorListener(ListenerSocket):
	def accept(self):
		socket = ListenerSocket.accept(self)
		elevator = Elevator.from_socket(socket)
		print "Elevator connected."
		return elevator

elevators = []

def request(floor, dir):
	msg = str(floor) + ' ' + dir
	for elevator in elevators:
		if (dir == 'up') and ( (elevator.dir == 'up') or (elevator.dir == 'idle') ) and (elevator.floor <= floor) :
			break
		elif (dir == 'down') and ( (elevator.dir == 'down') or (elevator.dir == 'idle') )  and (elevator.floor >= floor):
			break
	else:
		elevator = choice(elevators)

	elevator.writeln(msg)
	elevator.orders.add((floor, dir))
		

def handle_elevator(elevator):
	# recieved a line from an elevator
	msg = elevator.readln()
	print "Elevator " + str(elevators.index(elevator)) + ": " +msg
	msg = msg.split()
	floor = int(msg[1])
	dir = msg[2]

	if msg[0] == 'button':
		request(floor, dir)
	if msg[0] in ('stop', 'floor'):
		elevator.floor = floor
		elevator.dir = dir
	if msg[0] == 'stop':
		elevator.orders.discard((floor,dir)) 

def elevator_disconnect(elevator):
	for order in elevator.orders:
		print '\033[93m' "Redirect order." '\033[37m'
		request(*order)

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
				elevator_disconnect(socket)
				print '\033[93m' "Lost the connection to an elevator." '\033[37m'

			if socket.hasln():
				handle_elevator(socket)

		for socket in get_writeable():
			socket.transport_out()

		sending_sockets = filter(Socket.is_sending, elevators)


if __name__ == '__main__':
	main()