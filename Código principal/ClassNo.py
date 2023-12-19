MAX_ENUMERATE = 2

class No:
    def __init__(self, rotulo):
        self.rotulo = rotulo
        self.quantidade = 0
        self.propriedades = {}
        self.relacionamentos = {}

    def adicionar_propriedade(self, nome, tipo, valor):
        if nome not in self.propriedades:
            self.propriedades[nome] = {"tipos": {}, "values": set(), "is_enum": True, "total": 1}
        else:
            self.propriedades[nome]["tipos"][tipo] = self.propriedades[nome]["tipos"].get(tipo, 0) + 1
            self.propriedades[nome]["total"] += 1
            
            # Verifica se é enumerate
            if self.propriedades[nome]["is_enum"]:
                if len(self.propriedades[nome]["values"]) < MAX_ENUMERATE:
                    self.propriedades[nome]["values"].add(valor)
                    if len(self.propriedades[nome]["values"]) > MAX_ENUMERATE:
                        self.propriedades[nome]["is_enum"] = False
        
    def adicionar_relacionamento(self, tipo_relacionamento, rotulo_destino, quantidade_rel):
        if tipo_relacionamento not in self.relacionamentos:
            self.relacionamentos[tipo_relacionamento] = {"rotulos_destino": set(), "quantidade": 0}
        self.relacionamentos[tipo_relacionamento]["rotulos_destino"].add(rotulo_destino)
        self.relacionamentos[tipo_relacionamento]["quantidade"] = quantidade_rel

