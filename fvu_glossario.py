# -*- coding: utf-8 -*-
"""
fvu_glossario.py
================
Glossário técnico de classificação FVU escrito com as palavras do inspetor,
consolidado com o Manual de FVU MICHELIN e o Manual de Ressulcagem MICHELIN.

Uso no app Streamlit:

    from fvu_glossario import (
        GLOSSARIO_FVU,
        montar_prompt_inspecao,
        FVU_KEYWORDS,
        encontrar_fvu_por_descricao,
        aplicar_regras_deterministicas,
    )

Fluxo recomendado:
    prompt = montar_prompt_inspecao(fvu_data, tem_reforma=None)
    ... chama a IA ...
    codigo = aplicar_regras_deterministicas(item, n_reformas)
"""

# =============================================================================
# 1) GLOSSÁRIO — como o inspetor enxerga cada dano
#    Cada entrada: o que é, o que se vê na foto, como diferenciar do parecido,
#    e o que NUNCA pode ser confundido.
# =============================================================================

GLOSSARIO_FVU = {
    # ------------------------------ TOPO / BANDA ------------------------------
    "45B": {
        "titulo": "Deterioração do topo por choque",
        "zona": "BANDA DE RODAGEM (TOPO)",
        "definicao": (
            "Motorista bateu a BANDA DE RODAGEM contra obstáculo alto (meio-fio, cabeceira "
            "de ponte, pedra, degrau). O pneu rompe na banda com um CORTE que atravessa de "
            "FLANCO A FLANCO (transversal, de ombro a ombro). Esse corte atravessado é o "
            "maior indicador do 45B."
        ),
        "sinais_visuais": [
            "corte/ruptura transversal na banda, atravessando de ombro a ombro",
            "bordas do corte abertas, lonas de topo rompidas",
            "escultura (sulcos) ainda existe — o pneu NÃO está careca",
        ],
        "nao_confundir": {
            "48D": "se a banda está lisa/careca ou com cinta aparente → 48D, nunca 45B",
            "45A": "furo isolado de prego/parafuso, sem corte atravessado → 45A",
            "45G": "se o corte está no FLANCO e não na banda → 45G",
        },
    },
    "48D": {
        "titulo": "Desgaste da banda por utilização extrema",
        "zona": "BANDA DE RODAGEM (TOPO)",
        "definicao": (
            "CINTAS (lonas de topo / aço) APARENTES. Não precisa haver desgaste irregular; "
            "pode estar uniformemente gasto até expor o aço. REGRA DE OURO: se houver "
            "desgaste irregular acentuado E um dos lados já atingiu a cinta, o pneu é "
            "OBRIGATORIAMENTE 48D (não 45D)."
        ),
        "sinais_visuais": [
            "aço/cinta metálica visível na banda",
            "banda lisa, careca, sem sulco em toda a largura ou em um ombro",
            "sulco no limite legal (TWI atingido) com exposição estrutural",
        ],
        "nao_confundir": {
            "45D": "45D é desgaste irregular SEM cinta aparente. Cinta à vista → 48D.",
        },
    },
    "45D": {
        "titulo": "Desgaste irregular (um lado da banda)",
        "zona": "BANDA DE RODAGEM (TOPO)",
        "definicao": (
            "Desgaste acentuado SOMENTE de um lado da banda: os sulcos de um lado estão "
            "visivelmente mais baixos que os do outro lado. NÃO há cinta aparente — apenas "
            "a diferença de profundidade entre os lados."
        ),
        "sinais_visuais": [
            "um ombro/lado com sulco raso e o lado oposto com sulco cheio",
            "degrau de desgaste de bordo a bordo",
            "nenhum aço/cinta visível",
        ],
        "nao_confundir": {
            "48D": "se qualquer lado atingiu a cinta → 48D obrigatoriamente",
        },
        "nota_ressulcagem": (
            "Manual de Ressulcagem: pneu com desgaste irregular acentuado NÃO deve ser "
            "ressulcado — por isso 45D nunca coexiste com 45R."
        ),
    },
    "45N": {
        "titulo": "Ressulcagem executada fora do parâmetro (CONTRAN / MICHELIN)",
        "zona": "BANDA DE RODAGEM (TOPO) — SERVIÇO",
        "definicao": (
            "O borracheiro ressulcou (frisou) o pneu, mas fora da norma. Só se aplica a pneu "
            "SEM REFORMA (desenho original de fábrica, com marcação RESSULCÁVEL/REGROOVABLE)."
        ),
        "sinais_visuais": [
            "sulco novo com traçado torto, largura irregular ou fora do desenho original",
            "ressulcagem profunda demais: fundo do sulco encostando/expondo a lona de trabalho (aço)",
            "lâmina passou nos indicadores de desgaste (TWI) destruindo os testemunhos",
            "ressulcado em pneu que já estava com aço aparente, arrancamento ou picotamento",
            "ressulcado em pneu com desgaste irregular acentuado",
        ],
        "parametros_michelin": [
            "profundidade de ressulcagem típica: 2 a 3 mm conforme o modelo (XZE2/XZU3 2mm, XDE2/XZA2+ 3mm)",
            "largura típica de 6 a 12 mm conforme modelo, lâmina R3 ou R4",
            "profundidade de sulco original remanescente antes de ressulcar: 2 a 3 mm",
            "lonas de trabalho NUNCA podem ficar aparentes",
            "TWI deve ser preservado e rebaixado para 1,6 mm em relação ao novo fundo",
        ],
        "nao_confundir": {
            "45R": "45R é NÃO ter ressulcado; 45N é ter ressulcado ERRADO",
            "48D": "aço aparente por desgaste de rodagem → 48D; aço aparente causado pela lâmina → 45N",
        },
        "pre_requisito": "n_reformas == 0",
    },
    "45R": {
        "titulo": "Ressulcagem não realizada",
        "zona": "BANDA DE RODAGEM (TOPO) — SERVIÇO",
        "definicao": (
            "Pneu chegou ao fim da 1ª vida SEM ter sido ressulcado, perdendo quilometragem e "
            "economia. Penalizamos para reforçar a prática. Só se aplica a pneu SEM REFORMA, "
            "com desenho original do fabricante e marcação RESSULCÁVEL."
        ),
        "sinais_visuais": [
            "desenho original de fábrica, sem nenhum sulco reaberto por lâmina",
            "sulcos uniformemente gastos até o limite, sem sinal de ressulcagem",
            "banda em bom estado geral (sem arrancamento/picotamento) — ou seja, era ressulcável",
        ],
        "nao_confundir": {
            "45N": "há sulco reaberto por lâmina → é 45N (ressulcado errado), não 45R",
            "45D": "se há desgaste irregular acentuado, o pneu não era ressulcável → 45D",
        },
        "pre_requisito": "n_reformas == 0",
    },

    # --------------------------------- FLANCO ---------------------------------
    "45F": {
        "titulo": "Ferida acidental no flanco",
        "zona": "FLANCO",
        "definicao": (
            "Motorista cortou o flanco. Corte geralmente HORIZONTAL, RETILÍNEO e PEQUENO, "
            "acompanhado de algumas ranhuras/riscos no flanco."
        ),
        "sinais_visuais": [
            "corte único, limpo e retilíneo na horizontal do flanco",
            "ranhuras/arranhões próximos",
            "não arranca pedaço de borracha",
        ],
        "nao_confundir": {
            "45G": "corte grande, com pedaço arrancado → 45G",
            "70K": "rachadura circunferencial com borda ondulada/oscilante (parede rachada) → 70K. "
                   "O 45F é CORTE retilíneo, o 70K é RACHADURA irregular.",
            "46F": "marcas repetidas/circunferenciais no mesmo ponto → 46F",
        },
    },
    "45G": {
        "titulo": "Deterioração do flanco por choque",
        "zona": "FLANCO",
        "definicao": (
            "Igual ao 45F na origem, porém o corte é MUITO MAIOR — às vezes arranca pedaços "
            "de borracha do flanco."
        ),
        "sinais_visuais": [
            "rasgo extenso no flanco",
            "pedaço de borracha faltando / cratera no flanco",
            "possível exposição pontual da lona carcaça no ponto do rasgo",
        ],
        "nao_confundir": {
            "45F": "corte pequeno e retilíneo → 45F",
            "70J/70L": "quando a destruição é no TALÃO (lona de reforço solta ou cordonéis rompidos)",
        },
    },
    "46F": {
        "titulo": "Agressões repetidas no flanco",
        "zona": "FLANCO",
        "definicao": (
            "Agressões REPETIDAS no mesmo lugar do flanco, fragilizando a lateral e gerando "
            "rachaduras ou perfurações. Casos típicos: peça do veículo que se soltou e ficou "
            "raspando o pneu (dano circunferencial na lateral), ou pedra presa entre os duplos "
            "traseiros que, com a rodagem, perfura/fissura o flanco."
        ),
        "sinais_visuais": [
            "faixa/trilha de dano acompanhando a circunferência do flanco",
            "abrasão contínua, ranhuras repetidas, borracha lixada",
            "perfuração ou fissura no ponto de contato constante",
        ],
        "nao_confundir": {
            "45F": "dano único e pontual → 45F",
            "70K": "rachadura circunferencial por fadiga, sem sinal de atrito externo → 70K",
        },
    },
    "52B": {
        "titulo": "Flexão importante no interior (baixa pressão)",
        "zona": "FLANCO / INTERIOR",
        "definicao": (
            "Pneu rodou com BAIXA PRESSÃO e flexionou o flanco a ponto de marcar INTERNAMENTE "
            "o liner (butil): ranhuras ou rachaduras internas. Só classifico 52B quando NÃO há "
            "destruição interna/externa como no 52H — apenas a marca interna."
        ),
        "sinais_visuais": [
            "faixa circunferencial de ranhuras/rachaduras no liner interno",
            "brilho/marca de atrito interno",
            "flanco externo ainda íntegro, mantendo forma",
        ],
        "nao_confundir": {
            "52H": "se há pó de borracha esfarelada dentro, ou flanco sem estrutura → 52H",
        },
    },
    "52H": {
        "titulo": "Rodagem sem ar / flexão importante do flanco",
        "zona": "FLANCO / INTERIOR",
        "definicao": (
            "Parecido com 52B, mas com DANO efetivo — interno, externo ou ambos. Tipicamente "
            "há PÓ dentro do pneu (esfarelamento da borracha interna pela fricção da flexão) "
            "e/ou o flanco foi destruído a ponto de não ter mais estrutura para o pneu ficar em pé."
        ),
        "sinais_visuais": [
            "pó preto de borracha solto no interior",
            "liner esfarelado, arrancado, esfacelado",
            "flanco colapsado / pneu não mantém a forma",
            "marca circunferencial de esmagamento nos dois flancos",
        ],
        "nao_confundir": {
            "52B": "apenas marcas/ranhuras internas, sem pó e sem colapso → 52B",
        },
    },
    "75A": {
        "titulo": "Agressões físicas ou químicas (óleo/derivados de petróleo)",
        "zona": "AGRESSÕES FÍSICO-QUÍMICAS",
        "definicao": (
            "Contato prolongado com óleo ou derivado de petróleo. O flanco ABSORVE e fica "
            "ESTUFADO para fora e manchado. Olhando o pneu de cima, a lateral aparece inchada."
        ),
        "sinais_visuais": [
            "flanco abaulado/estufado para fora, deformando o perfil da lateral",
            "manchas escuras, borracha amolecida ou brilhante de óleo",
            "óleo ainda presente na lateral",
        ],
        "nao_confundir": {
            "52H": "estufamento por óleo é localizado e manchado; 52H é colapso por falta de ar",
        },
        "dica_foto": "Fotografar a lateral inteira, e uma foto de cima mostrando o estufamento.",
    },

    # ---------------------------------- TALÃO ---------------------------------
    "70J": {
        "titulo": "Desenrolamento do retorno da lona carcaça no talão",
        "zona": "TALÃO",
        "definicao": (
            "A LONA DE REFORÇO DO TALÃO se desprende do encordoamento do talão. Causa: "
            "aquecimento abrupto e excessivo. Visual: talão muito destruído, com o dano "
            "chegando a afetar uma parte do flanco."
        ),
        "sinais_visuais": [
            "lona de reforço solta/desenrolada saindo do talão",
            "talão aberto e destruído, borracha queimada/escurecida",
            "dano sobe para a parte baixa do flanco",
        ],
        "nao_confundir": {
            "70L": "quando o que rompeu foram os CORDONÉIS (encordoamento) → 70L",
            "70R": "se é apenas rachadura na zona baixa → 70R",
            "71J/71K": "se a marca é de ferramenta de montagem → 71J/71K",
        },
    },
    "70L": {
        "titulo": "Ruptura da lona carcaça no talão",
        "zona": "TALÃO",
        "definicao": (
            "Parecido com o 70J, porém aqui há ROMPIMENTO DOS CORDONÉIS (encordoamento) do talão."
        ),
        "sinais_visuais": [
            "cordonéis/arames do talão partidos e à mostra",
            "talão perdeu integridade estrutural no ponto de ruptura",
        ],
        "nao_confundir": {
            "70J": "lona de reforço desprendida por aquecimento, cordonéis inteiros → 70J",
        },
    },
    "70K": {
        "titulo": "Separações no talão / rachadura circunferencial acima do talão",
        "zona": "TALÃO / FLANCO BAIXO",
        "definicao": (
            "RACHADURA CIRCUNFERENCIAL no flanco, bem acima do talão. Pode ser pequena ou "
            "grande. CUIDADO para não confundir com 45F: essa rachadura também é horizontal, "
            "mas é uma RACHADURA de verdade — borda ondulada/oscilante, como parede rachada. "
            "No 45F o corte lateral é RETILÍNEO."
        ),
        "sinais_visuais": [
            "trinca acompanhando a circunferência, acima do talão",
            "borda irregular, oscilante, borracha aberta por fadiga",
        ],
        "nao_confundir": {
            "45F": "corte retilíneo e limpo → 45F",
            "70R": "se a rachadura está na ZONA BAIXA do talão (pé de galinha) → 70R",
        },
    },
    "70Q": {
        "titulo": "Alteração na zona baixa (sem rachadura)",
        "zona": "TALÃO",
        "definicao": (
            "NÃO há dano no talão. Simplesmente a ZONA DO TALÃO ABAIXA/afunda, o que torna o "
            "pneu mais suscetível ao 70R. Mas NÃO há rachadura na zona baixa do talão."
        ),
        "sinais_visuais": [
            "zona baixa rebaixada/afundada, perfil alterado",
            "nenhuma trinca, nenhum pé de galinha",
        ],
        "nao_confundir": {
            "70R": "existe rachadura na zona baixa → 70R (a rachadura é o divisor)",
        },
    },
    "70R": {
        "titulo": "Rachadura na zona baixa",
        "zona": "TALÃO",
        "definicao": (
            "RACHADURA na ZONA BAIXA DO TALÃO — o famoso PÉ DE GALINHA no talão. Pode ser "
            "grande ou pequena. É justamente a rachadura que diferencia do 70Q."
        ),
        "sinais_visuais": [
            "trincas ramificadas (pé de galinha) na base do talão",
            "fissuras curtas e múltiplas na zona baixa",
        ],
        "nao_confundir": {
            "70Q": "zona baixa apenas afundada, sem trinca → 70Q",
            "70K": "rachadura circunferencial ACIMA do talão, no flanco → 70K",
        },
    },
    "71J": {
        "titulo": "Agressões durante montagem/desmontagem",
        "zona": "TALÃO",
        "definicao": (
            "O borracheiro danifica o talão na montagem ou desmontagem. Fica bem próximo da "
            "parte INTERNA do pneu, no ALTO DO TALÃO, onde fica o assentamento da roda que "
            "faz a vedação."
        ),
        "sinais_visuais": [
            "marca de alavanca/ferramenta, borracha rasgada por pressão pontual",
            "dano no alto do talão, lado interno, na área de vedação",
            "zona baixa do talão SEM afundamento",
        ],
        "nao_confundir": {
            "71K": "se a zona baixa do talão estiver FUNDA (talão já aquecido/fragilizado) → 71K",
        },
    },
    "71K": {
        "titulo": "Agressão em montagem/desmontagem sobre talão já fragilizado",
        "zona": "TALÃO",
        "definicao": (
            "Muito parecido com o 71J. O que diferencia é o ESTADO DO TALÃO: pneu já aquecido "
            "e fragilizado quebra mais facilmente na montagem/desmontagem. CRITÉRIO PRÁTICO: "
            "olhar a ZONA BAIXA do talão — se estiver FUNDA, usar 71K; se não, usar 71J."
        ),
        "sinais_visuais": [
            "marca de ferramenta + zona baixa nitidamente afundada",
            "borracha do talão ressecada/aquecida, quebradiça",
        ],
        "nao_confundir": {
            "71J": "zona baixa normal → 71J",
        },
    },
}


