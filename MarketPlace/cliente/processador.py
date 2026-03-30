from shared.excepcoes_shared import OpCodes
import shared.excepcoes_shared
from cliente.ClassesReduzidas import ClienteLoja, Encomenda, Produto, Categoria

OPCODES_VALIDOS = {
    OpCodes.CRIA_CATEGORIA,
    OpCodes.LISTA_CATEGORIAS,
    OpCodes.REMOVE_CATEGORIA,
    OpCodes.CRIA_PRODUTO,
    OpCodes.LISTA_PRODUTOS,
    OpCodes.AUMENTA_STOCK,
    OpCodes.ATUALIZA_PRECO,
    OpCodes.CRIA_CLIENTE,
    OpCodes.LISTA_CLIENTES,
    OpCodes.ADICIONA_PRODUTO_CARRINHO,
    OpCodes.REMOVE_PRODUTO_CARRINHO,
    OpCodes.LISTA_CARRINHO,
    OpCodes.CHECKOUT_CARRINHO,
    OpCodes.LISTA_ENCOMENDAS,
}

class Processador:

    def __init__(self, stub):
        self.stub = stub

    def validar_pedido(self, pedido):
        opcode = pedido[0]
        lista_args = pedido[1]
        perfil = pedido[2]
        id_utilizador = pedido[3]

        if not isinstance(pedido, list):
            raise ValueError("Pedido deve ser uma lista.")
        if len(pedido) != 4:
            raise ValueError(f"O pedido deve conter 4 campos, tem {len(pedido)}.")
        if not isinstance(opcode, int) or opcode not in OPCODES_VALIDOS:
            raise ValueError(f"Op_code inválido: {opcode}.")
        if not isinstance(lista_args, list):
            raise ValueError("Ö segundo campo (argumentos) deve ser uma lista.")
        if not isinstance(perfil, int) or perfil not in [0, 1, 2, 3]:
            raise ValueError(f"Perfil inválido: {perfil}. Deve ser 0, 1, 2 ou 3.")
        if not isinstance(id_utilizador, int) or id_utilizador < 0:
            raise ValueError(f"id_utilizador inválido: {id_utilizador}. Deve ser um inteiro não negativo.")
    
    def processar_pedido(self, pedido):
        self.validar_pedido(pedido)
        self.stub.envia(pedido)
        resposta = self.stub.recebe()
        return resposta

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
            return f"OK; Categoria {cat.nome} criada com sucesso."
 
        if opcode == OpCodes.OK_LISTA_CATEGORIAS:
            categorias = resposta[1]
            produtos   = resposta[2] if len(resposta) > 2 else []
            if not categorias:
                return "OK; Sem Categorias."
            linhas = [f"\nTotal Categorias: {len(categorias)}",
                      f"Total Produtos: {len(produtos)}"]
            for c in categorias:
                n_prod = sum(1 for p in produtos if p.categoria == c.nome)
                linhas.append(f"{c.id_categoria} - {c.nome} ({n_prod} produtos);")
            return "OK;" + "\n".join(linhas)
 
        if opcode == OpCodes.OK_REMOVE_CATEGORIA:
            return "OK; Categoria removida com sucesso."
 
        if opcode == OpCodes.OK_CRIA_PRODUTO:
            prod = resposta[1][0]
            return f"OK; Produto {prod.nome} criado com sucesso."
 
        if opcode == OpCodes.OK_LISTA_PRODUTOS:
            categorias = resposta[1]
            produtos   = resposta[2] if len(resposta) > 2 else []
            if not produtos:
                return "OK; Sem Produtos."
            total_qtd = sum(p.quantidade for p in produtos)
            linhas = [f"\nTotal Produtos: {len(produtos)}",
                      f"Total Quantidade: {total_qtd}"]
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
            return f"OK; Cliente criado com sucesso com identificador único {cliente.id}."
 
        if opcode == OpCodes.OK_LISTA_CLIENTES:
            clientes = resposta[1]
            if not clientes:
                return "OK; Sem Clientes."
            linhas = [f"\nTotal Clientes: {len(clientes)}"]
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
            categorias = resposta[1]
            itens      = resposta[2] if len(resposta) > 2 else []
            if not itens:
                return "OK; Carrinho Vazio."
            total_qtd   = sum(qtd for (_, qtd) in itens)
            total_preco = sum(prod.preco * qtd for (prod, qtd) in itens)
            cat_map     = {c.id_categoria: c for c in categorias}
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
        encomendas       = resposta[1]
        produtos_por_enc = resposta[2] if len(resposta) > 2 else []
 
        if not encomendas:
            return "OK; Sem encomendas."
 
        from operator import itemgetter
 
        total_preco_geral   = round(sum(e.total_preco for e in encomendas), 2)
        ids_produtos_vistos = []
        cat_quantidades     = {}
        linhas_encomendas   = []
 
        for i, enc in enumerate(encomendas):
            itens         = produtos_por_enc[i] if i < len(produtos_por_enc) else []
            total_qtd_enc = 0
            linhas_prods  = []
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