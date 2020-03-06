import socket 	  		            #for all the server work 
import sys							#for input arguments
import signal				 	    #for keyboard interrupt handling
from urllib.parse import urlparse	#for validating url
import re

##
#	Projekt pre predmet IPK
#	akad. rok: 2019/2020
#	autor: Boboš Dominik (xbobos00)
##

#for keyboard interrupt
def SignalHandler(sig, frame):
	print('Server on PORT =', TCP_PORT, 'ended its session!')
	sys.exit(0)

def ValidIp(address):	#checks for valid IP
	if (isinstance(address, bytes)):
		address = address.decode('utf-8')
	try: 
		socket.inet_aton(address)	#IPv4 check
		return address
	except:
		try: 
			socket.inet_pton(socket.AF_INET6, address)	#IPv6 check
			return address
		except:
			return False

def ValidURL(address):	#checks for valid URL
	if (isinstance(address, str)):			#encoding string input
		address = address.encode('utf-8')
	url = urlparse(address.decode('utf-8'))
	url = url[2]							#second item is the wanted
	if (url == '' or url == ValidIp(url)):	#case when 'A' but IP was entered
		return False			#end connection
	return url 					#return url

def ValidAddress(address):	#checks for valid IP or URL
	if (isinstance(address, str)):			#encoding string input
		address = address.encode('utf-8')
	if (ValidIp(address.decode('utf-8')) == False):
		url = urlparse(address.decode('utf-8'))
		url = url[2]			
		if (url == ''):
			return False			#end connection
		return url 					#return url
	else:
		url = address.decode('utf-8')	
		return url 					#return IP

#for parsing and finding A or PTR type 
def AorPTR(data, bool_str):
	if (bool_str == False):					#decoding bytes input to string
		if (isinstance(data, bytes)):
			data = data.decode('utf-8')
	if (data.rfind('type') != -1):	#I have GET request
		if (data.find('A', 0, data.find('HTTP')) != -1):
			return data.rfind('type'), "A"
		elif (data.find('PTR',0, data.find('HTTP')) != -1):
			return data.rfind('type'), "PTR"
		else:
			return False, False
	elif (data.rfind(':') != -1):	#I have POST request
		if (re.search(r'[:\s]A$|[:\s*](A\s)$',data)):	#it could contain spaces	
			return data.rfind(':'), "A"
		elif (re.search(r'[:\s]PTR$|[:\s*](PTR\s)$',data)): #it could contain spaces
			return data.rfind(':'), "PTR"
		else:
			return False, False
	elif (data == ''):
		return 0, ''
	else:
		return False, False


#arguments parsing
if (len(sys.argv) == 2) and (sys.argv[1][4] == '='):
	str1 = sys.argv[1].split('=')[0]
	str2 = sys.argv[1].split('=')[1]
	if (str1 == 'PORT' and str2.isdigit() and (int(str2) >= 1024 and int(str2) <= 65535)):
		pass
	else:
		sys.stderr.write("ERROR: Wrong typed port. Port is a number from 1024 to 65535 \n")
		sys.exit(1)
else:
	sys.stderr.write("ERROR: Could not start server, TCP_PORT was not specified. Port is a number from 1024 to 65535 \n")
	sys.exit(1)