# =============================================================================
# 2) ÁRVORE DE DECISÃO — ordem de verificação (Manual FVU MICHELIN, pág. 4)
# =============================================================================

ARVORE_DECISAO = """
ORDEM OBRIGATÓRIA DE ANÁLISE (Manual FVU MICHELIN):
1) Identificar o pneu (medida, número de fogo, nº de reformas)
2) Analisar a BANDA DE RODAGEM
3) Analisar o FLANCO
4) Analisar os TALÕES
5) Analisar o INTERIOR

REGRA MESTRA: havendo mais de um dano, classificar pelo dano que REALMENTE
sucateou o pneu, não pelo mais visível.

ÁRVORE DE DECISÃO RÁPIDA:

A) BANDA / TOPO
   A1. Cinta ou aço APARENTE na banda? .................................... 48D
       (mesmo com desgaste irregular acentuado — 48D tem prioridade sobre 45D)
   A2. Corte atravessando a banda de flanco a flanco (impacto em obstáculo)? .. 45B
   A3. Um lado dos sulcos nitidamente mais baixo, SEM cinta aparente? ....... 45D
   A4. Pneu SEM reforma, desenho original, com sulco reaberto por lâmina
       fora de norma (profundidade/largura erradas, TWI destruído,
       lona de trabalho exposta pela lâmina)? ............................. 45N
   A5. Pneu SEM reforma, desenho original, banda apta e nunca ressulcada? ... 45R

B) FLANCO
   B1. Corte horizontal PEQUENO e retilíneo + ranhuras? .................... 45F
   B2. Corte GRANDE, arrancou pedaço do flanco? ............................ 45G
   B3. Dano REPETIDO/circunferencial no mesmo ponto (peça solta, pedra
       entre duplos), com perfuração ou fissura? ........................... 46F
   B4. Rachadura CIRCUNFERENCIAL de borda ondulada acima do talão? ......... 70K
   B5. Flanco estufado para fora + manchas de óleo? ........................ 75A

C) INTERIOR / PRESSÃO
   C1. Só marcas/ranhuras/rachaduras no liner (butil), pneu íntegro? ....... 52B
   C2. Pó de borracha dentro, liner esfarelado, flanco colapsado
       ou destruído externamente? .......................................... 52H

D) TALÃO
   D1. Lona de reforço do talão DESPRENDIDA, talão destruído por
       aquecimento, dano atingindo o flanco? ............................... 70J
   D2. CORDONÉIS/encordoamento do talão ROMPIDOS? .......................... 70L
   D3. Rachadura na ZONA BAIXA (pé de galinha)? ............................ 70R
   D4. Zona baixa apenas ABAIXADA/afundada, SEM rachadura? ................. 70Q
   D5. Marca de ferramenta no alto do talão (lado interno, área de vedação):
        - zona baixa NORMAL ................................................ 71J
        - zona baixa FUNDA ................................................. 71K
"""


