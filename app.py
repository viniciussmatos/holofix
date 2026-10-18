"""
app.py - Servidor do Holofix  (ESQUELETO PARA OS ALUNOS)

O que é este arquivo?
    É a API: o "meio de campo" entre o ÓCULOS do técnico e o PAINEL do
    especialista. Os dois conversam SÓ com este servidor, trocando JSON.

        [óculos]  <--JSON-->  [app.py (API)]  <--JSON-->  [painel web]
                                    |
                                [dados.py]

Como rodar:
    pip install flask
    python app.py

Abra no navegador:
    http://localhost:5000/oculos   -> simulador da tela do óculos
    http://localhost:5000/painel   -> painel do especialista remoto

Como saber se a missão está certa:
    python verificar.py            (todas as missões)
    python verificar.py 1          (só a missão 1)

REGRAS DO JOGO
    - Procure por "TODO". Cada TODO diz o que fazer, passo a passo.
    - Meta mínima: missões 1, 2 e 3. As missões 4 e 5 valem pontos extras.
    - As páginas (óculos e painel) JÁ ESTÃO PRONTAS. Elas vão "ganhando vida"
      conforme vocês completam as missões.
    - Toda rota devolve JSON. Em caso de erro, use a função erro(...).
    - Não mude os nomes das rotas nem dos campos: o óculos e o painel
      dependem deles (é o "contrato" da API).

Dicas de Python/Flask que vão usar:
    jsonify(x)                        -> transforma dict/lista em resposta JSON
    return jsonify(x), 201            -> devolve JSON com código HTTP 201 (criado)
    request.get_json(silent=True)     -> lê o JSON que o cliente enviou (ou None)
    corpo.get("campo", "")            -> pega um campo do dict, com valor padrão
    texto.strip() / texto.upper()     -> tira espaços / deixa em maiúsculas
    chave in dicionario               -> True se a chave existe
    dicionario.get(chave)             -> o valor, ou None se não existir
"""

from flask import Flask, jsonify, request, send_from_directory

import dados

app = Flask(__name__, static_folder="static")


# ===============================================================
# PÁGINAS (já prontas - não precisa mexer)
# ===============================================================
@app.route("/")
def inicio():
    return send_from_directory("static", "index.html")


@app.route("/oculos")
def pagina_oculos():
    return send_from_directory("static", "oculos.html")


@app.route("/painel")
def pagina_painel():
    return send_from_directory("static", "painel.html")


# ===============================================================
# FUNÇÕES AUXILIARES (já prontas - usem à vontade)
# ===============================================================
def erro(mensagem, codigo_http):
    """Resposta de erro padrão. Ex.: return erro("Máquina não encontrada", 404)"""
    return jsonify({"erro": mensagem}), codigo_http


def nao_implementado(missao):
    """Resposta provisória enquanto a missão não é feita."""
    return erro(f"Missão {missao} ainda não implementada (veja o app.py)", 501)


def montar_ordem(ordem):
    """Junta a ordem com dados da máquina, do procedimento e do último
    pedido de ajuda. É ISSO que o óculos recebe para desenhar a tela.
    Sempre que uma rota for devolver uma ordem, devolva jsonify(montar_ordem(ordem))."""
    maquina = dados.maquinas[ordem["maquina_codigo"]]
    procedimento = dados.procedimentos[maquina["procedimento_id"]]
    passos = procedimento["passos"]

    ultima_ajuda = None
    for pedido in dados.pedidos_ajuda.values():
        if pedido["ordem_id"] == ordem["id"]:
            ultima_ajuda = pedido  # fica com o mais recente

    return {
        "id": ordem["id"],
        "tecnico": ordem["tecnico"],
        "status": ordem["status"],
        "maquina_codigo": maquina["codigo"],
        "maquina_nome": maquina["nome"],
        "procedimento": procedimento["titulo"],
        "passo_atual": ordem["passo_atual"],
        "total_passos": len(passos),
        "texto_passo": passos[ordem["passo_atual"]],
        "inicio": ordem["inicio"],
        "fim": ordem["fim"],
        "ajuda": ultima_ajuda,
    }


