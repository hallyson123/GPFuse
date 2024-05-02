import random

def rel_pessoas_filmes(tx, tipo_origem, propriedade_origem, quantidade):
    # Para cada nó de origem, criar um relacionamento com um nó de destino (Filme)
    result = tx.run(f"MATCH(origem:{tipo_origem}) RETURN count(origem) AS quantidade_rotulos")
    limite = result.single()["quantidade_rotulos"]
    quantidade_relacionamentos = random.randint(1, limite) 

    # Gerar uma lista de títulos de filmes únicos
    titulos_filmes = [f"filme_{i}" for i in range(1, 500)]
    
    # Criar todos os nós Filme
    for titulo_filme in titulos_filmes:
        tx.run("MERGE (:Filme {titulo: $titulo})", titulo=titulo_filme)

    # Recarregar a lista de títulos de filmes com novos valores
    titulos_filmes = [f"filme_{i}" for i in range(1, 500)]

    for _ in range(quantidade_relacionamentos):
        if not titulos_filmes:
            break
            
        valor_origem = f"{propriedade_origem}_{random.randint(1, 100)}"  # Gerar um valor aleatório para a propriedade do nó de origem
            
        # Selecionar aleatoriamente um título de filme da lista
        valor_destino = random.choice(titulos_filmes)
        titulos_filmes.remove(valor_destino)  # Remover o título selecionado da lista para garantir que seja único
            
        # Determinar o tipo de relacionamento com base no tipo de nó de origem
        tipo_relacionamento = tipo_origem.upper()[:6]

        # Criar o relacionamento entre o nó de origem e o nó de destino (Filme) (1,N):(0,N)
        tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }}), (filme:Filme{{titulo: $propriedade_destino}}) "
            f"MERGE (origem)-[:{tipo_relacionamento}]->(filme)", propriedade_origem=valor_origem, propriedade_destino=valor_destino)

def rel_financiadores_filmes(tx, quantidade):
    # Criar relacionamentos Financiadores para Filmes (0,1):(1,1)
    propriedade_financiador = [f"financiador_{i}" for i in range(1, 11)]  # Lista de financiadores possíveis

    filmes = [f"filme_{i}" for i in range(1, 501)]  # Lista de todos os filmes possíveis

    for _ in range(quantidade):
        # Selecionar aleatoriamente um financiador
        financiador = propriedade_financiador.pop(0)

        # Selecionar aleatoriamente um filme da lista
        valor_destino = random.choice(filmes)
        
        # Remover o filme selecionado da lista de filmes para garantir que cada filme seja financiado apenas uma vez
        filmes.remove(valor_destino)

        # Verificar se já existe um relacionamento para esse financiador
        result = tx.run("MATCH (origem:Financiador {nome: $propriedade_origem})-[:PATROCINA]->(destino:Filme) "
               "RETURN count(destino)", propriedade_origem=financiador)
        count = result.single()[0]

        if count > 0:
            print("Relacionamento já existe")
        else:
            # Criar o relacionamento de financiamento entre o financiador e o filme
            tx.run("MATCH (origem:Financiador {nome: $propriedade_origem}), (destino:Filme {titulo: $propriedade_destino}) "
                "MERGE (origem)-[:PATROCINA]->(destino)", propriedade_origem=financiador, propriedade_destino=valor_destino)
            
def rel_streaming_filme(tx, propriedade_origem, quantidade):
    propriedade_streaming = propriedade_origem  # Streaming

    #criar rel Streaming -[CONTEM]-> Filme ((0:N);(0:N))
    for _ in range(quantidade):
        propriedade_filme = f"filme_{random.randint(1, 501)}" #Filme aleatorio
        tx.run("MATCH (origem:Streaming{nome: $propriedade_origem}), (destino:Filme {titulo: $propriedade_destino}) "
            "MERGE (origem)-[:CONTEM]->(destino)", propriedade_origem=propriedade_streaming, propriedade_destino=propriedade_filme)
