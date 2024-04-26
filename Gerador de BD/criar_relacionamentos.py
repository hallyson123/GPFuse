import random

def criar_relacionamentos(tx, tipo_origem, propriedade_origem, quantidade):
    # Para cada nó de origem, criar um relacionamento com um nó de destino (Filme)
    result = tx.run(f"MATCH(origem:{tipo_origem}) RETURN count(origem) AS quantidade_rotulos")
    limite = result.single()["quantidade_rotulos"]
    quantidade_relacionamentos = random.randint(1, limite) 
    for _ in range(quantidade_relacionamentos):
        valor_origem = f"{propriedade_origem}_{random.randint(1, 100)}"  # Gerar um valor aleatório para a propriedade do nó de origem
        valor_destino = f"filme_{random.randint(1, 100)}"  # Gerar um valor aleatório para o título do nó de destino (Filme)
        
        # Determinar o tipo de relacionamento com base no tipo de nó de origem
        tipo_relacionamento = tipo_origem.upper()[:6]

        # Criar o relacionamento entre o nó de origem e o nó de destino (Filme)
        tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }}), (destino:Filme {{ titulo: $propriedade_destino }}) "
            f"MERGE (origem)-[:{tipo_relacionamento}]->(destino)", propriedade_origem=valor_origem, propriedade_destino=valor_destino)
        
        # Verificar se o relacionamento foi criado com sucesso
        result = tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }})-[:{tipo_relacionamento}]->(destino:Filme {{ titulo: $propriedade_destino }}) "
                        "RETURN COUNT(*) AS count", propriedade_origem=valor_origem, propriedade_destino=valor_destino)
        count = result.single()["count"]
        if count > 0:
            print(f"Relacionamento criado entre [{tipo_origem}] e [Filme] ({valor_origem})")
        # else:
        #     print(f"Não foi possível criar relacionamento entre [{tipo_origem}] e [Filme] ({valor_origem})")