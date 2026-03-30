# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio ClienteLoja - representa um cliente da loja com id, nome, email, password, carrinho de compras e permissao
#            O id é gerado automaticamente.
#            (o atributo permissão ainda não é útil nesta fase do projeto, mas foi adicionado preemptivamente)

class ClienteLoja:

    def __init__(self, nome, email, pw, id, permissao):
        self.id = id
        self.nome = nome
        self.email = email
        self.pw = pw
        self.carrinho_compras = {}  # { id_produto : quantidade }
        self.permissao = permissao



