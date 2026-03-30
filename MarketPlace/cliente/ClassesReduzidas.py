

class ClienteLoja:

    def __init__(self, nome, email, pw, id, permissao):
        self.id = id
        self.nome = nome
        self.email = email
        self.pw = pw
        self.carrinho_compras = {}  # { id_produto : quantidade }
        self.permissao = permissao

class Encomenda:
    _contador_global = 1
    def __init__(self, data, carrinho_compras, cliente_id, total):
        self.id = Encomenda._contador_global
        self.data = data
        self.carrinho_compras = carrinho_compras
        self.cliente_id = cliente_id
        self.total = total
        Encomenda._contador_global += 1

class Produto:
    _contador_global = 1

    def __init__(self, nome, categoria, preco, quantidade):
        self.id = Produto._contador_global
        self.nome = nome
        self.categoria = categoria
        self.preco = round(preco, 2)
        self.quantidade = quantidade
        Produto._contador_global += 1

class Categoria:
    _contador_global = 1

    def __init__(self, nome):
        self.id = Categoria._contador_global
        self.nome = nome
        Categoria._contador_global += 1