from ClassNo import No

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
        nos[rotulos].quantidade += quantidade #psomar a quantidade

        # Adicionando propriedades ao nó
        propriedades = record["props"]
        for nome, valor in propriedades.items():
            tipo = "UNKNOWN"
            if valor is not None:
                tipo = type(valor).__name__
            nos[rotulos].adicionar_propriedade(nome, tipo, valor)

def percorrer_relacionamentos(tx, nos):
    result = tx.run(
        "MATCH (p)-[r]->(q)"
        "RETURN DISTINCT labels(p) AS nodeType, type(r) AS relType, labels(q) AS destLabel, count(r) AS count"
    )

    for record in result:
        rotulos_origem = tuple(record["nodeType"])
        tipo_relacionamento = record["relType"]
        rotulo_destino = tuple(record["destLabel"])
        quantidade_rel = record["count"]
        
        if rotulos_origem not in nos:
            nos[rotulos_origem] = No(rotulos_origem)
        
        # Adicionando relacionamentos
        nos[rotulos_origem].adicionar_relacionamento(tipo_relacionamento, rotulo_destino, quantidade_rel)
