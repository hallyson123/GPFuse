def criar_restricao_se_nao_existe(tx, rotulo, propriedade):
    # Dá um nome único à restrição
    nome_restricao = f"constraint_{rotulo}_{propriedade}"
    
    # 1. Verifica se a restrição com este nome já existe
    query_check = "SHOW CONSTRAINTS WHERE name = $nome_restricao"
    result = tx.run(query_check, nome_restricao=nome_restricao)
    
    # Se a consulta não retornar nada, a restrição não existe
    if result.peek() is None:
        # 2. Cria a restrição
        query_create = (
            f"CREATE CONSTRAINT {nome_restricao} "
            f"FOR (n:{rotulo}) REQUIRE n.{propriedade} IS UNIQUE"
        )
        tx.run(query_create)
        print(f"SUCESSO: Restrição '{nome_restricao}' criada para [{rotulo}.{propriedade}].")
    else:
        # A restrição já existe, então não faz nada
        print(f"INFO: Restrição '{nome_restricao}' para [{rotulo}.{propriedade}] já existe.")