def total_de_passos(ordem):
    """Quantos passos tem o procedimento desta ordem."""
    maquina = dados.maquinas[ordem["maquina_codigo"]]
    return len(dados.procedimentos[maquina["procedimento_id"]]["passos"])


# ===============================================================
# MISSÃO 1 - MÁQUINAS                (feita junto com o professor)
# Quando terminar: a lista de máquinas aparece no óculos.
# ===============================================================
@app.route("/api/maquinas", methods=["GET"])
def listar_maquinas():
        # TODO 1.1: devolver TODAS as máquinas como uma LISTA em JSON.
    #   - As máquinas estão em dados.maquinas (um dicionário código -> máquina).
    #   - Dica: list(dados.maquinas.values()) vira uma lista.
    return jsonify(list(dados.maquinas.values()))

@app.route("/api/maquinas/<codigo>", methods=["GET"])
def buscar_maquina(codigo):
    # TODO 1.2: devolver UMA máquina pelo código.
    #   a) Deixe o código em maiúsculas (o usuário pode digitar "cmp-01").
    #   b) Se o código NÃO existir em dados.maquinas -> erro("Máquina não encontrada", 404)
    #   c) Pegue a máquina e o procedimento dela:
    #        dados.procedimentos[maquina["procedimento_id"]]
    #   d) Monte a resposta: uma CÓPIA da máquina (dict(maquina)) com dois campos a mais:
    #        "procedimento": título do procedimento
    #        "total_passos": quantidade de passos (len(...))
    #   e) return jsonify(resposta)
    codigo = codigo.upper()
    
    if codigo not in dados.maquinas:
        return erro("Máquina não encontrada", 404)
    
    maquina = dados.maquinas[codigo]
    procedimento = dados.procedimentos[maquina["procedimento_id"]]

    resposta = dict(maquina)
    total_passos = len(procedimento["passos"])
    resposta["procedimento"] = procedimento["titulo"]
    resposta["total_passos"] = total_passos

    return jsonify(resposta)


# ===============================================================
# MISSÃO 2 - ABRIR E CONSULTAR ORDEM DE SERVIÇO     (~55 min)
# Quando terminar: escolher a máquina no óculos mostra o 1º passo.
# ===============================================================
@app.route("/api/ordens", methods=["POST"])
def criar_ordem():
    # O óculos envia: {"maquina_codigo": "CMP-01", "tecnico": "Ana"}
    #
    # TODO 2.1: ler o JSON enviado:
    #     corpo = request.get_json(silent=True) or {}
    #   e pegar "maquina_codigo" (maiúsculas, sem espaços) e "tecnico" (sem espaços).
    #

    corpo = request.get_json(silent=True) or {}
    maquina_codigo = corpo.get("maquina_codigo", "").upper()
    tecnico = corpo.get("tecnico", "")

    # TODO 2.2: validar
    #   - se faltar código ou técnico -> erro("Informe maquina_codigo e tecnico", 400)
    #   - se a máquina não existir     -> erro("Máquina não encontrada", 404)
    #

    if not maquina_codigo or not tecnico:
        return erro("Informe maquina_codigo e tecnico", 400)

    if maquina_codigo not in dados.maquinas:
        return erro("Máquina não encontrada", 404)

    # TODO 2.3: criar a ordem (um dict) com estes campos:
    #     "id":             dados.proximo_id("ordem")
    #     "maquina_codigo": o código
    #     "tecnico":        o nome do técnico
    #     "status":         "em_andamento"
    #     "passo_atual":    0            (o primeiro passo é o 0)
    #     "inicio":         dados.agora()
    #     "fim":            None
    #   e guardar em dados.ordens[id] = ordem
    #

    ordem = {
        "id": dados.proximo_id("ordem"),
        "maquina_codigo": maquina_codigo,
        "tecnico": tecnico,
        "status": "em_andamento",
        "passo_atual": 0,
        "inicio": dados.agora(),
        "fim": None,
    }
    dados.ordens[ordem["id"]] = ordem
    # TODO 2.4: return jsonify(montar_ordem(ordem)), 201
    return jsonify(montar_ordem(ordem)), 201


