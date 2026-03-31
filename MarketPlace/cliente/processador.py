# Grupo: 47
# Guilherme Pinto - nº 60260
# Tiago Telha - nº 60261
# Descrição: Processador do cliente - valida os argumentos passados pelo utilizador e transforma o comando num pedido formatado, chama o Stub 
#            para enviar/receber, e formata a resposta
#            para apresentar ao utilizador.

from shared.excepcoes_shared import OpCodes
import shared.excepcoes_shared
from cliente.ClassesReduzidas import ClienteLoja, Encomenda, Produto, Categoria
from operator import itemgetter

COMANDOS_VALIDOS = {
    "CRIA_CATEGORIA": [OpCodes.CRIA_CATEGORIA, 1],
    "LISTA_CATEGORIAS": [OpCodes.LISTA_CATEGORIAS, 0],
    "REMOVE_CATEGORIA": [OpCodes.REMOVE_CATEGORIA, 1],
    "CRIA_PRODUTO": [OpCodes.CRIA_PRODUTO, 4],
    "LISTA_PRODUTOS": [OpCodes.LISTA_PRODUTOS, 0],
    "AUMENTA_STOCK_PRODUTO": [OpCodes.AUMENTA_STOCK, 2],
    "ATUALIZA_PRECO_PRODUTO": [OpCodes.ATUALIZA_PRECO, 2],
    "CRIA_CLIENTE": [OpCodes.CRIA_CLIENTE, 3],
    "LISTA_CLIENTES": [OpCodes.LISTA_CLIENTES, 0],
    "ADICIONA_PRODUTO_CARRINHO": [OpCodes.ADICIONA_PRODUTO_CARRINHO, 2],
    "REMOVE_PRODUTO_CARRINHO": [OpCodes.REMOVE_PRODUTO_CARRINHO, 1],
    "LISTA_CARRINHO": [OpCodes.LISTA_CARRINHO, 0],
    "CHECKOUT_CARRINHO": [OpCodes.CHECKOUT_CARRINHO, 0],
    "LISTA_ENCOMENDAS": [OpCodes.LISTA_ENCOMENDAS, 1],
}