# =============================================================================
# 3) PARES CONFUNDÍVEIS — critério único de desempate
# =============================================================================

PARES_CONFUNDIVEIS = [
    ("45D", "48D", "Cinta aparente? SIM=48D / NÃO=45D. Se desgaste irregular atingiu a cinta → 48D obrigatório."),
    ("45F", "45G", "Tamanho: corte pequeno e retilíneo=45F / corte grande com pedaço arrancado=45G."),
    ("45F", "70K", "Aspecto da borda: corte retilíneo e limpo=45F / rachadura ondulada circunferencial=70K."),
    ("45F", "46F", "Repetição: dano único=45F / dano repetido no mesmo ponto, circunferencial=46F."),
    ("45N", "45R", "Ressulcou errado=45N / não ressulcou=45R. Ambos só em pneu SEM reforma."),
    ("52B", "52H", "Pó interno / colapso do flanco? SIM=52H / apenas marcas no liner=52B."),
    ("70J", "70L", "O que falhou: lona de reforço desprendida por calor=70J / cordonéis rompidos=70L."),
    ("70Q", "70R", "Rachadura na zona baixa? SIM=70R / apenas afundamento=70Q."),
    ("70K", "70R", "Altura: rachadura acima do talão, no flanco=70K / na zona baixa do talão=70R."),
    ("71J", "71K", "Zona baixa do talão: normal=71J / funda (talão aquecido e fragilizado)=71K."),
]


