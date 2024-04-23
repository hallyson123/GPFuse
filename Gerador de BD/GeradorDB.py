from neo4j import GraphDatabase
import random

uri = "bolt://localhost:7687"  # Substitua pelo seu URI
user = "neo4j"
password = "1F16EBD3"

driver = GraphDatabase.driver(uri, auth=(user, password))

def criar_nodos(tx, rotulo, propriedade, atributo, quantidade, subtipo=None, enumerate_valor_max=None):
    for _ in range(quantidade):
        valor = f"{atributo}_{random.randint(1, 10000)}"  # Adiciona um valor aleatório para evitar duplicatas
        lista_valores = [random.randint(1, 10000) for _ in range(random.randint(1, 10))]  # Lista de valores aleatórios
        # Verificar se o nó já existe
        result = tx.run(f"MATCH (n:{rotulo}) WHERE n.{propriedade} = $atributo RETURN n", atributo=valor)
        if result.peek() is None:
            # Se o nó não existir
            if subtipo:
                tx.run(f"CREATE (:{rotulo}:{subtipo} {{{propriedade}: $atributo, lista_propriedade: $lista}})", atributo=valor, lista=lista_valores)
            else:
                # Verificar se a propriedade deve ser enumerada
                if enumerate_valor_max is not None:
                    enumerate_propriedade = random.randint(1, enumerate_valor_max)
                    tx.run(f"CREATE (:{rotulo} {{enumerate_propriedade: $enumerate_propriedade}})",
                           enumerate_propriedade=enumerate_propriedade)
                else:
                    tx.run(f"CREATE (:{rotulo} {{{propriedade}: $atributo, lista_propriedade: $lista}})",
                           atributo=valor, lista=lista_valores)
        else:
            print(f"Nodo com [{propriedade}: '{valor}]' já existe.")

def criar_nodos_e_relacionamentos(tx, tipo_origem, propriedade_origem, tipo_relacionamento, quantidade):
    # Para cada nó de origem, criar um relacionamento com um nó de destino (Filme)
    for _ in range(quantidade):
        valor_origem = f"{propriedade_origem}_{random.randint(1, 10000)}"  # Gerar um valor aleatório para a propriedade do nó de origem
        valor_destino = f"filme_{random.randint(1, 10000)}"  # Gerar um valor aleatório para o título do nó de destino (Filme)
        
        # Cria o relacionamento entre o nó de origem e o nó de destino (Filme)
        tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }}), (destino:Filme {{ titulo: $propriedade_destino }}) "
               f"MERGE (origem)-[:{tipo_relacionamento}]->(destino)", propriedade_origem=valor_origem, propriedade_destino=valor_destino)

def criar_restricao(tx, rotulo, propriedade):
    result = tx.run("SHOW CONSTRAINT")
    for record in result:
        nodo_rotulo = record["labelsOrTypes"]
        pripriedade_rotulo = record["properties"]

        if rotulo in nodo_rotulo and propriedade in pripriedade_rotulo:
            print(f"Restrição com o nodo [{rotulo}] e propriedade [{propriedade}] já existe.")
            return
        else:
            tx.run(f"CREATE CONSTRAINT Unique{rotulo} FOR (n:{rotulo}) REQUIRE n.{propriedade} IS UNIQUE")

def close_driver():
    driver.close()

#Tipos de nós e seus possíveis subtipos
tipos_nodos = {
    "Pessoa": ["Diretor", "Produtor", "Avaliador"]
}

rotulos_nodos = ["Pessoa", "Diretor", "Produtor", "Avaliador", "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"]

# Exemplo de uso
quantidade_nodos = 1000
quantidade_relacionamentos = 50
max_enumerate = 10

with driver.session() as session:
    #Criar restriçao
    session.write_transaction(criar_restricao, "Filme", "titulo")

    # Criar nodos Filme
    session.write_transaction(criar_nodos, "Filme", "titulo", "filme", quantidade_nodos, subtipo= None, enumerate_valor_max=max_enumerate) #criar nodos Filme
    
    #Criar nodos Pessoa e seus subtipos
    for tipo_origem, subtipos in tipos_nodos.items():
        session.write_transaction(criar_nodos, tipo_origem, "nome", tipo_origem.lower(), quantidade_nodos) #criar nodos "Pessoa"
        for subtipo in subtipos:
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos, tipo_origem) # cria nodos "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos) #cria nodos "Diretor", "Produtor", "Avaliador"
            
    #criar relacionamentos
    for _ in range(quantidade_relacionamentos):
        valorRotulo = random.randint(0, 6)
        rotulo_origem = rotulos_nodos[valorRotulo]
        print(rotulos_nodos[valorRotulo])
        session.write_transaction(criar_nodos_e_relacionamentos, rotulo_origem, rotulo_origem.lower(), "RELACIONADO_COM", quantidade_relacionamentos)
