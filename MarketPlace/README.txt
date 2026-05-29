Grupo: 47
Guilherme Pinto - nº 60260
Tiago Telha - nº 60261

COMO EXECUTAR

Os comandos devem ser executados na pasta raiz do projeto (MarketPlace).

1. Iniciar o servidor (Terminal 1):
    python -m servidor.main <porto> <ip_zk>:<porto_zk> <cert_ficheiro <key_ficheiro> <ca_ficheiro>

2. Iniciar o cliente (Terminal 2):
    python -m cliente.main <ip_zk>:<porto_zk> <id_perfil> <id_utilizador> <ca_ficheiro>

TESTES EXECUTADOS

Foram apenas executados testes à mão a partir do terminal para verificação e consolidação de lógica, respostas e erros.