# =============================================================================
# 4) PROMPT — construtor
# =============================================================================

def _bloco_glossario() -> str:
    partes = []
    for cod, g in GLOSSARIO_FVU.items():
        linhas = [f"### {cod} — {g['titulo']}  [{g['zona']}]"]
        linhas.append(f"DEFINIÇÃO: {g['definicao']}")
        linhas.append("O QUE VER NA FOTO: " + "; ".join(g["sinais_visuais"]) + ".")
        if g.get("parametros_michelin"):
            linhas.append("PARÂMETROS MICHELIN: " + "; ".join(g["parametros_michelin"]) + ".")
        if g.get("nao_confundir"):
            nc = " | ".join(f"vs {k}: {v}" for k, v in g["nao_confundir"].items())
            linhas.append("NÃO CONFUNDIR — " + nc)
        if g.get("pre_requisito"):
            linhas.append(f"PRÉ-REQUISITO: {g['pre_requisito']} (pneu sem reforma).")
        partes.append("\n".join(linhas))
    return "\n\n".join(partes)


def _bloco_pares() -> str:
    return "\n".join(f"- {a} x {b}: {c}" for a, b, c in PARES_CONFUNDIVEIS)


def montar_prompt_inspecao(fvu_data, n_reformas_por_fogo=None) -> str:
    """
    fvu_data: lista de dicts {codigo, categoria, descricao, causa, acao} da planilha.
    n_reformas_por_fogo: dict opcional {fogo: nº de reformas} vindo do relatório HTML,
                         usado para liberar/bloquear 45N e 45R.
    """
    linhas_fvu = "\n".join(
        f'  {{"codigo": "{x["codigo"]}", "descricao": "{x["descricao"]}", "categoria": "{x["categoria"]}"}}'
        for x in fvu_data
    )

    bloco_reformas = ""
    if n_reformas_por_fogo:
        pares = ", ".join(f"{k}={v}" for k, v in n_reformas_por_fogo.items())
        bloco_reformas = (
            "\nNÚMERO DE REFORMAS POR FOGO (do relatório): " + pares +
            "\nPneu com reforma >= 1 NÃO pode receber 45N nem 45R.\n"
        )

    return f"""
Você é um inspetor técnico sênior de pneus de frota pesada, treinado no Manual de FVU
MICHELIN e no Manual de Ressulcagem MICHELIN. Sua classificação deve reproduzir
EXATAMENTE o critério do inspetor descrito no glossário abaixo — ele tem prioridade
sobre qualquer interpretação genérica.

TAREFA para cada pneu presente nas fotos:
1. Ler o número de Fogo escrito a giz.
2. Listar em "arquivos_fotos" os nomes EXATOS dos arquivos que pertencem a esse pneu.
3. Identificar marca e profundidade de sulco aproximada.
4. Descrever objetivamente o que você VÊ (zona, forma, tamanho, borda, exposição de aço),
   sem já nomear o código.
5. Só então escolher o código FVU, seguindo a ordem de análise e a árvore de decisão.
6. Preencher "evidencia" explicando qual sinal visual decidiu o código, e
   "descartados" com 1 a 2 códigos parecidos que você descartou e por quê.

{ARVORE_DECISAO}
{bloco_reformas}
==================== GLOSSÁRIO DO INSPETOR (AUTORIDADE MÁXIMA) ====================
{_bloco_glossario()}

==================== DESEMPATE ENTRE CÓDIGOS PARECIDOS ====================
{_bloco_pares()}

==================== REGRAS DURAS (NUNCA VIOLAR) ====================
R1. Cinta/aço aparente na banda ⇒ 48D, mesmo com desgaste irregular. Nunca 45D, nunca 45B.
R2. 45B exige corte na BANDA atravessando de flanco a flanco. Sem esse corte, não é 45B.
R3. 45N e 45R só existem em pneu SEM reforma (nº de reformas = 0) e com desenho original.
R4. 45N = ressulcado fora do padrão. 45R = não ressulcado. Nunca os dois.
R5. Rachadura na zona baixa do talão ⇒ 70R. Sem rachadura, só afundamento ⇒ 70Q.
R6. Pó de borracha interno ou flanco colapsado ⇒ 52H. Apenas marcas no liner ⇒ 52B.
R7. Marca de ferramenta no talão: zona baixa funda ⇒ 71K, senão ⇒ 71J.
R8. Corte retilíneo no flanco ⇒ 45F/45G. Rachadura ondulada circunferencial ⇒ 70K.
R9. Se as fotos não mostram a zona necessária para decidir, responda confianca="Baixa"
    e informe em "foto_faltante" qual foto resolveria (ex.: "interior do pneu",
    "zona baixa do talão", "lateral de cima").
R10. Havendo mais de um dano, classifique o que SUCATEOU o pneu, não o mais chamativo.

TABELA FVU OFICIAL DA EMPRESA (use o código exatamente como escrito aqui):
[
{linhas_fvu}
]

Responda SOMENTE com um array JSON válido, sem markdown e sem texto fora do JSON:
[
  {{
    "fogo": "string",
    "marca": "string",
    "sulco": "string",
    "arquivos_fotos": ["arquivo1.jpg"],
    "zona_dano": "BANDA | FLANCO | TALAO | INTERIOR | FISICO_QUIMICO | NENHUMA",
    "cinta_aparente": true,
    "ressulcado": true,
    "descricao_dano_ia": "descrição visual objetiva, sem citar código",
    "codigo_fvu_sugerido": "ex: 45D ou OK",
    "evidencia": "qual sinal visual decidiu o código",
    "descartados": [{{"codigo": "45D", "motivo": "cinta aparente"}}],
    "foto_faltante": "",
    "confianca": "Alta | Média | Baixa"
  }}
]
"""


