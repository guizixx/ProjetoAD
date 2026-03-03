# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 
# Descrição: 

# -----------------------------------
#   Excepções de Configuracao
# -----------------------------------

class ExcepcaoConfiguracaoInvalida(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class ExcepcaoIPInvalido(ExcepcaoConfiguracaoInvalida):

    def __init__(self, ip, e):
        super().__init__(f"Endereço de IP \'{ip}\' inválido. ")

class ExcepcaoPortoInvalido(ExcepcaoConfiguracaoInvalida):

    def __init__(self, porto):
        super().__init__(f"Porto {porto} inválido. Porto deve ser inteiro entre 1024 e 65535")

# -----------------------------------
#   Excepções de Sistema Distribuído
# -----------------------------------

# TODO: Acrescentar excepcoes

