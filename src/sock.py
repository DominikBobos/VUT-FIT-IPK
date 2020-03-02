import socket 	  		            #for all the server work 
import sys							#for input arguments
from urllib.parse import urlparse	#for validating url

##
#	Projekt pre predmet IPK
#	akad. rok: 2019/2020
#	autor: Boboš Dominik (xbobos00)
##

def ValidIp(address):	#checks for valid IP
	if (isinstance(address, bytes)):
		address = address.decode('utf-8')
	try: 
		socket.inet_aton(address)
		return address
	except:
		try: 
			socket.inet_pton(socket.AF_INET6, address)
			return address
		except:
			return False

def ValidURL(address):	#checks for valid URL
	if (isinstance(address, str)):
		address = address.encode('utf-8')
	url = urlparse(address.decode('utf-8'))
	url = url[2]			
	if (url == '' or url == ValidIp(url)):	#case when 'A' but IP was entered
		return False			#end connection
	return url 					#return url

def ValidAddress(address):	#checks for valid IP or URL
	if (isinstance(address, str)):
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
	if (bool_str == False):
		if (isinstance(data, bytes)):
			print(data)
			data = data.decode('utf-8')
	if (data.rfind('type') != -1):	#I have GET
		if (data.find('A', 0, data.find('HTTP')) != -1):
			return data.rfind('type'), "A"
		elif (data.find('PTR',0, data.find('HTTP')) != -1):
			return data.rfind('type'), "PTR"
	elif (data.rfind(':') != -1):	#I have POST
		if (data.find('A',data.rfind(':')) != -1):
			return data.rfind(':'), "A"
		elif (data.find('PTR',data.rfind(':')) != -1):
			return data.rfind(':'), "PTR"
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
				conn.send(error_str.encode('utf-8'))
				conn.close()
				continue
			try:
				ip = socket.gethostbyaddr(url)
			except:
				error_str = http + ' 404 Not Found\r\n\r\n'
				conn.send(error_str.encode('utf-8'))
				conn.close()
				continue
			http_ver = http + " 200 OK\r\n\r\n"
			send_str = url + ":A=" + ip[2][0] + "\n"
			
			conn.send(http_ver.encode('utf-8'))
			conn.send(send_str.encode('utf-8'))
			conn.close()	
		elif (len(url) == 2 and req_type == 'PTR'):	#type "PTR"
			
			if (ValidIp(url[0][5:].decode('utf-8')) == False):
				print("Hostname entered, but IP was expected")
				conn.send(error_str.encode('utf-8'))
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
			conn.send(host.encode('utf-8'))
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
		if(data[7] == ''):				#empty post
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
					err_check = len(data)
					print("IP entered, but hostname was expected")
					break
				try:
					ip = socket.gethostbyaddr(url)
				except:
					err_check += 1
					continue	#not included to final response
				send_str = url + ":A=" + ip[2][0] + "\n"

			elif (req_type == 'PTR'):
				url = ValidIp(data[x][:colon_ind])
				if (url == False):
					err_check = len(data)
					print("Hostname entered, but IP was expected")
					break
				try:
					host = socket.gethostbyaddr(url)
				except:
					err_check += 1
					continue	#not included to final response
				send_str = url + ":PTR=" + host[0] + "\n"				
			else:
				conn.send(error_str.encode('utf-8'))
				conn.close()
				break
			final_msg += send_str

		if (err_check == len(data)-7 or err_check == len(data)):
			if (err_check == len(data)):
				conn.send(error_str.encode('utf-8'))
				conn.close()
			else:
				error_str = http + ' 404 Not Found\r\n\r\n'
				conn.send(error_str.encode('utf-8'))
				conn.close()
		else:
			http_ver = http + " 200 OK\r\n\r\n"
			conn.send(http_ver.encode('utf-8'))
			conn.send(final_msg.encode('utf-8'))
			conn.close()
	# neither of allowed requests
	else:
		error_str = http + ' 405 Method Not Allowed\r\n\r\n'
		conn.send(error_str.encode('utf-8'))
		conn.close()
