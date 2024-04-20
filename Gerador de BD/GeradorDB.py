from neo4j import GraphDatabase
import random

uri = "bolt://localhost:7687"
user = "neo4j"
password = "1F16EBD3"

driver = GraphDatabase.driver(uri, auth=(user, password))

def criar_nodos(tx, label, key, value, quantidade, subtipo=None):
    for _ in range(quantidade):
        valor = f"{value}_{random.randint(1, 100000)}"  # Adiciona um valor aleatório para evitar duplicatas
        lista_valores = [random.randint(1, 100) for _ in range(random.randint(1, 10))]  # Lista de valores aleatórios
        # Verificar se o nó já existe
        result = tx.run(f"MATCH (n:{label}) WHERE n.{key} = $value RETURN n", value=valor)
        if result.peek() is None:
            # Se o nó não existir
            if subtipo:
                tx.run(f"CREATE (:{label}:{subtipo} {{{key}: $value, lista_propriedade: $lista}})", value=valor, lista=lista_valores)
            else:
                tx.run(f"CREATE (:{label} {{{key}: $value, lista_propriedade: $lista}})", value=valor, lista=lista_valores)
        else:
            print(f"Node with [{key}: '{valor}]' already exists.")

def criar_relacionamentos(tx, tipo_origem, tipo_relacionamento, quantidade):
    # Recuperar uma lista de todos os nós
    result = tx.run(f"MATCH (n:{tipo_origem}) WHERE NOT n:Filme RETURN n")
    nodos_origem = [record["n"] for record in result]

    # Para cada nó de origem, criar um relacionamento com um nó de destino (Filme)
    for nodo_origem in nodos_origem:
        valor_destino = f"filme_{random.randint(1, 100000)}"  # Gerar um valor aleatório para o filme
        
        # Cria o relacionamento entre o nó de origem e o nó de destino (Filme)
        tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $nome_origem }}), (destino:Filme {{ titulo: $titulo_destino }}) "
               f"MERGE (origem)-[:{tipo_relacionamento}]->(destino)", nome_origem=nodo_origem["nome"], titulo_destino=valor_destino)
        print(tipo_origem, tipo_relacionamento, "Filme")

def close_driver():
    driver.close()

#Tipos de nós e seus possíveis subtipos
tipos_nodos = {
    "Pessoa": ["Diretor", "Produtor", "Avaliador"]
}

rotulos_nodos = ["Pessoa", "Diretor", "Produtor", "Avaliador", "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"]

# Exemplo de uso
quantidade_nodos = 200
quantidade_relacionamentos = 50
with driver.session() as session:
    session.write_transaction(criar_nodos, "Filme", "titulo", "filme", quantidade_nodos) #criar nodos Filme
    for tipo_origem, subtipos in tipos_nodos.items():
        session.write_transaction(criar_nodos, tipo_origem, "nome", tipo_origem.lower(), quantidade_nodos) #criar nodos "Pessoa", "Diretor", "Produtor", "Avaliador"
        for subtipo in subtipos:
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos, tipo_origem)

            #criar relacionamentos
            valorRotulo = random.randint(0, 6)
            session.write_transaction(criar_relacionamentos, rotulos_nodos[valorRotulo], "RELACIONADO_COM", quantidade_relacionamentos)
