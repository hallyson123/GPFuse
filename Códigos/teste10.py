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

        #armazenar tipos de propriedades por rótulo
        tipos_propriedades_por_rotulo = {}

        # Exibindo os resultados
        # print("-----------------------")

        for labels, propriedades in dados_nodos:
            # Convertendo a tupla de rótulos de volta para uma lista
            labels = list(labels)

            if tuple(labels) not in tipos_propriedades_por_rotulo:
                tipos_propriedades_por_rotulo[tuple(labels)] = {}

            #if not propriedades:
                #print(f"Rotulo: {labels}")
                #print("    Não existe propriedades")
            #else:
                for propriedade, valor in propriedades.items():
                    tipo = "UNKNOWN"
                    if valor is not None:
                        tipo = type(valor).__name__

                    # Adicionando o tipo da propriedade à lista correspondente
                    if propriedade in tipos_propriedades_por_rotulo[tuple(labels)]:
                        tipos_propriedades_por_rotulo[tuple(labels)][propriedade].add(tipo)
                    else:
                        tipos_propriedades_por_rotulo[tuple(labels)][propriedade] = {tipo}

                    # Exibindo o tipo da propriedade
                    #print(f"Rotulo: {labels}")
                    #print(f"    {propriedade}: [{tipo}]")
      
        print("-----------------------")

        # Exibindo os tipos das propriedades por rótulo
        for labels, tipos_propriedades in tipos_propriedades_por_rotulo.items():
            labels_str = ', '.join(labels)
            print(f"Rotulo: {labels_str}")
            
            for propriedade, tipos in tipos_propriedades.items():
                print(f"    {propriedade}: {list(tipos)}")
            print("-----------------------")