#server
TCP_IP = '127.0.0.1'    #localhost
TCP_PORT = int(str2)	#port from args
BUFFER_SIZE = 1024
#building up server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #AF_INET refers to the address family ipv4. The SOCK_STREAM means connection oriented TCP protocol.
s.bind((TCP_IP, TCP_PORT))
#infinite loop
while (True):
	signal.signal(signal.SIGINT, SignalHandler)	#waiting for control + c
	s.listen(1)	#waits for connection
	conn, addr = s.accept()
	print ("Connection from:" , conn)
	data = conn.recv(BUFFER_SIZE)	#recieving data
	http = data.find(b'HTTP')	#checks for http version
	http_end = data.find(b"\r",http)
	http = data[http:http_end].decode('utf-8')
	error_str = http + ' 400 Bad Request\r\n\r\n'

	#providing GET request
	if (data[:3] == b'GET'):
		if (data[4:12] != b'/resolve'):
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue
		try:
			data = data.split(b'?')		#GET a resolve v [0] others in [1]
		except ValueError:
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue

		if (len(data) == 2):
			try:
				url = data[1].split(b'&')	#url/ip is in [0] others in [1]
			except ValueError:
				conn.send(error_str.encode('utf-8'))
				conn.close()
				continue
		else:		# bad splitted data
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue

		colon_ind = 0
		req_type = ''
		if (len(url) == 2):
			colon_ind, req_type = AorPTR(url[1], False)

		if (len(url) == 2 and req_type == 'A'):	#type "A"
			url = ValidURL(url[0][5:])
			if (url == False):
				print("IP entered, but hostname was expected")
				conn.send(error_str.encode('utf-8'))	#400 Bad Request
				conn.close()
				continue
			try:
				ip = socket.gethostbyaddr(url)
			except:
				error_str = http + ' 404 Not Found\r\n\r\n'
				conn.send(error_str.encode('utf-8'))	#400 Bad Request
				conn.close()
				continue
			http_ver = http + " 200 OK\r\n\r\n"
			send_str = url + ":A=" + ip[2][0] + "\n"	
			conn.send(http_ver.encode('utf-8'))
			conn.sendall(send_str.encode('utf-8'))
			conn.close()	
		elif (len(url) == 2 and req_type == 'PTR'):	#type "PTR"
			url = ValidIp(url[0][5:])
			if (url == False):
				print("Hostname entered, but IP was expected")
				conn.send(error_str.encode('utf-8'))	#400 Bad Request
				conn.close()
				continue
			try:
				host = socket.gethostbyaddr(url)
			except:
				error_str = http + ' 404 Not Found\r\n\r\n'
				conn.send(error_str.encode('utf-8')) 
				conn.close()
				continue
			http_ver = http + " 200 OK\r\n\r\n"
			host = url + ":PTR=" + host[0] + "\n"
			conn.send(http_ver.encode('utf-8'))
			conn.sendall(host.encode('utf-8'))
			conn.close()
		elif (len(url) == 2):
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue
		else:
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue

	#providing POST request
	elif (data[:4] == b'POST'):
		if (data[5:15] != b'/dns-query'):
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue
		data = data.decode('utf-8')
		try:
			data = data.split('\n')
		except:
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue

		send_str = ''
		final_msg = ''
		print(len(data))
		if((data[7] == '' and len(data) == 8) or (data[7] == '' and data[8] == '' and len(data) == 9)):				#empty post
			http_ver = http + " 200 OK\r\n\r\n"
			conn.send(http_ver.encode('utf-8'))
			conn.close()
			continue

		err_check = 0;
		colon_ind = 0
		req_type = ''
		
		for x in range(7,len(data)):	#from index 7 to the rest are URLs/IPs
			colon_ind, req_type = AorPTR(data[x], True)
			if (req_type == 'A'):
				url = ValidURL(data[x][:colon_ind])
				if (url == False):
					err_check += 1	#just to specify error message
					print("IP entered, but hostname was expected")
					continue
				try:
					ip = socket.gethostbyaddr(url)
				except:
					err_check += 1
					continue	#not included to final response
				send_str = url + ":A=" + ip[2][0] + "\n"

			elif (req_type == 'PTR'):
				url = ValidIp(data[x][:colon_ind])
				if (url == False):
					err_check += 1	#just to specify error message
					print("Hostname entered, but IP was expected")
					continue
				try:
					host = socket.gethostbyaddr(url)
				except:
					err_check += 1
					continue	#not included to final response
				send_str = url + ":PTR=" + host[0] + "\n"			
			elif (colon_ind == 0 and req_type == ''):
				err_check +=1
				continue	
			else:
				err_check += 1	#just to specify error message
				continue
			final_msg += send_str

		if (err_check == len(data)-7):
			error_str = http + ' 404 Not Found\r\n\r\n'
			conn.send(error_str.encode('utf-8'))
			conn.close()
		else:
			http_ver = http + " 200 OK\r\n\r\n"
			conn.send(http_ver.encode('utf-8'))
			conn.sendall(final_msg.encode('utf-8'))
			conn.close()
	# neither of allowed requests
	else:
		error_str = http + ' 405 Method Not Allowed\r\n\r\n'
		conn.send(error_str.encode('utf-8'))
		conn.close()
