# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio ClienteLoja - representa um cliente da loja com id, nome, email, password, carrinho de compras e permissao
#            O id é gerado automaticamente.
#            (o atributo permissão ainda não é útil nesta fase do projeto, mas foi adicionado preemptivamente)

class ClienteLoja:

    def __init__(self, nome, email, pw, id):
        self.id = id
        self.nome = nome
        self.email = email
        self.pw = pw
        self.carrinho_compras = {}  # { id_produto : quantidade }
        self.permissao = 1

    def obter_id(self):
        return self.id
    
    def obter_nome(self):
        return self.nome
    
    def obter_email(self):
        return self.email
    
    def obter_carrinho_compras(self):
        return self.carrinho_compras
    
    def obter_permissao(self):
        return self.permissao
    
    def alterar_permissao(self, nova_permissao):
        self.permissao = nova_permissao