# =============================================================================
# 5) MATCHER POR PALAVRAS-CHAVE (fallback quando a IA não devolve código válido)
# =============================================================================

FVU_KEYWORDS = {
    "45B": {
        "pos": ["flanco a flanco", "de ombro a ombro", "corte transversal", "corte atravessado",
                "atravessa a banda", "ruptura banda", "banda rompida", "corte profundo banda",
                "impacto obstáculo", "meio-fio", "meio fio", "cabeceira", "cabeçeira",
                "corte na banda de rodagem", "rasgo banda", "choque no topo"],
        "neg": ["cinta aparente", "aço aparente", "careca", "calvo", "liso", "sem sulco",
                "talão", "ressulc", "desgaste irregular"],
    },
    "45F": {
        "pos": ["corte horizontal flanco", "corte retilíneo", "corte pequeno flanco",
                "corte lateral", "ranhura flanco", "ferida flanco", "corte flanco",
                "incisão flanco", "objeto cortante flanco", "corte limpo lateral"],
        "neg": ["talão", "ressulc", "banda de rodagem", "cinta", "arrancou pedaço",
                "circunferencial", "rachadura", "ondulad", "pedaço faltando"],
    },
    "45G": {
        "pos": ["corte grande flanco", "rasgo flanco", "arrancou pedaço", "pedaço arrancado",
                "pedaço faltando", "cratera flanco", "dano extenso flanco",
                "corte profundo flanco", "lesão grande flanco", "choque no flanco"],
        "neg": ["talão", "ressulc", "banda de rodagem", "cinta", "pequeno", "retilíneo",
                "rachadura", "circunferencial"],
    },
    "45N": {
        "pos": ["ressulcagem incorreta", "ressulcagem fora do padrão", "ressulcagem mal executada",
                "ressulcagem irregular", "ressulco incorreto", "sulco fora da norma",
                "ressulcagem inadequada", "lâmina", "twi destruído", "indicador de desgaste removido",
                "ressulcado profundo demais", "sulco reaberto torto", "ressulcagem profunda"],
        "neg": ["não ressulcado", "sem ressulcagem", "reforma", "recapado", "recauchutado"],
    },
    "45R": {
        "pos": ["não ressulcado", "sem ressulcagem", "ressulcagem não realizada",
                "falta de ressulcagem", "ressulcagem ausente", "deveria ter sido ressulcado",
                "desenho original gasto", "não foi ressulcado"],
        "neg": ["incorreta", "mal executada", "fora do padrão", "reforma", "recapado",
                "lâmina", "cinta aparente"],
    },
    "45D": {
        "pos": ["desgaste irregular", "desgaste de um lado", "sulco mais baixo de um lado",
                "desgaste assimétrico", "ombro desgastado", "diferença de sulco",
                "desgaste desigual", "um lado mais desgastado", "desgaste de bordo a bordo"],
        "neg": ["cinta aparente", "cinta exposta", "aço aparente", "careca", "calvo",
                "liso", "sem sulco"],
    },
    "46F": {
        "pos": ["agressão repetida", "dano circunferencial flanco", "marcas repetidas flanco",
                "pedra entre duplos", "peça solta", "perfuração circunferencial",
                "fissura circunferencial flanco", "abrasão flanco", "atrito contínuo flanco",
                "trilha de dano flanco", "raspando o pneu"],
        "neg": ["talão", "banda de rodagem", "ressulc", "corte único", "corte pontual"],
    },
    "48D": {
        "pos": ["cinta aparente", "cinta exposta", "cinta visível", "fio de aço exposto",
                "aço aparente", "aço exposto", "careca", "calvo", "liso", "sem sulco",
                "banda lisa", "desgaste até a cinta", "lona de topo exposta",
                "desgaste extremo", "desgaste total", "limite de desgaste", "twi atingido"],
        "neg": ["talão", "flanco estufado", "ressulcagem incorreta"],
    },
    "52B": {
        "pos": ["baixa pressão", "liner", "butil", "butílico", "dano interno",
                "ranhura interna", "rachadura interna", "flexão", "marca interna",
                "revestimento interno marcado"],
        "neg": ["pó", "esfarel", "sem ar", "rodou vazio", "colapsado", "sem estrutura"],
    },
    "52H": {
        "pos": ["rodou sem ar", "pó interno", "pó de borracha", "borracha esfarelada",
                "esfarelamento", "flanco sem estrutura", "sem ar", "rodou vazio",
                "flanco colapsado", "pneu murcho", "pressão zero", "liner destruído",
                "destruído externamente"],
        "neg": ["apenas marcas internas", "somente ranhura interna"],
    },
    "70J": {
        "pos": ["lona de reforço desprendida", "reforço do talão desprendido",
                "desenrolamento", "retorno da lona", "talão destruído", "aquecimento",
                "talão aberto", "lona solta talão", "dano talão e flanco", "queimado"],
        "neg": ["cordonéis rompidos", "pé de galinha", "zona baixa", "montagem", "desmontagem",
                "alavanca", "rachadura circunferencial"],
    },
    "70K": {
        "pos": ["rachadura circunferencial", "trinca circunferencial", "rachadura acima do talão",
                "rachadura ondulada", "rachadura oscilante", "fissura circunferencial lateral",
                "parede rachada", "rachadura horizontal flanco"],
        "neg": ["corte retilíneo", "zona baixa", "pé de galinha", "montagem", "banda",
                "cordonéis"],
    },
    "70L": {
        "pos": ["cordonéis rompidos", "cordoéis", "encordoamento rompido", "arames rompidos",
                "arames do talão partidos", "ruptura da lona carcaça no talão",
                "encordoamento partido"],
        "neg": ["rachadura", "zona baixa", "montagem", "desmontagem", "lona de reforço solta"],
    },
    "70Q": {
        "pos": ["zona baixa abaixada", "talão afundado", "zona baixa deformada",
                "afundamento do talão", "talão baixo", "alteração na zona baixa",
                "deformação do talão"],
        "neg": ["rachadura", "trinca", "fissura", "pé de galinha", "ruptura", "cordonéis",
                "alavanca", "ferramenta"],
    },
    "70R": {
        "pos": ["pé de galinha", "rachadura zona baixa", "trinca zona baixa",
                "fissura zona baixa", "rachadura base talão", "trincas ramificadas talão",
                "rachadura na zona do talão"],
        "neg": ["circunferencial no flanco", "montagem", "desmontagem", "cordonéis",
                "lona de reforço"],
    },
    "71J": {
        "pos": ["montagem", "desmontagem", "marca de ferramenta", "alavanca",
                "assentamento da roda", "área de vedação", "alto do talão",
                "borracheiro danificou", "ferramental"],
        "neg": ["zona baixa funda", "talão aquecido", "pé de galinha", "cordonéis",
                "circunferencial"],
    },
    "71K": {
        "pos": ["talão aquecido", "talão fragilizado", "zona baixa funda",
                "zona baixa profunda", "talão fundo", "quebra do talão fragilizado",
                "borracha ressecada talão"],
        "neg": ["pé de galinha", "rachadura", "circunferencial", "cordonéis"],
    },
    "75A": {
        "pos": ["flanco estufado", "estufamento", "lateral estufada", "flanco inchado",
                "óleo", "oleoso", "derivado de petróleo", "manchado", "borracha amolecida",
                "absorção de óleo", "graxa"],
        "neg": ["corte", "rachadura", "cinta aparente", "talão", "pé de galinha"],
    },
}