class Processador:

    def __init__(self, stub):
        self.stub = stub

    def validar_pedido(self, comando, args):
        
        if comando not in COMANDOS_VALIDOS:
            raise shared.excepcoes_shared.ComandoMalFormado(comando)
        if len(args) != COMANDOS_VALIDOS.get(comando)[1]:
            raise shared.excepcoes_shared.NumeroArgumentosInvalido(COMANDOS_VALIDOS.get(comando)[1], len(args))
        opc = COMANDOS_VALIDOS.get(comando)[0]
        args_norm = self.validar_args(comando, args)
        return opc, args_norm
    
    def validar_args(self, comando, args):
        if comando == "CRIA_PRODUTO":
            try:
                preco = float(args[2])
                qtd = int(args[3])
            except shared.excepcoes_shared.TipoArgumentoInvalido as e:
                raise e
            args[2] = preco
            args[3] = qtd
            
        elif comando == "AUMENTA_STOCK_PRODUTO":
            try:
                qtd = args[1]
            except shared.excepcoes_shared.TipoArgumentoInvalido as e:
                raise e
            args[1] = qtd

        elif comando == "ATUALIZA_PRECO_PRODUTO":
            try:
                qtd = args[1]
            except shared.excepcoes_shared.TipoArgumentoInvalido as e:
                raise e
            args[1] = qtd

        elif comando == "ADICIONA_PRODUTO_CARRINHO":
            try:
                qtd = args[1]
            except shared.excepcoes_shared.TipoArgumentoInvalido as e:
                raise e
            args[1] = qtd

        elif comando == "LISTA_ENCOMENDAS":
            try:
                id = args[0]
            except shared.excepcoes_shared.TipoArgumentoInvalido as e:
                raise e
            args[0] = id

        return args

    def processar_pedido(self, pedido):
        self.stub.envia(pedido)
        resposta = self.stub.recebe()
        return self.formatar_resposta(resposta)

    def formatar_resposta(self, resposta):
        if resposta == "SERVIDOR_ENCERROU":
            return resposta
        if not isinstance(resposta, list) or len(resposta) != 2:
            return f"Resposta inesperada: {resposta}"
        opcode = resposta[0]
        if 20000 <= opcode <= 30000:
            return self.formatar_ok(resposta)
        return self.formatar_nok(resposta)
    
    def formatar_ok(self, resposta):
        opcode = resposta[0]
 
        if opcode == OpCodes.OK_CRIA_CATEGORIA:
            cat = resposta[1][0]
            return f"Categoria {cat.nome} criada com sucesso."
 
        if opcode == OpCodes.OK_LISTA_CATEGORIAS:
            categorias = resposta[1][0]
            produtos   = resposta[1][1]
            if not categorias:
                return "Sem Categorias."
            linhas = [f"\nTotal Categorias: {len(categorias)}",
                      f"Total Produtos: {len(produtos)} \n"]
            for c in categorias:
                n_prod = sum(1 for p in produtos if p.categoria == c.nome)
                linhas.append(f"{c.id_categoria} - {c.nome} ({n_prod} produtos);")
            return "\n".join(linhas)
 
        if opcode == OpCodes.OK_REMOVE_CATEGORIA:
            nome_categoria = resposta[1][0].nome
            return f"Categoria {nome_categoria} removida com sucesso."
 
        if opcode == OpCodes.OK_CRIA_PRODUTO:
            prod = resposta[1][0]
            return f"Produto {prod.nome} criado com sucesso."
 
        if opcode == OpCodes.OK_LISTA_PRODUTOS:
            categorias = resposta[1][0]
            produtos   = resposta[1][1]
            if not produtos:
                return "Sem Produtos."
            total_qtd = sum(p.quantidade for p in produtos)
            linhas = [f"\nTotal Produtos: {len(produtos)}",
                      f"Total Quantidade: {total_qtd} \n"]
            for p in produtos:
                linhas.append(
                    f"{p.id_produto} - {p.nome} ({p.categoria}, "
                    f"{p.preco:.2f} euros, {p.quantidade} unidades);"
                )
            return "\n".join(linhas)
 
        if opcode == OpCodes.OK_AUMENTA_STOCK:
            prod = resposta[1][0]
            return f"Stock do produto {prod.obter_nome()} aumentado com sucesso."
 
        if opcode == OpCodes.OK_ATUALIZA_PRECO:
            prod = resposta[1][0]
            return f"O preço do produto {prod.obter_nome()} foi atualizado para {prod.obter_preco():.2f} com sucesso."
 
        if opcode == OpCodes.OK_CRIA_CLIENTE:
            cliente = resposta[1][0]
            # print("Resposta do criar cliente: ", resposta[1][0])
            return f"Cliente criado com sucesso com identificador único {cliente.obter_id()}."
 
        if opcode == OpCodes.OK_LISTA_CLIENTES:
            clientes = resposta[1][0]
            if not clientes:
                return "Sem Clientes."
            linhas = [f"Total Clientes: {len(clientes)} \n"]
            for c in clientes:
                linhas.append(f"{c.obter_id()} - {c.obter_nome()} ({c.obter_email()});")
            return "\n".join(linhas)
 
        if opcode == OpCodes.OK_ADICIONA_CARRINHO:
            prod = resposta[1][0]
            return f"Produto {prod.nome} adicionado com sucesso ao carrinho."
 
        if opcode == OpCodes.OK_REMOVE_CARRINHO:
            prod = resposta[1][0]
            return f"Produto {prod.nome} removido com sucesso do carrinho de compras."
 
        if opcode == OpCodes.OK_LISTA_CARRINHO:
            categorias = resposta[1][0]
            itens = resposta[1][1]
            if not itens:
                return "Carrinho Vazio."
            total_qtd = sum(prod.obter_quantidade() for prod in itens)
            total_preco = sum(prod.obter_preco() * prod.obter_quantidade() for prod in itens)
            cat_map = {c.obter_nome(): c for c in categorias}
            linhas = [f"\nTotal Produtos: {len(itens)}",
                      f"Total Quantidade: {total_qtd}",
                      f"Total Preço: {total_preco:.2f} euros \n"]
            for prod in itens:
                cat = cat_map.get(prod.obter_categoria(), None)
                cat_str = (f"{cat.obter_id()}-{cat.obter_nome()}"
                           if cat is None else f"{cat.obter_id()}-{cat.obter_nome()}")
                linhas.append(
                    f"{prod.obter_id()} - {prod.obter_nome()} ({cat_str}, "
                    f"{prod.obter_preco():.2f} euros, {prod.obter_quantidade()} unidades);"
                )
            return "\n".join(linhas)
 
        if opcode == OpCodes.OK_CHECKOUT:
            return ("Checkout de carrinho de compras efetuado com sucesso. "
                    "Encomenda criada com sucesso a partir do carrinho.")
 
        if opcode == OpCodes.OK_LISTA_ENCOMENDAS:
            return self.formatar_lista_encomendas(resposta)
        
        if opcode == OpCodes.LIGACAO_INTERROMPIDA:
            return 
 
        return f"{resposta[1]}"

    # def formatar_nok(self, resposta):
    #     opcode = resposta[0]
    #     if len(resposta) > 1:
    #         detalhe = resposta[1]
    #     else:
    #         detalhe = []
        
    #     return f"Erro {opcode}: {detalhe}"
    
    def formatar_lista_encomendas(self, resposta):
        encomendas = resposta[1][0]
        produtos_por_enc = resposta[1][1]
 
        if not encomendas:
            return "Sem encomendas."
 
        total_preco_geral = round(sum(e.obter_total() for e in encomendas), 2)
        ids_produtos_vistos = []
        cat_quantidades = {}
        linhas_encomendas = []
 
        for i, enc in enumerate(encomendas):
            itens = produtos_por_enc[i] if i < len(produtos_por_enc) else []
            total_qtd_enc = 0
            linhas_prods = []
            for prod in itens:
                total_qtd_enc += prod.obter_quantidade()
                if prod.obter_id() not in ids_produtos_vistos:
                    ids_produtos_vistos.append(prod.obter_id())
                cat_quantidades[prod.obter_categoria()] = (
                    cat_quantidades.get(prod.obter_categoria(), 0) + prod.obter_quantidade()
                )
                linhas_prods.append(
                    f"{prod.obter_id()} - {prod.obter_nome()} "
                    f"({prod.obter_categoria()}, {prod.obter_preco():.2f} euros, {prod.obter_quantidade()} unidades);"
                )
            linhas_encomendas += [
                f"ID Encomenda: {enc.obter_id()}",
                f"Data Encomenda: {enc.obter_data()}",
                f"Total Produtos: {len(itens)}",
                f"Total Quantidade: {total_qtd_enc}",
                f"Total Preço: {enc.obter_total():.2f} euros\n",
            ] + linhas_prods + ["\n"]
 
        cats_ord = sorted(cat_quantidades.items(), key=itemgetter(1), reverse=True)
        top = []
        if cats_ord:
            top.append(cats_ord[0][0])
            if len(cats_ord) > 1:
                top.append(cats_ord[1][0])
        if len(top) > 1:
            cat_top_str = "Categorias Top: " + ", ".join(top)
        elif top:
            cat_top_str = "Categoria Top: " + top[0]
        else:
            cat_top_str = ""
 
        linhas = [
            f"\nTotal Encomendas: {len(encomendas)}",
            f"Total Produtos: {len(ids_produtos_vistos)}",
            f"Total Preço: {total_preco_geral} euros",
            cat_top_str,
            "\n",
        ] + linhas_encomendas
 
        return "\n".join(linhas)

    
    def formatar_nok(self, resposta):
        opcode = resposta[0]
        detalhe = resposta[1] if len(resposta) > 1 else []

        if isinstance(detalhe, list) and detalhe:
            msg = detalhe[0]
            if isinstance(msg, str) and msg.strip():
                return f"{msg}"

        mensagens = {
            OpCodes.ERRO_GENERICO: "Erro genérico.",
            OpCodes.OP_CODE_INVALIDO: "Op_code inválido.",
            OpCodes.MENSAGEM_MAL_FORMADA: "Mensagem mal formada.",
            OpCodes.PEDIDO_NAO_E_LISTA: "Pedido inválido. Pedido deve ser uma lista.",
            OpCodes.NUMERO_CAMPOS_INVALIDO: "Pedido inválido. Pedido deve ter 4 campos.",
            OpCodes.ARGUMENTOS_NAO_SAO_LISTA: "O segundo campo (argumentos) deve ser uma lista.",
            OpCodes.PERFIL_INVALIDO: "Perfil inválido.",
            OpCodes.ID_UTILIZADOR_INVALIDO: "id_utilizador inválido.",
            OpCodes.SERIALIZACAO_INVALIDA: "Erro ao serializar dados antes de enviar.",
            OpCodes.DESSERIALIZACAO_INVALIDA: "Erro ao desserializar dados recebidos.",
            OpCodes.LIGACAO_INTERROMPIDA: "Ligação interrompida.",
            OpCodes.NUMERO_ARGUMENTOS_INVALIDO: "Número de argumentos inválido.",
            OpCodes.TIPO_ARGUMENTO_INVALIDO: "Tipo de argumento inválido.",
            OpCodes.VALOR_ARGUMENTO_INVALIDO: "Valor de argumento inválido.",
            OpCodes.ARGUMENTO_VAZIO: "Argumento vazio.",
            OpCodes.OPERACAO_NAO_AUTORIZADA: "Operação não autorizada.",
            OpCodes.UTILIZADOR_NAO_AUTENTICADO: "Utilizador não autenticado.",
            OpCodes.ERRO_INTERNO_SERVIDOR: "Erro interno do servidor.",

            OpCodes.CATEGORIA_JA_EXISTE: "A categoria já existe.",
            OpCodes.CATEGORIA_NAO_EXISTE: "A categoria não existe.",
            OpCodes.CATEGORIA_COM_PRODUTOS: "A categoria tem produtos associados com stock.",

            OpCodes.PRODUTO_JA_EXISTE: "O produto já existe.",
            OpCodes.CATEGORIA_NAO_EXISTE_PRODUTO: "A categoria não existe.",
            OpCodes.PRECO_INVALIDO: "Preço inválido.",
            OpCodes.QUANTIDADE_INVALIDA: "Quantidade inválida.",
            OpCodes.NOME_PRODUTO_INVALIDO: "Nome do produto inválido.",

            OpCodes.PRODUTO_NAO_EXISTE: "O produto não existe.",
            OpCodes.INCREMENTO_INVALIDO: "Valor de incremento inválido.",

            OpCodes.PRODUTO_NAO_EXISTE_PRECO: "O produto não existe.",
            OpCodes.NOVO_PRECO_INVALIDO: "Novo preço inválido.",

            OpCodes.EMAIL_JA_EXISTE: "Email já registado.",
            OpCodes.NOME_CLIENTE_INVALIDO: "Nome do cliente inválido.",
            OpCodes.EMAIL_INVALIDO: "Email inválido.",
            OpCodes.PASSWORD_INVALIDA: "Password inválida.",

            OpCodes.CLIENTE_NAO_EXISTE: "Cliente não existe.",
            OpCodes.PRODUTO_NAO_EXISTE_CARRINHO: "O produto não existe.",
            OpCodes.QUANTIDADE_INVALIDA_CARRINHO: "Quantidade inválida.",
            OpCodes.STOCK_INSUFICIENTE: "Stock insuficiente.",

            OpCodes.CLIENTE_NAO_EXISTE_REMOVE: "Cliente não existe.",
            OpCodes.PRODUTO_NAO_EXISTE_REMOVE: "O produto não existe.",
            OpCodes.PRODUTO_NAO_NO_CARRINHO: "Produto não está no carrinho.",

            OpCodes.CLIENTE_NAO_EXISTE_LISTA: "Cliente não existe.",

            OpCodes.CLIENTE_NAO_EXISTE_CHECKOUT: "Cliente não existe.",
            OpCodes.CARRINHO_VAZIO: "Carrinho vazio.",
            OpCodes.FALHA_ENCOMENDA: "Falha ao criar encomenda.",

            OpCodes.CLIENTE_NAO_EXISTE_ENCOMENDAS: "Cliente não existe.",
        }

        msg = mensagens.get(opcode)
        return f"{opcode} {msg}"
    

