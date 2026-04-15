# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio Produto - representa um produto no supermercado, 
#               com id, nome, categoria, preço e quantidade. O id é gerado automaticamente.

class Produto:
    _contador_global = 1

    def __init__(self, nome, categoria, preco, quantidade):
        self.id_produto = Produto._contador_global
        self.nome = nome
        self.categoria = categoria
        self.preco = round(preco, 2)
        self.quantidade = quantidade
        self.quantidade_aumentada = 0
        Produto._contador_global += 1

    def obter_id(self):
        return self.id_produto
    
    def obter_nome(self):
        return self.nome
    
    def obter_categoria(self):
        return self.categoria
    
    def obter_preco(self):
        return self.preco
    
    def obter_quantidade(self):
        return self.quantidade
    
    def obter_quantidade_aumentada(self):
        return self.quantidade_aumentada
    
    def adicionar_quantidade(self, adicionado):
        self.quantidade += adicionado
        self.quantidade_aumentada = adicionado

    def alterar_quantidade(self, novo):
        self.quantidade = novo

    def alterar_preco(self, novo):
        self.preco = round(novo, 2)