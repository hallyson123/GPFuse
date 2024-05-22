MAX_ENUMERATE = 10

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

    def adicionar_propriedade(self, nome, tipo, valor):
        if nome not in self.propriedades:
            self.propriedades[nome] = {"tipos": {}, "values": set(),"constraint": False, "constraintList": [], "listProp": [], "listConstProp": False, "is_enum": True, "total": 0, "is_list": False, "tamQuantLista": {}, "ModaList": [], "tipos_listas": {}, "is_shared": False}

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
    
    def adicionar_relacionamento(self, tipo_relacionamento, nodo_destino, quantidade_rel):
        if tipo_relacionamento not in self.relacionamentos:
            self.relacionamentos[tipo_relacionamento] = []
        self.relacionamentos[tipo_relacionamento].append((nodo_destino, quantidade_rel))

    def atualizar_cardinalidade(self, tipo_relacionamento, cardinalidade):
        self.cardinalidades[tipo_relacionamento] = cardinalidade