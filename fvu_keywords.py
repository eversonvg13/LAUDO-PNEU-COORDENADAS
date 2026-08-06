# fvu_keywords.py

FVU_KEYWORDS = {
    # 45B — motorista sobe em obstáculo alto (meio-fio, cabeçeira de ponte, pedra)
    # com a BANDA DE RODAGEM. Corte atravessa de flanco a flanco na banda. Corte profundo transversal.
    "45B": {
        "pos": ["corte banda", "corte transversal", "corte de flanco a flanco", "ruptura banda",
                "banda rompida", "corte profundo banda", "impacto obstáculo", "meio-fio banda",
                "cabeçeira", "corte na banda de rodagem", "rasgo banda", "objeto banda"],
        "neg": ["flanco", "talão", "ressulc", "desgaste", "liso", "careca", "calvo",
                "sem sulco", "cinta", "irregular", "rachadura flanco"],
    },
    # 45F — corte HORIZONTAL pequeno no flanco, geralmente único e retilíneo, com algumas ranhuras.
    "45F": {
        "pos": ["corte horizontal flanco", "corte retilíneo flanco", "corte pequeno flanco",
                "corte lateral", "ranhura flanco", "ferida flanco", "furo flanco",
                "corte flanco", "incisão flanco", "objeto cortante flanco"],
        "neg": ["talão", "ressulc", "banda de rodagem", "desgaste", "cinta",
                "grande", "arrancou", "pedaço", "circunferencial", "rachadura"],
    },
    # 45G — parecido com 45F mas o corte é MAIOR, pode arrancar pedaços do flanco.
    "45G": {
        "pos": ["corte grande flanco", "rasgo flanco", "arrancou pedaço flanco",
                "dano extenso flanco", "corte profundo flanco", "flanco danificado gravemente",
                "pedaço arrancado flanco", "lesão grande flanco", "impacto flanco severo"],
        "neg": ["talão", "ressulc", "banda de rodagem", "desgaste", "cinta",
                "horizontal pequeno", "ranhura", "lonas expostas", "destruído", "rachadura"],
    },
    # 45N — ressulcagem EXECUTADA mas fora dos parâmetros do CONTRAN (profundidade/largura errada).
    # Só em pneu SEM reforma (desenho original do fabricante).
    "45N": {
        "pos": ["ressulcagem incorreta", "ressulcagem fora do padrão", "ressulcagem mal executada",
                "ressulcagem irregular", "ressulco incorreto", "frieza fora do padrão",
                "sulco fora da norma", "ressulcagem inadequada"],
        "neg": ["não ressulcado", "sem ressulcagem", "reforma"],
    },
    # 45R — NÃO realizou a ressulcagem quando deveria. Só em pneu SEM reforma.
    "45R": {
        "pos": ["não ressulcado", "sem ressulcagem", "ressulcagem não realizada",
                "pneu não ressulcado", "falta de ressulcagem", "ressulcagem ausente",
                "deveria ter sido ressulcado"],
        "neg": ["incorreta", "mal executada", "fora do padrão", "reforma"],
    },
    # 45D — desgaste IRREGULAR: um lado da banda mais desgastado que o outro (diferença nos sulcos).
    # NÃO há cinta aparente. Se atingiu a cinta → obrigatoriamente 48D.
    "45D": {
        "pos": ["desgaste irregular", "desgaste de um lado", "sulco mais baixo de um lado",
                "desgaste assimétrico", "ombro desgastado", "desgaste lateral",
                "diferença de sulco", "alinhamento", "desgaste desigual", "um lado mais desgastado"],
        "neg": ["cinta aparente", "cinta exposta", "cinta visível", "liso", "careca",
                "sem sulco", "calvo", "desgaste total", "extremo"],
    },
    # 46F — agressões REPETIDAS no mesmo ponto do flanco (circunferenciais).
    # Ex: peça do veículo solta rodando no pneu, ou pedra presa entre duplos.
    "46F": {
        "pos": ["agressão repetida flanco", "dano circunferencial flanco", "marcas repetidas flanco",
                "pedra entre duplos", "peça solta contato pneu", "perfuração circunferencial",
                "fissura circunferencial flanco", "ranhuras circunferenciais", "dano ao longo do flanco",
                "abrasão repetida flanco", "sulco circunferencial flanco"],
        "neg": ["talão", "banda de rodagem", "ressulc", "desgaste", "corte único", "corte pontual"],
    },
    # 48D — cintas/fios de aço APARENTES. Não necessariamente desgaste irregular nos sulcos.
    # Se desgaste irregular atingiu a cinta → também é 48D.
    "48D": {
        "pos": ["cinta aparente", "cinta exposta", "cinta visível", "fio de aço exposto",
                "aço aparente", "careca", "calvo", "liso", "sem sulco", "banda lisa",
                "desgaste até a cinta", "lona exposta banda", "desgaste extremo",
                "desgaste total banda", "sulco inexistente", "limite de desgaste",
                "indicador de desgaste", "desgaste excessivo"],
        "neg": ["flanco", "talão", "ressulc", "rachadura", "corte"],
    },
    # 52B — rodou com BAIXA PRESSÃO mas sem destruição externa visível.
    # Dano aparece INTERNAMENTE: ranhuras ou rachaduras no liner (butílico) interno.
    "52B": {
        "pos": ["baixa pressão", "liner danificado", "butílico danificado", "dano interno",
                "ranhura interna", "rachadura interna", "flexão por baixa pressão",
                "marca interna", "linha interna rachada", "butil rachado", "dano no liner"],
        "neg": ["sem ar", "vazio", "rodou vazio", "pó interno", "esfarelamento",
                "destruído externamente", "flanco sem estrutura"],
    },
    # 52H — rodou completamente SEM AR. Dano externo e/ou interno grave.
    # Internamente: pó (borracha esfarelada pela fricção). Externamente: flanco destruído sem estrutura.
    "52H": {
        "pos": ["rodou sem ar", "pó interno", "borracha esfarelada", "esfarelamento interno",
                "flanco sem estrutura", "sem ar", "vazio", "rodou vazio",
                "destruído externamente", "flanco colapsado", "fricção interna",
                "pneu murcho rodou", "pressão zero rodou"],
        "neg": ["baixa pressão", "dano somente interno", "liner", "butílico", "sobrecarga"],
    },
    # 70J — lona de REFORÇO DO TALÃO se desprende do encordoamento por aquecimento excessivo/abrupto.
    # Visualmente: talão muito destruído, dano se estende para parte do flanco. Aquecimento é a causa.
    "70J": {
        "pos": ["lona talão desprendida", "reforço talão desprendido", "encordoamento talão",
                "talão destruído", "aquecimento talão", "separação lona talão",
                "talão aberto", "lona reforço solta", "talão danificado gravemente",
                "dano talão e flanco", "talão afetado flanco"],
        "neg": ["rachadura", "trinca", "crack", "montagem", "desmontagem", "alavanca",
                "cordoeis rompidos", "zona baixa"],
    },
    # 70K — rachadura CIRCUNFERENCIAL no flanco bem acima do talão.
    # Parece com 45F mas é uma rachadura oscilante (como parede rachada), não corte retilíneo.
    "70K": {
        "pos": ["rachadura circunferencial flanco", "trinca circunferencial flanco",
                "rachadura horizontal flanco", "rachadura oscilante flanco",
                "rachadura acima talão", "fissura circunferencial lateral",
                "rachadura parede flanco", "crack circunferencial flanco"],
        "neg": ["corte retilíneo", "corte pontual", "talão", "zona baixa", "montagem",
                "pequeno corte", "ranhura", "banda"],
    },
    # 70L — rompimento dos CORDOÉIS (encordoamento) do talão. Parecido com 70J mas aqui os cordoéis rompem.
    "70L": {
        "pos": ["cordoéis rompidos", "encordoamento rompido", "cordoéis talão rompidos",
                "ruptura cordoéis", "cordão talão rompido", "arames talão rompidos",
                "encordoamento talão partido"],
        "neg": ["rachadura", "trinca", "zona baixa", "montagem", "desmontagem",
                "lona reforço", "circunferencial"],
    },
    # 70Q — zona do talão ABAIXA/deforma sem rachadura. Deixa o pneu suscetível ao 70R.
    # NÃO há rachadura na zona baixa — apenas afundamento/deformação.
    "70Q": {
        "pos": ["zona talão abaixada", "talão afundado", "zona baixa deformada",
                "talão deformado sem rachadura", "afundamento talão", "talão baixo",
                "deformação zona talão", "talão sem rachadura deformado"],
        "neg": ["rachadura", "trinca", "crack", "fissura", "pé de galinha",
                "ruptura", "cordoéis", "montagem"],
    },
    # 70R — rachadura na ZONA BAIXA DO TALÃO. O famoso "pé de galinha no talão".
    # Diferencia do 70Q justamente por TER rachadura. Pode ser grande ou pequena.
    "70R": {
        "pos": ["rachadura zona baixa", "pé de galinha", "trinca zona baixa",
                "rachadura talão", "fissura zona baixa", "crack zona baixa talão",
                "rachadura base talão", "trinca base talão", "pé de galinha talão",
                "rachadura na zona do talão"],
        "neg": ["flanco", "circunferencial", "montagem", "desmontagem",
                "cordoéis", "lona reforço", "destruído"],
    },
    # 71J — borracheiro danifica o talão na montagem/desmontagem.
    # Fica próximo da parte interna do pneu, no alto do talão (assentamento/vedação da roda).
    # Talão em bom estado — zona baixa sem deformação funda.
    "71J": {
        "pos": ["dano montagem", "dano desmontagem", "talão danificado montagem",
                "marca ferramenta talão", "alavanca talão", "corte montagem",
                "dano assentamento roda", "região vedação talão danificada",
                "alto talão danificado", "ferramental talão"],
        "neg": ["rachadura", "trinca", "zona baixa funda", "aquecimento",
                "flanco", "circunferencial", "cordoéis"],
    },
    # 71K — parecido com 71J mas o talão já estava aquecido/fragilizado antes da montagem/desmontagem.
    # Diferencial: zona baixa do talão está FUNDA (deformada). Se zona baixa funda → 71K; se não → 71J.
    "71K": {
        "pos": ["talão aquecido", "talão fragilizado", "quebra talão aquecido",
                "zona baixa funda", "zona baixa deformada profunda", "talão fundo",
                "pneu aquecido desmontagem", "quebra montagem talão fragilizado"],
        "neg": ["rachadura", "trinca", "pé de galinha", "flanco", "circunferencial"],
    },
    # 75A — contato prolongado com óleo/derivado de petróleo.
    # Flanco ESTUFADO para fora (visível de cima). Manchas de óleo na lateral.
    "75A": {
        "pos": ["flanco estufado", "estufamento lateral", "óleo flanco", "manchado óleo",
                "absorção óleo", "derivado petróleo", "contato óleo", "lateral estufada",
                "flanco inchado", "mancha derivado", "óleo na lateral", "borracha estufada"],
        "neg": ["corte", "rachadura", "desgaste", "talão", "banda"],
    },
}

def encontrar_fvu_por_descricao(descricao_ia, fvu_data):
    if not descricao_ia or not fvu_data:
        return fvu_data[0] if fvu_data else None

    desc_lower = descricao_ia.lower()
    melhor_match = None
    max_score = -999

    for item in fvu_data:
        codigo = item["codigo"].strip().upper()
        kw = FVU_KEYWORDS.get(codigo, {})
        score = 0
        for termo in kw.get("pos", []):
            if termo in desc_lower:
                score += 3
        for termo in kw.get("neg", []):
            if termo in desc_lower:
                score -= 4
        texto_fvu = (item["descricao"] + " " + item["categoria"]).lower()
        for palavra in [p for p in texto_fvu.split() if len(p) > 3]:
            if palavra in desc_lower:
                score += 1
        if score > max_score:
            max_score = score
            melhor_match = item

    return melhor_match if melhor_match and max_score > 0 else fvu_data[0]
