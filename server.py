#!/usr/bin/python          

import socket              
import sys
import threading as thread
import time
import signal
import os

class Client:
	def __init__(self,socket,name,password):
		self.socket = socket;
		self.name = name;
		self.password = password;
		self.blocked_clients = [];
		self.failed_count = 0;
		self.connected = False;
		self.pending_msg=[];
		self.address = None;
		self.activetime = None;
	def failed_connect(self,address):
		self.failed_count+=1;	
		if(self.failed_count > 3):
			socket.sendto('loginfailed Invalid Password. Your account has been blocked. Please try again later'.encode('utf-8'),address);
			print (block_time);
			thread.Timer(block_time, self.reset_fail).start();
		else:
			socket.sendto('loginfailed Invalid username/password'.encode('utf-8'),address);	
	def get_active_time(self):
		return self.activetime;
	def reset_fail(self):		
		self.failed_count = 0;
	def send_msg(self,msg):
		self.activetime = int(round(time.time() * 1000));
		if self.connected:	
			self.socket.sendto(msg.encode('utf-8'),self.address);
		else:
			self.add_pending_msg(msg);
	def send_pending_msg(self):
		for msg in self.pending_msg:
			self.send_msg(msg);
		self.pending_msg = [];
	def is_connected(self):
		return self.connected;
	def set_connected(self,value):
		self.connected = value;
	def block_client(self,c):
		self.blocked_clients.append(c);
	def get_blocked_clients(self):
		return self.blocked_clients;
	def unblock_client(self,c):
		self.blocked_clients.remove(c);
	def add_pending_msg(self,msg):
		self.pending_msg.append(msg);
	def set_address(self,address):
		self.address = address;
	def get_address(self):
		return self.address;
	def get_name(self):
		return self.name;
	def get_password(self):
		return self.password;
	def set_failed_count(self,count):
		self.failed_count = count;
	def get_failed_count(self):
		return self.failed_count;


class Client_pool:
	def __init__(self,socket,clients):
		self.clients = clients;
		self.socket = socket;
	def broadcast(self,msg,who):
		blocked = False;
		for client in self.clients:
			if not client == who :
				if not who in client.get_blocked_clients():			
					client.send_msg(msg);
				else:
					blocked = True;
		if blocked :
			who.send_msg('notify Your message could not be delivered to some recipients');
	def message(self,msg,to,from_):
		if to in self.clients:
			if from_ in to.get_blocked_clients():
				from_.send_msg('notify Your message could not be delivered as the '+to.get_name()+' has blocked you');
			else:
				to.send_msg(msg);
				if not to.is_connected():
					from_.send_msg('notify Your message will be delivered whenever '+to.get_name()+' logs in.');	
		else:
			from_.send_msg('notify Recipient does not exists');
	def is_authentic(self,username,password,address):
		for client in self.clients:
			if username == client.get_name():
				if client.is_connected():
					socket.sendto('loginfailed You are already connected'.encode('utf-8'),address);
					return False;
				if client.get_failed_count() <= 3:
					if password == client.get_password():
						client.set_connected(True);
						client.set_address(address);
						return True;
					else:
						client.failed_connect(address);
						return False;
				else:
					socket.sendto('loginfailed Your account is blocked due to multiple login failures. Please try again later'.encode('utf-8'),address);
					return False;
		socket.sendto(('loginfailed Invalid username/password').encode('utf-8'),address);
		return False;
	def disconnect(self,who):
		if who in self.clients:
			who.send_msg('logout You have been logged out');
			self.broadcast('notify '+who.get_name()+' logged out',self);
			who.set_connected(False);
	def get_client_addr(self,address):
		for client in self.clients:
			if client.get_address() == address:
				return client;		
		return None;
	
	def get_client_name(self,name):
		for client in self.clients:
			if client.get_name() == name:
				return client;		
		return None;
	def get_connected_clients_name(self,me):
		c = []
		for client in self.clients:
			if not client == me and client.is_connected():
				c.append(client.get_name());
		return c;	
	def check_activity(self):
		for client in self.clients:
			if client.is_connected() and client.activetime + timeout < int(round(time.time() * 1000)):
				self.disconnect(client);
				
def get_string(data):
	return ' '.join(data);	

def do_task(data,address):
	if not data[0] == 'login':
		me  = client_pool.get_client_addr(address);
		if len(data) > 1 :
			client = client_pool.get_client_name(data[1]);
			if client == None and not data[0] == 'broadcast':
				me.send_msg('notify Invalid client');
				return;
		else:
			me.send_msg('notify Error Invalid command');
			return;
	if data[0] == 'login':
		if client_pool.is_authentic(data[1],data[2],address):
			client = client_pool.get_client_name(data[1]);
			client.send_msg('login Welcome to the greatest messaging application ever!');
			client.send_pending_msg();
			client_pool.broadcast('notify '+data[1]+' just logged in',client);
	elif data[0] == 'whoelse':
		msg = 'notify ';		
		msg+= ' '.join(client_pool.get_connected_clients_name(me));
		me.send_msg(msg);
	elif data[0] == 'logout':
		client_pool.disconnect(client_pool.get_client_name(data[1]));
	elif data[0] == 'message':
		msg= 'notify '+me.get_name()+': '+get_string(data[2:len(data)]);
		client_pool.message(msg,client,me);
	elif data[0] == 'broadcast':
		msg= 'notify '+me.get_name()+': '+get_string(data[1:len(data)]);
		client_pool.broadcast(msg,me);
	elif data[0] == 'block':
		if data[1] == me.get_name():
			me.send_msg('notify Error cannot block self');
		else:
			me.block_client(client);
			me.send_msg('notify You have blocked '+client.get_name());
			client.send_msg('notify You have been blocked by '+me.get_name());
	elif data[0] == 'unblock':
		me.unblock_client(client);
		me.send_msg('notify You have unblocked '+client.get_name());
		client.send_msg('notify You have been unblocked by '+me.get_name());
	elif data[0] == 'startprivate':
		if client.is_connected():
			me.send_msg('addprivate '+client.get_name()+' '+client.get_address()[0]+' '+str(client.get_address()[1]));
			me.send_msg('notify Private started for '+client.get_name());
		else:
			me.send_msg('notify '+client.get_name()+' is not logged in');
	else:
		me.send_msg('notify Error Invalid command');
		return;

def handler(signum, frame):
	socket.close();
	close = True;
	
def listen_socket():
	while(True):
		try:
			data,address = socket.recvfrom(1024);
			data = data.decode('utf-8');
			data =	data.split(' ');
			do_task(data,address);
		except:
			close = True;
			os._exit(0);

def startServer(HOST,PORT):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
	server_address = (HOST, PORT)
	print ('Socket created');
	try:
		sock.bind(server_address)
	except socket.error as msg:
		print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]);
		sys.exit()
	print ('Socket bind completed');
	return sock;

def loadClients(socket):
	clients = [];
	with open('credentials.txt') as fp:
		for line in fp:
			data = line.strip().split(' ');
			client = Client(socket,data[0],data[1]);
			clients.append(client);
	return clients;

argv = sys.argv;
if len(argv) <= 4:
	print ('Argument missing');
	exit(0);
block_time = int(argv[3]);
timeout = int(argv[4]);
socket = startServer('0.0.0.0',int(argv[2]));
close = False;
client_pool = Client_pool(socket,loadClients(socket));

def check_activity():
	client_pool.check_activity();
	thread.Timer(timeout, check_activity).start();

print ('Press Ctrl+C to exit');
signal.signal(signal.SIGTSTP, handler)
check_activity();
listen_socket();