# aliases para tolerar variações de escrita vindas da planilha
_ALIASES = {"71k": "71K", "45n": "45N", "45r": "45R"}


def _norm(codigo: str) -> str:
    c = (codigo or "").strip()
    return _ALIASES.get(c, c.upper())


def encontrar_fvu_por_descricao(descricao_ia, fvu_data):
    """Fallback textual: pontua a descrição da IA contra as palavras-chave."""
    if not descricao_ia or not fvu_data:
        return fvu_data[0] if fvu_data else None

    desc = descricao_ia.lower()
    melhor, max_score = None, -999

    for item in fvu_data:
        kw = FVU_KEYWORDS.get(_norm(item["codigo"]), {})
        score = 0
        for termo in kw.get("pos", []):
            if termo in desc:
                score += 3
        for termo in kw.get("neg", []):
            if termo in desc:
                score -= 4
        texto_fvu = (item.get("descricao", "") + " " + item.get("categoria", "")).lower()
        for palavra in {p for p in texto_fvu.split() if len(p) > 4}:
            if palavra in desc:
                score += 1
        if score > max_score:
            max_score, melhor = score, item

    return melhor if melhor and max_score > 0 else fvu_data[0]


# =============================================================================
# 6) REGRAS DETERMINÍSTICAS — corrigem a IA depois da resposta
# =============================================================================

