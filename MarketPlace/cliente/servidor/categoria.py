# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio Categoria - representa uma categoria de produtos no supermercado,
#            com id e nome. O id é gerado automaticamente.

class Categoria:
    _contador_global = 1

    def __init__(self, nome):
        self.id = Categoria._contador_global
        self.nome = nome
        Categoria._contador_global += 1