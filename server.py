from cgi import print_arguments, print_form
from socket import *
import ssl
from rdt import *
from datetime import*

options = "1 - cardápio\n2 - pedir \n3 - conta individual\n4 - conta da mesa\n5 - levantar\n"
new_line = '\n'

def horario():
  relogio = datetime.now()
  return relogio.strftime("%X")[:5]

cardapio =  {
  1: ('pao com mortadela', '2.00'),
  2: ('qualquer coisa vegana', '40.00'),
  3: ('prato do dia', '3.00'),
  4: ('arroz com feijao', '4.00')
}

pedidos = {}

def showCardapio():
  card = ""
  for x, y in cardapio.items():
    card = card + " " + str(x) + " " + str(y[0]) + " " + " " + str(y[1]) + "\n" 
  return card


def pedido(mesa, cliente, data):
  prato = cardapio.get(int(data.decode()))

  pedidos[mesa][cliente]["pedidos"].append(prato)
  pedidos[mesa]["total"] += float(prato[1])
  pedidos[mesa][cliente]["comanda"] += float(prato[1])


RDTSocket = RDT(1)

data = RDTSocket.receive()

data = horario() + " cliente: "
RDTSocket.send_pkg(data.encode())

data = RDTSocket.receive()

while(data.decode() != "chefia"):
  data = horario() + " cliente:"
  RDTSocket.send_pkg(data.encode())
  data = RDTSocket.receive()

data = horario() + " CINtofome: Digite Sua mesa\n" + horario() + " cliente: "
RDTSocket.send_pkg(data.encode())

data = RDTSocket.receive()
mesa = data.decode()

data = horario() + " CINtofome: Digite Seu nome: \n" + horario() + " cliente: "
RDTSocket.send_pkg(data.encode())

data = RDTSocket.receive()
nome = data.decode()

# Atualiza tabela geral para inserir a mesa
if mesa not in pedidos:
  pedidos[mesa] = {
    "total": 0.0 
    } 

# Insere cliente
pedidos[mesa].update({
  nome: {
      "nome": nome, 
      "comanda": 0.0,
      "socket": "", # Falta colocar socket aqui
      "pedidos": []
    }
  })

data = horario() + " CINtofome: Digite uma das opções a seguir (ou número ou por extenso) \n" + options + horario() +" " + nome +": "
RDTSocket.send_pkg(data.encode())

pagamento = True

while True:

  req = RDTSocket.receive()
  data = req.decode('utf8')

  if (data == "1" or data == "cardápio"):
    resp = horario() + " CINtofome:\n" + showCardapio() + horario() +" " + nome + ": "

  if (data == "2" or data == "pedir"):
    resp = horario() + " CINtofome: Digite o primeiro item que gostaria (número) \n" + horario() +" " + nome +": "
    RDTSocket.send_pkg(resp.encode())
    
    data = RDTSocket.receive()
    while True:
      pedido(mesa,nome,data)
    
      resp = horario() + " CINtofome : Gostaria de mais algum item? (número ou por extenso) \n" + horario() +" " + nome + ": "
      RDTSocket.send_pkg(resp.encode())
      data = RDTSocket.receive() 

      if(str(data.decode()) == "nao"):
        break
    resp = horario() + " CINtofome: É pra já! \n" + horario() +" " + nome + ": "
    
    print(pedidos)

    pagamento = False
  
  if(data == "3" or data == "conta individual"):
    conta = f"{new_line}"
    valor = pedidos[mesa][nome]["comanda"]
    for produto in pedidos[mesa][nome]["pedidos"]:
      conta += f"{produto[0]} -> {str(produto[1])} {new_line}"

    resp = f"Sua conta total é:{new_line}{conta}------------- {new_line}Valor: {str(valor)}"
    resp += f"{new_line}{horario()} {nome}: "

  #if(data == 4 or data == "conta da mesa"):

  if(data == "5" or data == "pagar"):
    
    pagamento = True    
    resp = horario() + " CINtofome : Conta paga \n" + horario() +" " + nome + ": "

  if((data == "6" or data == "levantar") and ~pagamento):
    resp = horario() + " " + nome + ": Você ainda não pagou sua conta\n" + horario() + " " + nome + ": "

  if(data == "levantar" and pagamento):
    resp = "ok"
    del pedidos[mesa][nome] # Apaga cliente da mesa
    RDTSocket.send_pkg(resp.encode())
    break

  RDTSocket.send_pkg(resp.encode())

# Encerra conexão com cliente
data = horario() + " " + nome + ": Volte sempre ^^ \n"
RDTSocket.send_pkg(data.encode())

RDTSocket.close_connection()



