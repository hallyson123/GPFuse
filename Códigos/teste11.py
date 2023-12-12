from neo4j import GraphDatabase

uri = "bolt://3.82.107.186:7687"  # Substitua pelo seu URI
username = "neo4j"
password = "clubs-smokes-workmen"

class No:
    def __init__(self, rotulo):
        self.rotulo = rotulo
        self.quantidade = 0
        self.propriedades = {}

    def adicionar_propriedade(self, nome, tipo):
        if nome not in self.propriedades:
            self.propriedades[nome] = {"tipos": {}, "total": 0}
        if tipo in self.propriedades[nome]["tipos"]:
            self.propriedades[nome]["tipos"][tipo] += 1
        else:
            self.propriedades[nome]["tipos"][tipo] = 1
        # self.propriedades[nome]["total"] += 1

def percorrer_nos_e_armazenar_info(tx, nos):
    result = tx.run(
        "MATCH (p)"
        "RETURN DISTINCT labels(p) AS nodeType, properties(p) AS props, count(p) AS count"
    )

    for record in result:
        rotulos = tuple(record["nodeType"])
        quantidade = record["count"]
        if rotulos not in nos:
            nos[rotulos] = No(rotulos)
        nos[rotulos].quantidade += quantidade  # Corrigindo para somar a quantidade em vez de substituir

        # Adicionando propriedades ao nó
        propriedades = record["props"]
        for nome, valor in propriedades.items():
            tipo = "UNKNOWN"
            if valor is not None:
                tipo = type(valor).__name__
            nos[rotulos].adicionar_propriedade(nome, tipo)

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    nos = {}  # Dicionário para armazenar instâncias da classe No
    with driver.session() as session:
        session.read_transaction(percorrer_nos_e_armazenar_info, nos)

# Exibindo os resultados
print("-----------------------")
for rotulos, no in nos.items():
    rotulos_str = ', '.join(rotulos)
    print(f"Rótulo: {rotulos_str}")
    print(f"Quantidade: {no.quantidade}")
    for propriedade, info_propriedade in no.propriedades.items():
        print(f"    {propriedade}:")
        for tipo, quantidade in info_propriedade["tipos"].items():
            print(f"        Tipo: {tipo}, Quantidade: {quantidade}")
        #print(f"        Total: {info_propriedade['total']}")
    print("-----------------------")
