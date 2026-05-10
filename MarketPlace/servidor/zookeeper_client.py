# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Integração do servidor com o ZooKeeper.
#            Responsável por registar o servidor na cadeia, descobrir sucessor/antecessor,
#            fazer watch à cadeia e notificar o main quando a cadeia muda.

from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError, NodeExistsError
import threading

CHAIN_PATH = "/chain"

class ZooKeeperServidor:

    def __init__(self, endereco_zk, ip_proprio, porto_proprio):
        """
        endereco_zk: string "ip:porto" do ZooKeeper
        ip_proprio: IP deste servidor
        porto_proprio: porto TCP deste servidor
        """

        self.endereco_zk = endereco_zk
        self.ip_proprio = ip_proprio
        self.porto_proprio = str(porto_proprio)

        self.zk = KazooClient(hosts=self.endereco_zk)

        self.meu_znode = None

        self.sucessor_endereco = None
        
        self.sock_sucessor = None

        self.antecessor_endereco = None

        # Lock para garantir que enquanto faz a propagação da escrita não possa ser feita mais nenhuma operação de escrita.
        self.lock_escrita = threading.Lock()

        self._rede = None

    def ligar(self, rede):
        """Ligar ao ZooKeeper e garantir que /chain existe"""
        self._rede = rede
        self.zk.start()
        print(f"SERVIDOR-ZK> Ligado ao ZooKeeper em {self.endereco_zk}")
        self._garantir_raiz()
    
    def desligar(self):
        """Desligar do ZooKeeper"""
        if self.sock_sucessor is not None:
            try:
                self.sock_sucessor.close()
            except Exception:
                pass
            self.sock_sucessor = None
        self.zk.stop()
        self.zk.close()
        print("SERVIDOR-ZK> Desligado do ZooKeeper.")

    def registar(self):
        """
        Cria um ZNode efémero sequencial em /chain com o conteúdo 'ip:porto'.
        Guarda o path em self.meu_znode
        Devolve o path criado.
        """

        conteudo = f"{self.ip_proprio}:{self.porto_proprio}".encode("utf-8")
        path = self.zk.create(
            f"{CHAIN_PATH}/node",
            value=conteudo,
            ephemeral=True,
            sequence=True
        )
        self.meu_znode = path
        print(f"SERVIDOR-ZK> ZNode criado: {self.meu_znode}")
        return self.meu_znode

    def descobrir_vizinhos(self):
        """
        Determina: self.antecessor_endereco; self.sucessor_znode; self.sucessor_endereco.
        Devolve (antecessor_endereco, sucessor_endereco).
        """

        filhos = self._obter_filhos_com_watch()
        # Ordena lexicograficamente
        filhos_ordenados = sorted(filhos)

        meu_nome = self.meu_znode.split("/")[-1]

        if meu_nome not in filhos_ordenados:
            print("SERVIDOR-ZK> AVISO: o meu ZNode não está na lista de filhos.")
            return None, None

        meu_indice = filhos_ordenados.index(meu_nome)

        # Antecessor (apenas para sincronização inicial)
        if meu_indice > 0:
            antecessor_nome = filhos_ordenados[meu_indice - 1]
            self.antecessor_endereco = self._obter_endereco(antecessor_nome)
            print(f"SERVIDOR-ZK> Antecessor: {antecessor_nome} - {self.antecessor_endereco}")
        else:
            self.antecessor_endereco = None
            print("SERVIDOR-ZK> Sou o HEAD (Sem antecessor).")
        
        #Sucessor
        if meu_indice < len(filhos_ordenados) - 1:
            sucessor_nome = filhos_ordenados[meu_indice + 1]
            self.sucessor_endereco = self._obter_endereco(sucessor_nome)
            self.sock_sucessor = self._rede.ligar_a_servidor(self.sucessor_endereco)
            print(f"SERVIDOR-ZK> Sucessor: {sucessor_nome} - {self.sucessor_endereco}")
        else:
            self.sucessor_endereco = None
            self.sock_sucessor = None
            print(f"SERVIDOR-ZK> Sou a TAIL (Sem sucessor).")
        
        return self.antecessor_endereco, self.sucessor_endereco

    def obter_sock_sucessor(self):
        return self.sock_sucessor
    
    def obter_sucessor_endereco(self):
        return self.sucessor_endereco

    def obter_antecessor_endereco(self):
        return self.antecessor_endereco
    
    def obter_lock_escrita(self):
        return self.lock_escrita

    def eh_tail(self):
        return self.sucessor_endereco is None
    
    def eh_head(self):
        return self.antecessor_endereco is None

    
    def _garantir_raiz(self):
        """Cria /chain se ainda não existir."""
        if not self.zk.exists(CHAIN_PATH):
            try:
                self.zk.create(CHAIN_PATH, b"", makepath=True)
                print(f"SERVIDOR-ZK> ZNode raiz {CHAIN_PATH} criado.")
            except NodeExistsError:
                # Já foi criado por outro servidor em simultâneo.
                pass

    def _obter_filhos_com_watch(self):
        """
        Obtém filhos de /chain e põe um watch.
        O watch chama _ao_mudar_cadeia quando os filhos mudam.
        Devolve a lista de nomes dos filhos.
        """

        filhos = self.zk.get_children(CHAIN_PATH, watch=self._ao_mudar_cadeia)
        return filhos

    def _obter_endereco(self, nome_filho):
        """
        Lê o conteúdo do ZNode /chain/<nome_filho>.
        Devolve a string "ip:porto" ou None.
        """

        path = f"{CHAIN_PATH}/{nome_filho}"
        try:
            dados, _ = self.zk.get(path)
            return dados.decode("utf-8")
        except NoNodeError:
            return None

    def _ao_mudar_cadeia(self, evento):
        """
        Callback do ZooKeeper: chamado quando os filhos de /chain mudam.
        Reavalia o sucessor e chama o callback
        """
        print(f"SERVIDOR-ZK> Mudança na cadeia detetada: {evento}")

        # Obter novamente os filhos mas com novo watch
        try:
            filhos = self._obter_filhos_com_watch()
        except Exception as e:
            print(f"SERVIDOR-ZK> Erro ao reler filhos: {e}")
            return
        
        filhos_ordenados = sorted(filhos)
        meu_nome = self.meu_znode.split("/")[-1]

        if meu_nome not in filhos_ordenados:
            # Este servidor já não está na cadeia
            return
        
        meu_indice = filhos_ordenados.index(meu_nome)

        # Verificar antecessor novamente
        if meu_indice > 0:
            antecessor_nome = filhos_ordenados[meu_indice - 1]
            self.antecessor_endereco = self._obter_endereco(antecessor_nome)
        else:
            self.antecessor_endereco = None
        
        # Verificar sucessor novamente
        novo_sucessor_endereco = None
        if meu_indice < len(filhos_ordenados) - 1:
            sucessor_nome = filhos_ordenados[meu_indice + 1]
            novo_sucessor_endereco = self._obter_endereco(sucessor_nome)

        if novo_sucessor_endereco != self.sucessor_endereco:
            print(f"SERVIDOR-ZK> Sucessor mudou: {self.sucessor_endereco} passou para {novo_sucessor_endereco}")

            if self.sock_sucessor is not None:
                try:
                    self.sock_sucessor.close()
                except Exception:
                    pass
                self.sock_sucessor = None

            self.sucessor_endereco = novo_sucessor_endereco

            # abrir socket para novo sucessor
            if novo_sucessor_endereco is not None:
                self.sock_sucessor = self._rede.ligar_a_servidor(novo_sucessor_endereco)
                print(f"SERVIDOR-ZK> Novo sucessor ligado: {novo_sucessor_endereco}")
            else:
                print(f"SERVIDOR-ZK> Passei a ser a TAIL (Sem sucessor).")