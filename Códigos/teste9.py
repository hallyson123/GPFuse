from neo4j import GraphDatabase

uri = "bolt://3.82.107.186:7687"  # Substitua pelo seu URI
username = "neo4j"
password = "clubs-smokes-workmen"

# Função para percorrer os nós e coletar as propriedades de cada nó
def percorrer_nos_e_armazenar_propriedades(tx):
    result = tx.run(
        "MATCH (p)"
        "RETURN DISTINCT labels(p) AS nodeType, properties(p) AS propriedades"
    )
    return [(tuple(record["nodeType"]), record["propriedades"]) for record in result]

# Conectando ao banco de dados Neo4j
with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    with driver.session() as session:
        # Executando a função para percorrer os nós e coletar as propriedades
        dados_nodos = session.read_transaction(percorrer_nos_e_armazenar_propriedades)

        # Armazenar rótulos únicos
        rótulos_únicos = set()

        # Exibindo os resultados

        print("-----------------------")

        for labels, propriedades in dados_nodos:
            # Convertendo a tupla de rótulos de volta para uma lista
            labels = list(labels)

            if tuple(labels) not in rótulos_únicos:
                rótulos_únicos.add(tuple(labels))
                print(f"Rotulo: {labels}")

                if not propriedades:
                    print("    Não existe propriedades")

                else:
                    for propriedade, valor in propriedades.items():
                        tipo = "UNKNOWN"
                        if valor is not None:
                            tipo = type(valor).__name__

                        print(f"    {propriedade}: [{tipo}]")
      
                print("-----------------------")
driver.close()

# d={}
# d['X']={at:}
# for r in Rotulos:
#     try:
#         d[r].count+=1
#     except:
#         d[r]={count: 1}
#     if d[r] is None:


# if r in d.keys()

