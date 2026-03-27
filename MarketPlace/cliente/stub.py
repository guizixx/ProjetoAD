from cliente.rede import TCPSocketCliente
from shared import excepcoes_shared
import pickle, struct
from shared.excepcoes_shared import OpCodes

# copiado da pl3, adaptar o que for necessario
class Stub:

    def __init__(self, ponto_acesso):
        self.rede = TCPSocketCliente(ponto_acesso)
    
    def ligar(self):
        self.rede.ligar()

    def desligar(self):
        self.rede.desligar()
        

    def envia(self, pedido): 
        try:
            bytes = pickle.dumps(pedido, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacao("Erro ao serializar pedido.")
        try:
            self.rede.envia(bytes)
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        print("Estou a enviar", pedido)

    def recebe(self): 
        try:
            bytes = self.rede.recebe()
        except excepcoes_shared.ExcecaoLigacaoInterrompida as e:
            raise e
        try:
            resposta = pickle.loads(bytes)
        except Exception:
            raise excepcoes_shared.ExcecaoSerializacao("Erro ao desserializar resposta.")
        return resposta

    def processa(self, op_code, args, perfil, id_utilizador):
        pedido = [op_code, args, perfil, id_utilizador]
        self.envia(pedido)
        return self.recebe()
    

### Categoria
    def cria_categoria(self, nome_categoria, perfil, id_utilizador):
        return self.processa(OpCodes.CRIA_CATEGORIA, [nome_categoria], perfil, id_utilizador)
 
    def lista_categorias(self, perfil, id_utilizador):
        return self.processa(OpCodes.LISTA_CATEGORIAS, [], perfil, id_utilizador)
 
    def remove_categoria(self, nome_categoria, perfil, id_utilizador):
        return self.processa(OpCodes.REMOVE_CATEGORIA, [nome_categoria], perfil, id_utilizador)
    
### Produto
    def cria_produto(self, nome, categoria, preco, quantidade, perfil, id_utilizador):
        return self.processa(OpCodes.CRIA_PRODUTO, [nome, categoria, preco, quantidade], perfil, id_utilizador)
 
    def lista_produtos(self, perfil, id_utilizador):
        return self.processa(OpCodes.LISTA_PRODUTOS, [], perfil, id_utilizador)
 
    def aumenta_stock(self, nome_produto, delta, perfil, id_utilizador):
        return self.processa(OpCodes.AUMENTA_STOCK, [nome_produto, delta], perfil, id_utilizador)
 
    def atualiza_preco(self, nome_produto, novo_preco, perfil, id_utilizador):
        return self.processa(OpCodes.ATUALIZA_PRECO, [nome_produto, novo_preco], perfil, id_utilizador)
    
### Clientes
    def cria_cliente(self, nome, email, password, perfil, id_utilizador):
        return self.processa(OpCodes.CRIA_CLIENTE, [nome, email, password], perfil, id_utilizador)
 
    def lista_clientes(self, perfil, id_utilizador):
        return self.processa(OpCodes.LISTA_CLIENTES, [], perfil, id_utilizador)
    
### Carrinho
    def adiciona_produto_carrinho(self, nome_produto, quantidade, perfil, id_utilizador):
        return self.processa(OpCodes.ADICIONA_PRODUTO_CARRINHO, [nome_produto, quantidade], perfil, id_utilizador)
 
    def remove_produto_carrinho(self, nome_produto, perfil, id_utilizador):
        return self.processa(OpCodes.REMOVE_PRODUTO_CARRINHO, [nome_produto], perfil, id_utilizador)
 
    def lista_carrinho(self, perfil, id_utilizador):
        return self.processa(OpCodes.LISTA_CARRINHO, [], perfil, id_utilizador)
 
    def checkout_carrinho(self, perfil, id_utilizador):
        return self.processa(OpCodes.CHECKOUT_CARRINHO, [], perfil, id_utilizador)

### Encomendas
    def lista_encomendas(self, id_cliente, perfil, id_utilizador):
        return self.processa(OpCodes.LISTA_ENCOMENDAS, [id_cliente], perfil, id_utilizador)