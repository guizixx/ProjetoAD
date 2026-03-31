from shared.excepcoes_shared import OpCodes
import shared.excepcoes_shared
from cliente.ClassesReduzidas import ClienteLoja, Encomenda, Produto, Categoria

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
        # nome = resposta[1][0].nome
        # print(f"CLIENTE> Resposta recebida dentro do processador: {resposta}. Nome: {nome}")
        return self.formatar_resposta(resposta)

    def formatar_resposta(self, resposta):
        if resposta == "SERVIDOR_ENCERROU":
            return resposta
        print(f"CLIENTE> Resposta recebida dentro do processador: {resposta}. Tamanho: {len(resposta)}")
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
            return f"OK; Categoria {cat.nome} criada com sucesso."
 
        if opcode == OpCodes.OK_LISTA_CATEGORIAS:
            categorias = resposta[1][0]
            produtos   = resposta[1][1]
            if not categorias:
                return "OK; Sem Categorias."
            linhas = [f"\nTotal Categorias: {len(categorias)}",
                      f"Total Produtos: {len(produtos)} \n"]
            for c in categorias:
                n_prod = sum(1 for p in produtos if p.categoria == c.nome)
                linhas.append(f"{c.id_categoria} - {c.nome} ({n_prod} produtos);")
            return "OK;" + "\n".join(linhas)
 
        if opcode == OpCodes.OK_REMOVE_CATEGORIA:
            nome_categoria = resposta[1][0].nome
            return f"OK; Categoria {nome_categoria} removida com sucesso."
 
        if opcode == OpCodes.OK_CRIA_PRODUTO:
            prod = resposta[1][0]
            return f"OK; Produto {prod.nome} criado com sucesso."
 
        if opcode == OpCodes.OK_LISTA_PRODUTOS:
            categorias = resposta[1][0]
            produtos   = resposta[1][1]
            if not produtos:
                return "OK; Sem Produtos."
            total_qtd = sum(p.quantidade for p in produtos)
            linhas = [f"\nTotal Produtos: {len(produtos)}",
                      f"Total Quantidade: {total_qtd} \n"]
            for p in produtos:
                linhas.append(
                    f"{p.id_produto} - {p.nome} ({p.categoria}, "
                    f"{p.preco:.2f} euros, {p.quantidade} unidades);"
                )
            return "OK;" + "\n".join(linhas)
 
        if opcode == OpCodes.OK_AUMENTA_STOCK:
            prod = resposta[1][0]
            return f"OK; Stock do produto {prod.nome} aumentado com sucesso."
 
        if opcode == OpCodes.OK_ATUALIZA_PRECO:
            prod = resposta[1][0]
            return f"OK; O preço do produto {prod.nome} foi atualizado para {prod.preco:.2f} com sucesso."
 
        if opcode == OpCodes.OK_CRIA_CLIENTE:
            cliente = resposta[1][0]
            # print("Resposta do criar cliente: ", resposta[1][0])
            return f"OK; Cliente criado com sucesso com identificador único {cliente.id_cliente}."
 
        if opcode == OpCodes.OK_LISTA_CLIENTES:
            clientes = resposta[1][0]
            if not clientes:
                return "OK; Sem Clientes."
            linhas = [f"\nTotal Clientes: {len(clientes)} \n"]
            for c in clientes:
                linhas.append(f"{c.id_cliente} - {c.nome} ({c.email});")
            return "OK;" + "\n".join(linhas)
 
        if opcode == OpCodes.OK_ADICIONA_CARRINHO:
            prod = resposta[1][0]
            return f"OK; Produto {prod.nome} adicionado com sucesso ao carrinho."
 
        if opcode == OpCodes.OK_REMOVE_CARRINHO:
            prod = resposta[1][0]
            return f"OK; Produto {prod.nome} removido com sucesso do carrinho de compras."
 
        if opcode == OpCodes.OK_LISTA_CARRINHO:
            categorias = resposta[1][0]
            itens = resposta[1][1]
            if not itens:
                return "OK; Carrinho Vazio."
            total_qtd = sum(qtd for (_, qtd) in itens)
            total_preco = sum(prod.preco * qtd for (prod, qtd) in itens)
            cat_map = {c.id_categoria: c for c in categorias}
            linhas = [f"\nTotal Produtos: {len(itens)}",
                      f"Total Quantidade: {total_qtd}",
                      f"Total Preço: {total_preco:.2f} euros"]
            for (prod, qtd) in itens:
                cat = cat_map.get(prod.id_categoria, None)
                cat_str = (f"{prod.id_categoria}-{prod.categoria}"
                           if cat is None else f"{cat.id_categoria}-{cat.nome}")
                linhas.append(
                    f"{prod.id_produto} - {prod.nome} ({cat_str}, "
                    f"{prod.preco:.2f} euros, {qtd} unidades);"
                )
            return "OK;" + "\n".join(linhas)
 
        if opcode == OpCodes.OK_CHECKOUT:
            return ("OK; Checkout de carrinho de compras efetuado com sucesso. "
                    "Encomenda criada com sucesso a partir do carrinho.")
 
        if opcode == OpCodes.OK_LISTA_ENCOMENDAS:
            return self.formatar_lista_encomendas(resposta)
        
        if opcode == OpCodes.LIGACAO_INTERROMPIDA:
            return 
 
        return f"OK; {resposta[1]}"

    def formatar_nok(self, resposta):
        opcode = resposta[0]
        if len(resposta) > 1:
            detalhe = resposta[1]
        else:
            detalhe = []
        
        return f"NOK; Erro {opcode}: {detalhe}"
    
    def formatar_lista_encomendas(self, resposta):
        encomendas = resposta[1]
        produtos_por_enc = resposta[2] if len(resposta) > 2 else []
 
        if not encomendas:
            return "OK; Sem encomendas."
 
        from operator import itemgetter
 
        total_preco_geral = round(sum(e.total_preco for e in encomendas), 2)
        ids_produtos_vistos = []
        cat_quantidades = {}
        linhas_encomendas = []
 
        for i, enc in enumerate(encomendas):
            itens = produtos_por_enc[i] if i < len(produtos_por_enc) else []
            total_qtd_enc = 0
            linhas_prods = []
            for (prod, qtd, preco_enc) in itens:
                total_qtd_enc += qtd
                if prod.id_produto not in ids_produtos_vistos:
                    ids_produtos_vistos.append(prod.id_produto)
                cat_quantidades[prod.categoria] = (
                    cat_quantidades.get(prod.categoria, 0) + qtd
                )
                linhas_prods.append(
                    f"{prod.id_produto} - {prod.nome} "
                    f"({prod.categoria}, {preco_enc:.2f} euros, {qtd} unidades);"
                )
            linhas_encomendas += [
                f"ID Encomenda: {enc.id_encomenda}",
                f"Data Encomenda: {enc.data}",
                f"Total Produtos: {len(itens)}",
                f"Total Quantidade: {total_qtd_enc}",
                f"Total Preço: {enc.total_preco:.2f} euros\n",
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
            f"Total Preço: {total_preco_geral}",
            cat_top_str,
            "--------------------------------------------------------------------------",
        ] + linhas_encomendas
 
        return "OK;" + "\n".join(linhas)