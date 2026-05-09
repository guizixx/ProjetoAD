# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Skeleton - camada de comunicação do servidor.
#            Responsável por receber bytes da rede, desserializar com pickle,
#            e serializar + enviar as respostas. Não interpreta comandos.

from servidor.rede import TCPSocketServidor
import pickle, struct
from shared.socket_utilities import PontoAcesso
from shared import excepcoes_shared
from servidor.loja import Loja

class Skeleton:

    def __init__(self, pontoAcesso, cert_ficheiro=None, key_ficheiro=None, ca_ficheiro=None):
        self.rede = TCPSocketServidor(pontoAcesso, cert_ficheiro, key_ficheiro, ca_ficheiro)
        self.loja = Loja()

    def reset(self): 
        self.obter_loja().reset()

    def obter_loja(self):
        return self.loja
    
    def obter_rede(self):
        return self.rede

    def accept(self): 
        conn_sock, addr = self.obter_rede().accept()
        print("SERVIDOR> Servidor ligado a %s no porto %s" % (self.obter_rede().ponto_acesso.endereco_ip, self.obter_rede().ponto_acesso.porto))
        return conn_sock, addr

    def envia(self, conn_sock, msg_str): 
        try:
            bytes = pickle.dumps(msg_str, protocol=pickle.HIGHEST_PROTOCOL)            
            tamanho = struct.pack('!I', len(bytes))
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacaoInvalida()
        try:
            self.obter_rede().envia(conn_sock, tamanho, bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", msg_str)

    def recebe(self, conn_sock): 
        try:
            msg_bytes = self.obter_rede().recebe(conn_sock)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        try:
            msg = pickle.loads(msg_bytes)
        except Exception:
            raise excepcoes_shared.ExcecaoDesserializacaoInvalida()
        print(f"SERVIDOR> Comando recebido: {msg}")
        return msg

    def close(self): 
        self.obter_rede().close()

    def closeall(self): 
        self.obter_rede().closeall()

    # ------------------------------------------------------------------
    # Sincronização de estado servidor com servidor 
    # ------------------------------------------------------------------

    def enviar_estado(self, sock, loja):
        """
        Serializa o estado completo da loja e envia-o para o socket indicado (servidor a seguir na cadeia)

        Possivelmente isto é redundante, porque secalhar pode-se só utilizar o envia() normal e fazemos a exportação do estado antes de chamar o envia().
        """

        try:
            estado = loja.exportar_estado()
            dados =  pickle.dumps(estado, protocol=pickle.HIGHEST_PROTOCOL)
            tamanho = struct.pack('!I', len(dados))
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacaoInvalida()
        try:
            self.obter_rede().envia(sock, tamanho, dados)
            print("SERVIDOR> Estado da loja enviado com sucesso.")
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e

    def receber_estado(self, sock):
        """
        Recebe o estado completo da Loja enviado pelo antecessor, desserializa com pickle e aplica-o à Loja local.
        """
        try:
            msg_bytes = self.obter_rede().recebe(sock)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        try:
            estado = pickle.loads(msg_bytes)
        except Exception:
            raise excepcoes_shared.ExcecaoDesserializacaoInvalida()
 
        self.obter_loja().importar_estado(estado)
        print("SERVIDOR> Estado da loja recebido e atualizado com sucesso.")