@app.route("/api/ordens/<int:ordem_id>", methods=["GET"])
def buscar_ordem(ordem_id):
    # TODO 2.5: se ordem_id não estiver em dados.ordens -> erro("Ordem não encontrada", 404)
    #           senão devolva jsonify(montar_ordem(...)) da ordem.
    # (O óculos chama esta rota a cada 3 segundos para ver se chegou resposta do especialista.)
    if ordem_id not in dados.ordens:
        return erro("Ordem não encontrada", 404)
    else:
        return jsonify(montar_ordem(dados.ordens[ordem_id]))

# ===============================================================
# MISSÃO 3 - NAVEGAR PELOS PASSOS                   (~55 min)
# Com as missões 1, 2 e 3 prontas, o grupo atingiu a META MÍNIMA do dia.
# Quando terminar: as setas ← → do óculos funcionam e dá para concluir.
#
# As três rotas seguem a MESMA receita:
#   1. ordem = dados.ordens.get(ordem_id)  -> se for None: erro 404
#   2. se ordem["status"] == "concluida"   -> erro("Ordem já concluída", 400)
#   3. regra específica (abaixo)           -> se não puder: erro 400
#   4. altera a ordem e devolve jsonify(montar_ordem(ordem))
# ===============================================================
@app.route("/api/ordens/<int:ordem_id>/avancar", methods=["POST"])
def avancar_passo(ordem_id):
    # TODO 3.1: regra -> não pode avançar se já está no ÚLTIMO passo.
    #   O último passo é total_de_passos(ordem) - 1.
    #   Se puder, some 1 em ordem["passo_atual"].
    ordem = dados.ordens.get(ordem_id)
    if ordem == None:
        return erro("Ordem não encontrada", 404)
    
    if ordem["status"] == "concluida":
        return erro("Ordem já concluída", 400)

    if ordem["passo_atual"] >= total_de_passos(ordem) - 1:
        return erro("Já está no último passo", 400)

    ordem["passo_atual"] += 1
    return jsonify(montar_ordem(ordem))


@app.route("/api/ordens/<int:ordem_id>/voltar", methods=["POST"])
def voltar_passo(ordem_id):
    # TODO 3.2: regra -> não pode voltar se está no passo 0.
    #   Se puder, subtraia 1 de ordem["passo_atual"].
    ordem = dados.ordens.get(ordem_id)
    if ordem["passo_atual"] == 0:
        return erro("Já está no primeiro passo", 400)
    else:
        ordem["passo_atual"] -= 1
    return jsonify(montar_ordem(ordem))


@app.route("/api/ordens/<int:ordem_id>/concluir", methods=["POST"])
def concluir_ordem(ordem_id):
    # TODO 3.3: regra -> só pode concluir se estiver no ÚLTIMO passo
    #   (senão: erro("Ainda faltam passos", 400)).
    #   Se puder: status = "concluida" e fim = dados.agora().
    ordem = dados.ordens.get(ordem_id)
    if ordem["passo_atual"] != total_de_passos(ordem) - 1:
        return erro("Ainda faltam passos", 400)
    
    ordem["status"] = "concluida"
    ordem["fim"] = dados.agora() 

    return jsonify(montar_ordem(ordem))


# ===============================================================
# MISSÃO 4 - PEDIR AJUDA AO ESPECIALISTA            (BÔNUS, ~25 min)
# Quando terminar: seta ↓ no óculos abre o menu de ajuda e envia o pedido.
# ===============================================================
@app.route("/api/ordens/<int:ordem_id>/ajuda", methods=["POST"])
def pedir_ajuda(ordem_id):
    # O óculos envia: {"mensagem": "Não encontro a peça"}
    #
    # TODO 4.1: validar -> ordem existe (404)? não está concluída (400)?
    #           mensagem não está vazia (400 "Escreva a mensagem")?
    #
    ordem = dados.ordens.get(ordem_id)
    if ordem is None:
        return erro("Ordem não encontrada", 404)

    if ordem["status"] == "concluida":
        return erro("Ordem já concluída", 400)

    corpo = request.get_json(silent=True) or {}
    mensagem = corpo.get("mensagem", "")
    if not isinstance(mensagem, str) or not mensagem.strip():
        return erro("Escreva a mensagem", 400)
    
    # TODO 4.2: criar o pedido (um dict) com:
    #     "id":            dados.proximo_id("ajuda")
    #     "ordem_id":      ordem_id
    #     "passo":         o passo_atual da ordem (para o especialista saber onde o técnico está)
    #     "mensagem":      a mensagem
    #     "resposta":      None
    #     "status":        "aberto"
    #     "criado_em":     dados.agora()
    #     "respondido_em": None
    #   e guardar em dados.pedidos_ajuda[id] = pedido
    #
    pedido = {
        "id": dados.proximo_id("ajuda"),
        "ordem_id": ordem_id,
        "passo": ordem["passo_atual"],
        "mensagem": mensagem,
        "resposta": None,
        "status": "aberto",
        "criado_em": dados.agora(),
        "respondido_em": None,
    }

    dados.pedidos_ajuda[pedido["id"]] = pedido
    # TODO 4.3: mudar o status da ORDEM para "aguardando_ajuda"
    #
    ordem["status"] = "aguardando_ajuda"
    
    # TODO 4.4: return jsonify(pedido), 201
    return jsonify(pedido), 201


