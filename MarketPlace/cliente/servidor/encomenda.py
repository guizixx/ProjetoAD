# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio Encomenda. Representa uma encomenda feita por um cliente, 
#            com id, data, carrinho de compras, id do cliente e valor_total. O id é gerado automaticamente.

class Encomenda:
    _contador_global = 1
    def __init__(self, data, carrinho_compras, cliente_id, total):
        self.id = Encomenda._contador_global
        self.data = data
        self.carrinho_compras = carrinho_compras
        self.cliente_id = cliente_id
        self.total = total
        Encomenda._contador_global += 1

