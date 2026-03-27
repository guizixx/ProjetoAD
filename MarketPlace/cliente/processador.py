from cliente.stub import Stub


class Processador:

    def __init__(self, pontoAcesso):
        self.stub = Stub(pontoAcesso)

    def envia(self, msg_str):
        self.stub.envia(msg_str)

    def recebe(self):
        self.stub.recebe()

    def ligar(self):
        self.stub.ligar()

    def desligar(self):
        self.stub.desligar()
