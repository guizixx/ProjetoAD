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

class ZooKeeperCliente:

    def __init__(self, endereco_zk):

        self.endereco_zk = endereco_zk
        self.zk = KazooClient(hosts=self.endereco_zk)
        
        self.endereco_head = None
        self.endereco_tail = None
        self.znode_head = None
        self.znode_tail = None
        

    def obter_head(self):
        return self.endereco_head

    def obter_tail(self):
        return self.endereco_tail
    
    def alterar_head(self, head):
        self.head = head

    def alterar_tail(self, tail):
        self.tail = tail


    def ligar(self):
        """Ligar ao ZooKeeper e garantir que /chain existe"""
        self.zk.start()
        print(f"CLIENTE-ZK> Ligado ao ZooKeeper em {self.endereco_zk}")

    def desligar(self):
        """Desligar do ZooKeeper"""
        self.zk.stop()
        self.zk.close()
        print("CLIENTE-ZK> Desligado do ZooKeeper.")

    def obter_filhos_com_watch(self):
        """
        Obtém filhos de /chain e põe um watch.
        O watch chama handler_alteracao_cadeia quando os filhos mudam.
        Devolve a lista de nomes dos filhos.
        """

        filhos = self.zk.get_children(CHAIN_PATH, watch=self.handler_alteracao_cadeia)
        return filhos

    def obter_head_e_tail(self):
        """
        Obtém servidores head e tail a partir dos filhos
        do zookeeper.
        Altera os atributos head e tail da classe para a str 
        'ip:port' de cada um dos respetivos servidores obtidos
        """
        try: 
            filhos = self.obter_filhos_com_watch()
        except Exception as e:
            print(f"CLIENTE-ZK> Erro ao ler filhos: {e}")
            return
        
        filhos_ord = sorted(filhos)

        if not filhos_ord:
            print("CLIENTE-ZK> Nenhum servidor na cadeia.")
            return

        head = filhos_ord[0]
        self.znode_head = head
        try:
            data_h, _ = self.zk.get(f"/chain/{head}")
        except Exception as e:
            print(f"CLIENTE-ZK> Erro ao obter servidor {head}: {e}")
            return
        self.endereco_head = data_h.decode("utf-8")

        tail = filhos_ord[-1]
        self.znode_tail = tail
        try:
            data_t, _ = self.zk.get(f"/chain/{tail}")
        except Exception as e:
            print(f"CLIENTE-ZK> Erro ao obter servidor {tail}: {e}")
            return
        self.endereco_tail = data_t.decode("utf-8")

    def handler_alteracao_cadeia(self):
        """
        Callback do ZooKeeper: chamado quando os filhos de /chain mudam.
        Avalia se os servidores definidos como head e tail precisam de ser
        alterados com base numa reavaliação dos filhos de /chain
        """
        print(f"CLIENTE-ZK> Mudança na cadeia detetada.")

        try: 
            filhos = self.obter_filhos_com_watch()
        except Exception as e:
            print(f"CLIENTE-ZK> Erro ao reler filhos: {e}")
            return

        filhos_ord = sorted(filhos)
        if not filhos_ord:
            print("CLIENTE-ZK> Cadeia vazia após mudança.")
            return
        head = filhos_ord[0]
        tail = filhos_ord[-1]
        
        # Verificar alteração na head
        if head != self.znode_head:
            self.znode_head = head
            try:
                data_h, _ = self.zk.get(f"/chain/{head}")
            except Exception as e:
                print(f"CLIENTE-ZK> Erro ao obter servidor {head}: {e}")
                return
            self.endereco_head = data_h.decode("utf-8")
            
        # Verificar alteração na tail
        if tail != self.znode_tail:
            self.znode_tail = tail
            try:
                data_t, _ = self.zk.get(f"/chain/{tail}")
            except Exception as e:
                print(f"CLIENTE-ZK> Erro ao obter servidor {tail}: {e}")
                return
            self.endereco_tail = data_t.decode("utf-8")




        
