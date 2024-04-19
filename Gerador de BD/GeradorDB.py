from neo4j import GraphDatabase
import random

uri = "bolt://localhost:7687"  # Substitua pelo seu URI
user = "neo4j"
password = "1F16EBD3"

driver = GraphDatabase.driver(uri, auth=(user, password))

def criar_nodos(tx, label, key, value, quantidade):
    for _ in range(quantidade):
        valor = f"{value}_{random.randint(1, 100000)}"  #Adiciona um valor aleatório para evitar duplicatas
        lista_valores = [random.randint(1, 100) for _ in range(random.randint(1, 10))]  #Lista de valores aleatórios
        # Verificar se o nó já existe
        result = tx.run(f"MATCH (n:{label}) WHERE n.{key} = $value RETURN n", value=valor)
        if result.peek() is None:
            # Se o nó não existir
            tx.run(f"CREATE (:{label} {{{key}: $value, lista_propriedade: $lista}})", value=valor, lista=lista_valores)
        else:
            print(f"Node with [{key}: '{valor}]' already exists.")

def criar_nodos_e_relacionamentos(tx, tipo_origem, chave_origem, valor_origem, tipo_destino, chave_destino, valor_destino, tipo_relacionamento, quantidade):
    for _ in range(quantidade):
        valor_origem = f"{valor_origem}_{random.randint(1, 100000)}"
        valor_destino = f"{valor_destino}_{random.randint(1, 100000)}"
        lista_valores_origem = [random.randint(1, 100) for _ in range(random.randint(1, 10))]  # Lista de valores aleatórios
        lista_valores_destino = [random.randint(1, 100) for _ in range(random.randint(1, 10))]  # Lista de valores aleatórios
        #Verificar se o nó de origem já existe
        result_origem = tx.run(f"MATCH (n:{tipo_origem}) WHERE n.{chave_origem} = $value RETURN n", value=valor_origem)
        if result_origem.peek() is None:
            #Se o nó de origem não existir, criar
            tx.run(f"CREATE (:{tipo_origem} {{{chave_origem}: $value, lista_propriedade: $lista}})", value=valor_origem, lista=lista_valores_origem)

        #Verificar se o nó de destino já existe
        result_destino = tx.run(f"MATCH (n:{tipo_destino}) WHERE n.{chave_destino} = $value RETURN n", value=valor_destino)
        if result_destino.peek() is None:
            #Se o nó de destino não existir, criar
            tx.run(f"CREATE (:{tipo_destino} {{{chave_destino}: $value, lista_propriedade: $lista}})", value=valor_destino, lista=lista_valores_destino)

        #Criar o relacionamento entre os nós
        tx.run(f"MATCH (origem:{tipo_origem} {{ {chave_origem}: $valor_origem }}), (destino:{tipo_destino} {{ {chave_destino}: $valor_destino }}) "
               f"MERGE (origem)-[:{tipo_relacionamento}]->(destino)", valor_origem=valor_origem, valor_destino=valor_destino)

def close_driver():
    driver.close()

# Exemplo de uso
quantidade_nodos = 25
quantidade_relacionamentos = 2
with driver.session() as session:
    for _ in range(quantidade_nodos):
        session.write_transaction(criar_nodos, "User", "email", "user@example.com", quantidade_relacionamentos)
        session.write_transaction(criar_nodos_e_relacionamentos, "User", "email", "user@example.com", "Product", "id", "123", "PURCHASED", quantidade_relacionamentos)
