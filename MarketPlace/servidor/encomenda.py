class Encomenda:
    _contador_global = 1
    def __init__(self, data, carrinho_compras, cliente_id, total):
        self.id = Encomenda._contador_global
        self.data = data
        self.carrinho_compras = carrinho_compras
        self.cliente_id = cliente_id
        self.total = total
        Encomenda._contador_global += 1

    def obter_id(self):
        return self.id
