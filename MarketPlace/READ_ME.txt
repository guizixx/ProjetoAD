MarketCenter – Cliente/Servidor com Comandos de Texto


Descrição

Este projeto constitui o esqueleto (template base) da primeira fase do projeto.

O objetivo deste repositório é fornecer:

    Estrutura inicial de pastas
    Classes base
    Exemplo de testes automáticos

Requisitos

Python 3.x (recomendado 3.8 ou superior)


COMO CORRER O PROJETO NO VISUAL CODE

Como Iniciar o Servidor

    Na pasta raiz do projeto (MarketCenter):

    python -m servidor.main <porto>

Iniciar o Cliente

    Abrir outro terminal, ainda na pasta raiz:

    python -m cliente.main <porto>


Exemplos de Comandos

Como criar categoria:

    CRIA_CATEGORIA "Eletronica Premium"

    Nota:
    Se o nome tiver espaços, deve ser colocado entre aspas (ou pelicas).

COMO CORRER OS UNIT TESTS

Como executar os testes:

    python -m unittest testes.py 
    NOTA IMPORTANTE: NAO ALTERE NADA QUE IMPEÇA O ATUAL testes.py DE EXECUTAR

Notas Finais: 

Execute sempre os comandos a partir da pasta raiz do projeto (cd MarketPlace).

Use "python -m ..." para evitar problemas de imports.