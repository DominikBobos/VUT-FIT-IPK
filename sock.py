import socket
import sys
from urllib.parse import urlparse


def ValidIp(address):	#checks for valid IP
    try: 
        socket.inet_aton(address)
        return True
    except:
        return False

def ValidAddress(address):	#checks for valid IP or URL
	if (isinstance(address, str)):
		address = address.encode('utf-8')
	if (ValidIp(address.decode('utf-8')) == False):
		url = urlparse(address.decode('utf-8'))
		url = url[2]			
		return url 					#return url
		if (url == ''):
			return False			#end connection
	else:
		url = address.decode('utf-8')	
		return url 					#return IP

#arguments parsing
if (len(sys.argv) == 2) and (sys.argv[1][4] == '='):
	str1 = sys.argv[1].split('=')[0] #if (sys.argv[2] == "3333"):
	str2 = sys.argv[1].split('=')[1]
	if (str1 == 'PORT' and str2.isdigit() ):
		pass
	else:
		sys.stderr.write("ERROR: Wrong typed port.\n")
		sys.exit(1)
else:
	sys.stderr.write("ERROR: Could not start server, TCP_PORT was not specified.\n")
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
	data = conn.recv(BUFFER_SIZE)	#recieving data
	http = data.find(b'HTTP')	#checks for http version
	http_end = data.find(b"\r",http)
	http = data[http:http_end].decode('utf-8')
	error_str = http + ' 400 Bad Request\r\n\r\n'

	if (data[:3] == b'GET'):
		if (data[4:12] != b'/resolve'):
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue
		try:
			data = data.split(b'?')		#GET a resolve v [0] zvysok v [1]
		except ValueError:
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue

		if (len(data) == 2):
			try:
				url = data[1].split(b'&')	#url pripadne ip mam v [0] zvysok v [1]
			except ValueError:
				conn.send(error_str.encode('utf-8'))
				conn.close()
				continue
		else:		# data sa nespravne rozdelili
			conn.send(error_str.encode('utf-8'))
			conn.close()
			continue

		if (len(url) == 2 and url[1][5] == 65):	#type "A"
			url = ValidAddress(url[0][5:])
			if (url == False):
				conn.send(error_str.encode('utf-8'))
				conn.close()
				continue
			try:
				ip = socket.gethostbyname(url)
			except:
				error_str = http + ' 404 Not Found\r\n\r\n'
				conn.send(error_str.encode('utf-8'))
				conn.close()
				continue
			http_ver = http + " 200 OK\r\n\r\n"
			send_str = url + ":A=" + ip + "\n"
			
			conn.send(http_ver.encode('utf-8'))
			conn.send(send_str.encode('utf-8'))
			conn.close()	
		elif (len(url) == 2 and url[1][5:8] == bytes("PTR",'utf-8')):
			
			if (ValidIp(url[0][5:].decode('utf-8')) == False):
				url = urlparse(url[0][5:].decode('utf-8'))
				url = url[2]
				if (url == ''):
					conn.send(error_str.encode('utf-8'))
					conn.close()
					continue
			else:
				url = url[0][5:].decode('utf-8')

			if (url == ''):
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
		for x in range(7,len(data)):
			if (data[x][-2] == 'A' or data[x][-1] == 'A'):
				ind = 0
				if (data[x][-1] == 'A'):
					ind = 1
				url = ValidAddress(data[x][:(-3+ind)])
				if (url == False):
					conn.send(error_str.encode('utf-8'))
					conn.close()
					break
				try:
					ip = socket.gethostbyname(url)
				except:
					continue	#not included to final response
				send_str = url + ":A=" + ip + "\n"

			elif (data[x][-4:-1] == 'PTR' or data[x][-3:] == 'PTR'):
				ind = 0
				if (data[x][-3:] == 'PTR'):
					ind = 1
				url = ValidAddress(data[x][:(-5+ind)])
				if (url == False):
					conn.send(error_str.encode('utf-8'))
					conn.close()
					break
				try:
					host = socket.gethostbyaddr(url)
				except:
					continue	#not included to final response
				send_str = url + ":PTR=" + host[0] + "\n"				
			else:
				conn.send(error_str.encode('utf-8'))
				conn.close()
				break
			final_msg += send_str
		
		http_ver = http + " 200 OK\r\n\r\n"
		conn.send(http_ver.encode('utf-8'))
		conn.send(final_msg.encode('utf-8'))
		conn.close()
	else:
		error_str = http + ' 405 Method Not Allowed\r\n\r\n'
		conn.send(error_str.encode('utf-8'))
		conn.close()