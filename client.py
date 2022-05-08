from socket import *
from rdt import *

RDTSocket = RDT()

msg = " "

while True:
  
  RDTSocket.send_pkg(msg.encode())

  resp = RDTSocket.receive()

  if (resp.decode('utf-8') == "ok"):
    break

  msg = input(resp.decode('utf8'))


resp = RDTSocket.receive()
print(resp.decode())

RDTSocket.close_connection()
    
    