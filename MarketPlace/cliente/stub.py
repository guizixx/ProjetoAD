from rede import Rede

# copiado da pl3, adaptar o que for necessario
class Stub:

    def __init__(self, HOST, PORT):
        self.rede = Rede(HOST, PORT)
        
    def processa(self, msg_str):
        self.envia(msg_str)
        resposta_str = self.recebe()
        print ('Recebi: %s' % resposta_str)

    def envia(self, msg_str): 
        bytes = msg_str.encode()
        self.rede.envia(bytes)

    def recebe(self): 
        bytes = self.rede.recebe()
        resposta_str = bytes.decode()
        return resposta_str

    def close(self): 
        self.rede.close()