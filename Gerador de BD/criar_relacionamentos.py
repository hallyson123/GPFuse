def relacionar_pessoa_filme(tx, pessoa_id, filme_titulo):
    query = """
    MATCH (p:Person {id: $pessoa_id})
    MATCH (f:Film {title: $filme_titulo})
    MERGE (p)-[:RELATED_TO]->(f)
    """
    tx.run(query, pessoa_id=pessoa_id, filme_titulo=filme_titulo)

def relacionar_sponsor_filme(tx, sponsor_nome, filme_titulo, propriedades_rel):
    query = """
    MATCH (s:Sponsor {name: $sponsor_nome})
    MATCH (f:Film {title: $filme_titulo})
    MERGE (s)-[r:SPONSORED_BY]->(f)
    SET r = $props
    """
    tx.run(query, sponsor_nome=sponsor_nome, filme_titulo=filme_titulo, props=propriedades_rel)

def relacionar_streaming_filme(tx, streaming_nome, filme_titulo, propriedades_rel):
    query = """
    MATCH (st:Streaming {name: $streaming_nome})
    MATCH (f:Film {title: $filme_titulo})
    MERGE (st)-[r:CONTAINS]->(f)
    SET r = $props
    """
    tx.run(query, streaming_nome=streaming_nome, filme_titulo=filme_titulo, props=propriedades_rel)