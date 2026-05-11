# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Stub - camada de comunicação do cliente.
#            Simétrico ao Skeleton: serializa pedidos com pickle e envia com prefixo
#            de tamanho; recebe bytes e desserializa a resposta. Não interpreta conteúdo.

from cliente.rede import TCPSocketCliente
from shared import excepcoes_shared
import pickle, struct

class Stub:

    def __init__(self, ponto_acesso_W, ponto_acesso_R, ca_ficheiro=None):
        self.redeW = TCPSocketCliente(ponto_acesso_W, ca_ficheiro)
        self.redeR = TCPSocketCliente(ponto_acesso_R, ca_ficheiro)

    def obter_rede_w(self):
        return self.redeW
    
    def obter_rede_r(self):
        return self.redeR
    
    def ligar(self):
        self.obter_rede_w().ligar()
        self.obter_rede_r().ligar()

    def desligar(self):
        self.obter_rede_w().desligar()
        self.obter_rede_r().desligar()
        
    def envia(self, pedido): 
        try:
            bytes = pickle.dumps(pedido, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacaoInvalida("Erro ao serializar pedido.")
        try:
            self.obter_rede_w().envia(bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e

    def recebe(self): 
        try:
            bytes = self.obter_rede_r().recebe()
            print(f"CLIENTE> Tamanho dos bytes recebidos: {len(bytes)}")
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        try:
            resposta = pickle.loads(bytes)
            print(f"CLIENTE> Resposta dentro do recebe do stub: {resposta}")
        except Exception:
            raise excepcoes_shared.ExcecaoDesserializacaoInvalida("Erro ao desserializar resposta.")
        return resposta

