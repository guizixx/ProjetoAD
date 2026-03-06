# Grupo: 47
# Guilherme Pinto - nº 60260 
# Tiago Telha - nº 60261
# Descrição: métodos utilitários gerais

import re

#---------------------------
# Normaliza comando textual
#---------------------------

def normalizar_nome(nome): 
    # remove espaços extremos
    nome = nome.strip()

    nome = nome.replace('"', '').replace("'", '')

    # substitui múltiplos espaços por 1 só
    nome = re.sub(r'\s+', ' ', nome)

    # normaliza capitalização
    return nome.lower().title()