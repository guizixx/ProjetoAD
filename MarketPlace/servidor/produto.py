class Produto:
    _contador_global = 1

    def __init__(self, nome, categoria, preco, quantidade):
        self.id = Produto._contador_global
        self.nome = nome
        self.categoria = categoria
        self.preco = round(preco, 2)
        self.quantidade = quantidade
        Produto._contador_global += 1

    def obter_id(self):
        return self.id