def _tem(desc: str, *termos) -> bool:
    return any(t in desc for t in termos)


def aplicar_regras_deterministicas(item: dict, n_reformas="0") -> tuple:
    """
    Recebe o dict devolvido pela IA e devolve (codigo_corrigido, lista_de_ajustes).
    Aplica as regras duras que a IA costuma errar.
    """
    codigo = _norm(str(item.get("codigo_fvu_sugerido", "")))
    desc = (str(item.get("descricao_dano_ia", "")) + " " +
            str(item.get("evidencia", ""))).lower()
    ajustes = []

    try:
        reformas = int(str(n_reformas).strip() or "0")
    except ValueError:
        reformas = 0

    cinta = bool(item.get("cinta_aparente")) or _tem(
        desc, "cinta aparente", "cinta exposta", "aço aparente", "aço exposto",
        "lona de topo exposta", "careca", "calvo"
    )

    # R1 — cinta aparente sempre 48D
    if cinta and codigo in {"45D", "45B", "45A", "45R", "45N"}:
        ajustes.append(f"{codigo}→48D: cinta/aço aparente na banda (R1).")
        codigo = "48D"

    # R3 — 45N/45R só em pneu sem reforma
    if codigo in {"45N", "45R"} and reformas >= 1:
        alternativa = "48D" if cinta else "45D" if _tem(desc, "desgaste irregular") else "48D"
        ajustes.append(f"{codigo}→{alternativa}: pneu com {reformas} reforma(s), não é ressulcável (R3).")
        codigo = alternativa

    # R4 — coerência ressulcado x código
    ressulcado = item.get("ressulcado")
    if codigo == "45R" and ressulcado is True:
        ajustes.append("45R→45N: há sulco reaberto por lâmina (R4).")
        codigo = "45N"
    if codigo == "45N" and ressulcado is False:
        ajustes.append("45N→45R: não há sinal de ressulcagem (R4).")
        codigo = "45R"

    # R5 — 70Q x 70R
    if codigo == "70Q" and _tem(desc, "rachadura", "trinca", "fissura", "pé de galinha"):
        ajustes.append("70Q→70R: há rachadura na zona baixa (R5).")
        codigo = "70R"
    if codigo == "70R" and not _tem(desc, "rachadura", "trinca", "fissura", "pé de galinha"):
        if _tem(desc, "afund", "abaixad", "deformad"):
            ajustes.append("70R→70Q: apenas afundamento, sem rachadura (R5).")
            codigo = "70Q"

    # R6 — 52B x 52H
    if codigo == "52B" and _tem(desc, "pó", "esfarel", "colapsad", "sem estrutura", "rodou sem ar"):
        ajustes.append("52B→52H: pó interno / colapso do flanco (R6).")
        codigo = "52H"

    # R7 — 71J x 71K
    if codigo == "71J" and _tem(desc, "zona baixa funda", "zona baixa profunda",
                                "talão aquecido", "talão fragilizado"):
        ajustes.append("71J→71K: zona baixa funda / talão fragilizado (R7).")
        codigo = "71K"
    if codigo == "71K" and _tem(desc, "zona baixa normal", "zona baixa preservada"):
        ajustes.append("71K→71J: zona baixa sem afundamento (R7).")
        codigo = "71J"

    # R8 — 45F x 70K
    if codigo == "45F" and _tem(desc, "circunferencial", "ondulad", "oscilant", "parede rachada"):
        ajustes.append("45F→70K: rachadura circunferencial ondulada, não corte retilíneo (R8).")
        codigo = "70K"

    # 45F x 45G pelo tamanho
    if codigo == "45F" and _tem(desc, "arrancou pedaço", "pedaço arrancado", "pedaço faltando",
                                "rasgo extenso", "cratera"):
        ajustes.append("45F→45G: corte grande com perda de borracha.")
        codigo = "45G"

    # R2 — 45B exige corte atravessado na banda
    if codigo == "45B" and not _tem(desc, "flanco a flanco", "ombro a ombro", "transversal",
                                    "atravess", "rompeu a banda", "ruptura"):
        if _tem(desc, "furo", "prego", "parafuso", "perfuração isolada"):
            ajustes.append("45B→45A: perfuração isolada, sem corte atravessado (R2).")
            codigo = "45A"

    return codigo, ajustes
