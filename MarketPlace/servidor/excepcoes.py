# -----------------------------------
#   Excepções de Comando inválido
# -----------------------------------

class ExcepcaoComandoInvalido(Exception):

    def __init__(self, msg):
        super().__init__(msg)

class ExcepcaoArgumentoFloatInvalido(ExcepcaoComandoInvalido):

    def __init__(self, nome_argumento):
        super().__init__(f"O argumento \'{nome_argumento}'\ não é um float válido.")    
class ExcepcaoArgumentoNaoInteiro(ExcepcaoComandoInvalido):

    def __init__(self, nome_argumento):
        super().__init__(f"O argumento \'{nome_argumento}'\ não é um inteiro válido.")    

class ExcepcaoComandoNaoInterpretavel(ExcepcaoComandoInvalido):

    def __init__(self, comando):
        super().__init__(f"Não foi possível interpretar o comando \'{comando}\'. ")

class ExcepcaoComandoVazio(ExcepcaoComandoInvalido):

    def __init__(self):
        super().__init__(f"Não é possível correr um comando vazio. ")

class ExcepcaoComandoDesconhecido(ExcepcaoComandoInvalido):

    def __init__(self, nome_comando):
        super().__init__(f"O comando {nome_comando} não é conhecido. ")

class ExcepcaoComandoNumeroArgumentosIncorreto(ExcepcaoComandoInvalido):

    def __init__(self, nr_argumentos_esperado, nr_argumentos_fornecido):
        super().__init__(f"O número de argumentos é inválido. O esperado é {nr_argumentos_esperado} e não {nr_argumentos_fornecido}. ")


# ----------------------------------
#   Excepções de Regras de Negócio
# ----------------------------------
class ExcepcaoSupermercado(Exception):
    
    def __init__(self, msg):
        super().__init__(msg)

class ExcepcaoSupermercadoCategoriaJaExistente(ExcepcaoSupermercado):

    def __init__(self, nome_categoria):
        super().__init__(f"A categoria {nome_categoria} já existe. ")

