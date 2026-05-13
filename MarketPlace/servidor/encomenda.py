# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio Encomenda. Representa uma encomenda feita por um cliente, 
#            com id, data, carrinho de compras, id do cliente e valor_total. O id é gerado automaticamente.

class Encomenda:
    _contador_global = 1
    def __init__(self, data, carrinho_compras, cliente_id, total, cliente_nome=None, cliente_email=None):
        self.id_encomenda = Encomenda._contador_global
        self.data = data
        self.produtos = carrinho_compras
        self.id_cliente = cliente_id
        self.cliente_nome = cliente_nome
        self.cliente_email = cliente_email
        self.total_preco = total
        Encomenda._contador_global += 1

    def obter_id(self):
        return self.id_encomenda
    
    def obter_data(self):
        return self.data
    
    def obter_carrinho_compras(self):
        return self.produtos
    
    def obter_cliente_id(self):
        return self.id_cliente
    
    def obter_cliente_nome(self):
        return self.cliente_nome
    
    def obter_cliente_email(self):
        return self.cliente_email
    
    def obter_total(self):
        return self.total_preco