# ===============================================================
# MISSÃO 5 - PAINEL DO ESPECIALISTA                 (BÔNUS, ~35 min)
# Quando terminar: o painel mostra os pedidos, responde, e a resposta
# aparece na lente do óculos (em até 3 segundos).
# ===============================================================
@app.route("/api/ajudas", methods=["GET"])
def listar_ajudas():
    # TODO 5.1: devolver a LISTA de pedidos de ajuda.
    #   - Filtro opcional pela URL: /api/ajudas?status=aberto
    #       filtro = request.args.get("status")   (None se não veio)
    #     Se veio filtro, pule os pedidos com status diferente.
    #   - Cada item da lista deve ser uma cópia do pedido (dict(pedido)) com
    #     um campo a mais: "ordem" = montar_ordem(da ordem daquele pedido)
    #     (é assim que o painel sabe o técnico, a máquina e o texto do passo)
    filtro = request.args.get("status")
    pedidos = []
    for pedido in dados.pedidos_ajuda.values():
        if filtro is not None and pedido["status"] != filtro:
            continue
        item = dict(pedido)
        item["ordem"] = montar_ordem(dados.ordens[pedido["ordem_id"]])
        pedidos.append(item)
    return jsonify(pedidos)


@app.route("/api/ajudas/<int:ajuda_id>/responder", methods=["POST"])
def responder_ajuda(ajuda_id):
    # O painel envia: {"resposta": "Olhe atrás do painel lateral"}
    #
    # TODO 5.2: validar -> pedido existe (404)? já foi respondido (400)? 
    #           resposta não está vazia (400)?

    pedido = dados.pedidos_ajuda.get(ajuda_id)
    if pedido is None:
        return erro("Pedido não encontrado", 404)

    if pedido["status"] == "respondido":
        return erro("Pedido já respondido", 400)

    corpo = request.get_json(silent=True) or {}
    resposta = corpo.get("resposta", "")
    if not isinstance(resposta, str) or not resposta.strip():
        return erro("Escreva a resposta", 400)


    # TODO 5.3: preencher no pedido: "resposta", "status" = "respondido",
    #           "respondido_em" = dados.agora()

    pedido["resposta"] = resposta
    pedido["status"] = "respondido"
    pedido["respondido_em"] = dados.agora()

    # TODO 5.4: se a ORDEM desse pedido estiver "aguardando_ajuda",
    #           volte o status dela para "em_andamento"

    ordem = dados.ordens.get(ajuda_id)
    if ordem["status"] == "aguardando_ajuda":
        ordem["status"] = "em_andamento"

    # TODO 5.5: return jsonify(pedido)
    return jsonify(pedido)


@app.route("/api/ordens", methods=["GET"])
def listar_ordens():
    # TODO 5.6: devolver a lista de TODAS as ordens, cada uma passada por montar_ordem.
    #   Dica: [montar_ordem(o) for o in dados.ordens.values()]
    return [montar_ordem(o) for o in dados.ordens.values()]


# ===============================================================
# DESAFIOS EXTRAS (só depois das 5 missões) - ideias no roteiro do dia
# ===============================================================


if __name__ == "__main__":
    # debug=True faz o servidor reiniciar sozinho sempre que o arquivo é salvo
    app.run(port=5000, debug=True)
