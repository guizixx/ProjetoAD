# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Integração do  com o ZooKeeper.
#            Responsável por registar o servidor na cadeia, descobrir sucessor/antecessor,
#            fazer watch à cadeia e notificar o main quando a cadeia muda.

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError, NodeExistsError
import threading

CHAIN_PATH = "/chain"

class ZookeeperCliente:

    def __init__(self, endereco_zk):

        self.endereco_zk = endereco_zk
        self.zk = KazooClient(hosts=self.endereco_zk)
        
        self.head = None
        self.tail = None
        

    def obter_head(self):
        return self.head

    def obter_tail(self):
        return self.tail

    def ligar(self):
        """Ligar ao ZooKeeper e garantir que /chain existe"""
        self.zk.start()
        print(f"CLIENTE-ZK> Ligado ao ZooKeeper em {self.endereco_zk}")

    def desligar(self):
        """Desligar do ZooKeeper"""
        self.zk.stop()
        self.zk.close()
        print("CLIENTE-ZK> Desligado do ZooKeeper.")

    def obter_filhos_com_watch_chain(self):
        """
        Obtém filhos de /chain e põe um watch.
        O watch chama handler_alteracao_cadeia quando os filhos mudam.
        Devolve a lista de nomes dos filhos.
        """

        filhos = self.zk.get_children(CHAIN_PATH, watch=self.handler_alteracao_cadeia)
        return filhos

    def obter_head_e_tail(self):

        filhos = self.obter_filhos_com_watch_chain()
        filhos_ord = sorted(filhos)

        head = filhos_ord[-1]
        data_h, _ = self.zk.get(f"/servers/{head}")
        self.head = data_h.decode("utf-8")

        tail = filhos_ord[0]
        data_t, _ = self.zk.get(f"/servers/{tail}")
        self.tail = data_t.decode("utf-8")

    def alterar_head(self, head):
        self.head = head

    def alterar_tail(self, tail):
        self.tail = tail

    def handler_alteracao_cadeia(self):


    



        
