# fvu_keywords.py

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

ARVORE_DECISAO = """
ORDEM OBRIGATÓRIA DE ANÁLISE (Manual FVU MICHELIN):
1) Identificar o pneu (medida, número de fogo, nº de reformas)
2) Analisar a BANDA DE RODAGEM
3) Analisar o FLANCO
4) Analisar os TALÕES
5) Analisar o INTERIOR

REGRA MESTRA: havendo mais de um dano, classificar pelo dano que REALMENTE sucateou o pneu, não pelo mais visível.

ÁRVORE DE DECISÃO RÁPIDA:
A) BANDA / TOPO
   A1. Cinta ou aço APARENTE na banda? .................................... 48D (tem prioridade sobre 45D)
   A2. Corte atravessando a banda de flanco a flanco (impacto em obstáculo)? .. 45B
   A3. Um lado dos sulcos nitidamente mais baixo, SEM cinta aparente? ....... 45D
   A4. Pneu SEM reforma, desenho original, com sulco reaberto por lâmina fora de norma (profundidade/largura erradas, TWI destruído, lona de trabalho exposta)? ... 45N
   A5. Pneu SEM reforma, desenho original, banda apta e nunca ressulcada? ... 45R

B) FLANCO
   B1. Corte horizontal PEQUENO e retilíneo + ranhuras? .................... 45F
   B2. Corte GRANDE, arrancou pedaço do flanco? ............................ 45G
   B3. Dano REPETIDO/circunferencial no mesmo ponto (peça solta, pedra entre duplos)? ... 46F
   B4. Rachadura CIRCUNFERENCIAL de borda ondulada acima do talão? ......... 70K
   B5. Flanco estufado para fora + manchas de óleo? ........................ 75A

C) INTERIOR / PRESSÃO
   C1. Só marcas/ranhuras/rachaduras no liner (butil), pneu íntegro? ....... 52B
   C2. Pó de borracha dentro, liner esfarelado, flanco colapsado ou destruído externamente? ... 52H

D) TALÃO
   D1. Lona de reforço do talão DESPRENDIDA, talão destruído por aquecimento? .. 70J
   D2. CORDONÉIS/encordoamento do talão ROMPIDOS? .......................... 70L
   D3. Rachadura na ZONA BAIXA (pé de galinha)? ............................ 70R
   D4. Zona baixa apenas ABAIXADA/afundada, SEM rachadura? ................. 70Q
   D5. Marca de ferramenta no alto do talão (lado interno, área de vedação):
        - zona baixa NORMAL ................................................ 71J
        - zona baixa FUNDA ................................................. 71K
"""

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

def gerar_guia_prompt_fvu():
    """Gera o texto completo contendo a Árvore de Decisão, Pares Confundíveis e Glossário para o prompt do Gemini."""
    texto = []
    texto.append("=== ÁRVORE DE DECISÃO OBRIGATÓRIA DA MICHELIN ===")
    texto.append(ARVORE_DECISAO)
    
    texto.append("\n=== REGRAS DE DESEMPATE E PARES CONFUNDÍVEIS ===")
    for c1, c2, regra in PARES_CONFUNDIVEIS:
        texto.append(f"• {c1} vs {c2}: {regra}")
        
    texto.append("\n=== GLOSSÁRIO TÉCNICO DE INSPEÇÃO VISUAL ===")
    for cod, data in GLOSSARIO_FVU.items():
        texto.append(f"CÓDIGO {cod}: {data['titulo']}")
        texto.append(f"  Região: {data['zona']}")
        texto.append(f"  Definição: {data['definicao']}")
        texto.append("  Sinais Visuais:")
        for s in data["sinais_visuais"]:
            texto.append(f"    - {s}")
        if "nao_confundir" in data:
            texto.append("  NÃO CONFUNDIR:")
            for k, v in data["nao_confundir"].items():
                texto.append(f"    - Com {k}: {v}")
        if "pre_requisito" in data:
            texto.append(f"  Pré-requisito: {data['pre_requisito']}")
        texto.append("")
        
    return "\n".join(texto)

def gerar_prompt_sistema_ia():
    """Gera o prompt completo de sistema integrando o guia técnico e o formato de saída JSON para a IA."""
    guia_tecnico = gerar_guia_prompt_fvu()
    return f"""Você é um assistente especializado em análise de pneus para uma frota logística, seguindo rigorosamente o Manual FVU da Michelin.
Sua tarefa é analisar a imagem enviada (que contém o código de classificação manuscrito e o número de série/fogo do pneu) e extrair os dados necessários.

{guia_tecnico}

INSTRUÇÕES DE SAÍDA:
- Identifique o código FVU correto com base na árvore de decisão e glossário.
- Extraia o ID/número de série do pneu visível na imagem.
- Retorne APENAS um objeto JSON válido, sem blocos de código markdown adicionais, estruturado exatamente assim:
{{
  "codigo_fvu": "string com o código (ex: 45B, 48D) ou null",
  "id_pneu": "string com o número de série/fogo ou null",
  "confianca": "alta/media/baixa",
  "observacoes": "breve descrição técnica justificando o código escolhido"
}}
"""

def encontrar_fvu_por_descricao(descricao_ia, fvu_data):
    """Encontra o código FVU na planilha correspondente à descrição gerada pela IA."""
    if not descricao_ia or not fvu_data:
        return fvu_data[0] if fvu_data else None

    desc_lower = descricao_ia.lower()
    melhor_match = None
    max_score = -999

    for item in fvu_data:
        codigo = item["codigo"].strip().upper()
        info = GLOSSARIO_FVU.get(codigo, {})
        score = 0
        
        # Pontua por sinais visuais presentes
        for sinal in info.get("sinais_visuais", []):
            for termo in sinal.split():
                if len(termo) > 3 and termo.lower() in desc_lower:
                    score += 2

        texto_fvu = (item["descricao"] + " " + item["categoria"]).lower()
        for palavra in [p for p in texto_fvu.split() if len(p) > 3]:
            if palavra in desc_lower:
                score += 1
                
        if score > max_score:
            max_score = score
            melhor_match = item

    return melhor_match if melhor_match and max_score > 0 else fvu_data[0]
