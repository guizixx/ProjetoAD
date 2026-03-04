# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: Classe de domínio ClienteLoja - representa um cliente da loja

class ClienteLoja:
    _contador_global = 1

    def __init__(self, nome, email, pw):
        self.id = ClienteLoja._contador_global
        self.nome = nome
        self.email = email
        self.pw = pw
        self.carrinho_compras = {}  # { id_produto : quantidade }
        self.permissao = "Cliente"
        ClienteLoja._contador_global += 1

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



