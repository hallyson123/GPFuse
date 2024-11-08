MAX_ENUMERATE = 20
THRESHOLD = 0.9
THRESHOLD_OCCURRENCE = 0.7

class No:
    def __init__(self, rotulo):
        self.rotulo = rotulo
        self.quantidade = 0
        self.total_propriedades = 0
        self.propriedades = {}
        self.relacionamentos = {}
        self.tamanhos_listas = {}
        self.cardinalidades = {}
        self.supertipos = []
        self.subtipos = []
        self.listaChaveUnica = []

    def adicionar_propriedade(self, nome, tipo, valor):
        if nome not in self.propriedades:
            self.propriedades[nome] = {"tipos": {}, "PropValues": set(), "values": set(), "constraint": False, 'unicidadeNeo4j': False, "constraintUniquess": False, "constraintList": [], "listProp": [], "listConstProp": False, "is_enum": True, "total": 0, "is_list": False, "tamQuantLista": {}, "ModaList": [], "tipos_listas": {}, "is_shared": False}

        if isinstance(valor, list):
            self.propriedades[nome]["is_list"] = True
        else:
            self._adicionar_tipo_propriedade(nome, valor)

    def _adicionar_tipo_propriedade(self, nome, valor):
        self.propriedades[nome]["total"] += 1

        tipo = type(valor).__name__
        if tipo in self.propriedades[nome]["tipos"]:
            self.propriedades[nome]["tipos"][tipo] += 1
        else:
            self.propriedades[nome]["tipos"][tipo] = 1

        # Verifica se é enumerate
        if self.propriedades[nome]["is_enum"]:
            if len(self.propriedades[nome]["values"]) < MAX_ENUMERATE:
                if isinstance(valor, str):
                    valor = valor[:20]  # Limita a string a 20 caracteres
                # Verifica se "values" é uma lista
                if isinstance(self.propriedades[nome]["values"], list):
                    self.propriedades[nome]["values"].append(valor)
                else:
                    # Se não for uma lista, deve ser um conjunto, então adicionamos o valor usando "add()"
                    self.propriedades[nome]["values"].add(valor)
                if len(self.propriedades[nome]["values"]) >= MAX_ENUMERATE:
                    self.propriedades[nome]["is_enum"] = False
                    self.propriedades[nome]["values"].clear()

        # cria lista de valores não repetidos para auxiliar a criação de constraints únicas
        if isinstance(valor, int) or isinstance(valor, str): #floats são descartados
            if isinstance(valor, str):
                valor = valor[:20]  # Limita a string a 20 caracteres
            self.propriedades[nome]["PropValues"].add(valor)

    def adicionar_subtipo(self, subtipo):
        self.subtipos.append(subtipo)

    def adicionar_supertipo(self, supertipo):
        self.supertipos.append(supertipo)

    def moda_tamanho_listas(self):
        if not self.propriedades:
            return None

        modas = {}
        for propriedade, info_propriedade in self.propriedades.items():
            if info_propriedade["is_list"]:
                tamQuantLista = info_propriedade.get("tamQuantLista", {})
                max_quantidade = max(tamQuantLista.values(), default=0)
                modas[propriedade] = [tamanho for tamanho, quantidade in tamQuantLista.items() if quantidade == max_quantidade]

        return modas if modas else None

    def adicionar_relacionamento(self, tipo_relacionamento, nodo_destino, quantidade_rel, propriedades):
        # Verifica se o tipo de relacionamento não existe e inicializa
        if tipo_relacionamento not in self.relacionamentos:
            self.relacionamentos[tipo_relacionamento] = []

        # Contabiliza as propriedades do relacionamento e adiciona lista de valores únicos
        contador_propriedades = {}
        for nome_propriedade, valor in propriedades.items():
            tipo = type(valor).__name__

            # Inicializa a contagem se necessário
            if nome_propriedade not in contador_propriedades:
                contador_propriedades[nome_propriedade] = {
                    "total": 0,
                    "tipos": {},
                    "valores_unicos": set(),  # Conjunto para valores únicos
                    "valores_enum": set(),
                    "is_enum": True,
                    "is_list": False,
                    "list_info": {"tipo_item": None, "tamanho_min": None, "tamanho_max": None}
                }
            
            # Incrementa o total de ocorrências
            contador_propriedades[nome_propriedade]["total"] += 1

            # Conta tipos de dados
            if tipo in contador_propriedades[nome_propriedade]["tipos"]:
                contador_propriedades[nome_propriedade]["tipos"][tipo] += 1
            else:
                contador_propriedades[nome_propriedade]["tipos"][tipo] = 1

            # Tratamento específico para listas
            if isinstance(valor, list):
                contador_propriedades[nome_propriedade]["tipos"]["list"] = contador_propriedades[nome_propriedade]["tipos"].get("list", 0) + 1
                contador_propriedades[nome_propriedade]["is_enum"] = False
                contador_propriedades[nome_propriedade]["valores_enum"].clear()

                contador_propriedades[nome_propriedade]["is_list"] = True

                # Identificar tipo dos elementos da lista e atualizar informações de tamanho mínimo e máximo
                if valor:  # Somente processa se a lista não estiver vazia
                    tipo_item = type(valor[0]).__name__
                    contador_propriedades[nome_propriedade]["list_info"]["tipo_item"] = tipo_item
                    tamanho_lista = len(valor)

                    # Atualiza tamanho mínimo e máximo
                    if contador_propriedades[nome_propriedade]["list_info"]["tamanho_min"] is None or tamanho_lista < contador_propriedades[nome_propriedade]["list_info"]["tamanho_min"]:
                        contador_propriedades[nome_propriedade]["list_info"]["tamanho_min"] = tamanho_lista
                    if contador_propriedades[nome_propriedade]["list_info"]["tamanho_max"] is None or tamanho_lista > contador_propriedades[nome_propriedade]["list_info"]["tamanho_max"]:
                        contador_propriedades[nome_propriedade]["list_info"]["tamanho_max"] = tamanho_lista
                    
                # print(contador_propriedades[nome_propriedade])
                continue  # Ignora o restante do loop, pois já tratamos como lista

            # Adiciona o valor à lista de valores únicos (limita string para 20 caracteres se for do tipo str)
            if isinstance(valor, int) or isinstance(valor, str): #floats são descartados
                if isinstance(valor, (int, str)):
                    valor = valor[:20] if isinstance(valor, str) else valor
                    contador_propriedades[nome_propriedade]["valores_unicos"].add(valor)

            # Verifica enum
            if isinstance(valor, list) == False:
                valor = valor[:20] if isinstance(valor, str) else valor
                if contador_propriedades[nome_propriedade]["is_enum"]:
                    contador_propriedades[nome_propriedade]["valores_enum"].add(valor)

                    if len(contador_propriedades[nome_propriedade]["valores_enum"]) > MAX_ENUMERATE:
                        contador_propriedades[nome_propriedade]["is_enum"] = False
                        contador_propriedades[nome_propriedade]["valores_enum"].clear()

        # Verifica se o relacionamento com destino e quantidade especificada já existe
        for rel in self.relacionamentos[tipo_relacionamento]:
            if rel[0] == nodo_destino and rel[1] == quantidade_rel:
                # Atualiza contador de propriedades em caso de relacionamento existente
                for nome_propriedade, dados_propriedade in contador_propriedades.items():
                    if nome_propriedade in rel[2]:
                        rel[2][nome_propriedade]["total"] += dados_propriedade["total"]
                        for tipo, quantidade in dados_propriedade["tipos"].items():
                            if tipo in rel[2][nome_propriedade]["tipos"]:
                                rel[2][nome_propriedade]["tipos"][tipo] += quantidade
                            else:
                                rel[2][nome_propriedade]["tipos"][tipo] = quantidade
                        # Atualiza valores únicos no relacionamento existente
                        rel[2][nome_propriedade]["valores_unicos"].update(dados_propriedade["valores_unicos"])

                        # Verifica novamente se a propriedade ainda pode ser enum após a atualização
                        if rel[2][nome_propriedade]["is_enum"]:
                            rel[2][nome_propriedade]["valores_enum"].update(dados_propriedade["valores_enum"])
                            if len(rel[2][nome_propriedade]["valores_enum"]) > MAX_ENUMERATE:
                                rel[2][nome_propriedade]["is_enum"] = False
                                rel[2][nome_propriedade]["valores_enum"].clear()
                    else:
                        rel[2][nome_propriedade] = dados_propriedade
                return

        # Caso contrário, adiciona um novo relacionamento
        self.relacionamentos[tipo_relacionamento].append((nodo_destino, quantidade_rel, contador_propriedades))

    def atualizar_cardinalidade(self, tipo_relacionamento, cardinalidade):
        self.cardinalidades[tipo_relacionamento] = cardinalidade