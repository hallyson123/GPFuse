def criar_nodo(tx, rotulos, propriedade_unica, propriedades_completas):
    # Junta as labels para a query, ex: :Person:Director
    labels_cypher = ":".join(rotulos)

    query = (
        f"MERGE (n:{labels_cypher} {{ {propriedade_unica}: ${propriedade_unica} }}) "
        "ON CREATE SET n = $props"
    )
    
    tx.run(query, **{propriedade_unica: propriedades_completas[propriedade_unica], 'props': propriedades_completas})