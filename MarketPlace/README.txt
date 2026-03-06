Grupo: 47
Guilherme Pinto - nº 60260
Tiago Telha - nº 60261

COMO EXECUTAR

Os comandos devem ser executados na pasta raiz do projeto (MarketPlace).

1. Iniciar o servidor (Terminal 1):
    python -m servidor.main <porto>

2. Iniciar o cliente (Terminal 2):
    python -m cliente.main <porto>

TESTES EXECUTADOS

1. testes.py (fornecido pelo professor)
    - Resultado: todos os testes passaram com sucesso.

2. testes2.py (criados pelo grupo)
    - Testes aos comandos:
        LISTA_CATEGORIAS, REMOVE_CATEGORIA,
       CRIA_PRODUTO, LISTA_PRODUTOS,
       AUMENTA_STOCK_PRODUTO, ATUALIZA_PRECO_PRODUTO,
       CRIA_CLIENTE, LISTA_CLIENTES,
       ADICIONA_PRODUTO_CARRINHO, REMOVE_PRODUTO_CARRINHO,
       LISTA_CARRINHO, CHECKOUT_CARRINHO,
       LISTA_ENCOMENDAS
    - Resultado: todos os testes passaram com sucesso.

3. testes dos comandos no terminal para verificação e consolidação de lógica, respostas e erros

Para correr os testes:
    python -m unittest testes.py
    python -m unittest testes2.py

LIMITAÇÕES

- O servidor não termina ao pressionar Control+C.