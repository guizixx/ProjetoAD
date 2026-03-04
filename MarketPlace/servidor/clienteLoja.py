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



