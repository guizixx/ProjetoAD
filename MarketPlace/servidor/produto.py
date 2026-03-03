# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: Classe de domínio Produto - representa um produto no supermercado, com id, nome, categoria, preço e quantidade. O id é gerado automaticamente.

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