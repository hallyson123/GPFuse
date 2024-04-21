from neo4j import GraphDatabase
import random

uri = "bolt://localhost:****"
user = "neo4j"
password = "****"

driver = GraphDatabase.driver(uri, auth=(user, password))

def criar_nodos(tx, rotulo, propriedade, atributo, quantidade, subtipo=None):
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
                tx.run(f"CREATE (:{rotulo} {{{propriedade}: $atributo, lista_propriedade: $lista}})", atributo=valor, lista=lista_valores)
        else:
            print(f"Node with [{propriedade}: '{valor}]' already exists.")

def criar_relacionamentos(tx, tipo_origem, propriedade_origem, tipo_relacionamento, quantidade):
    # Para cada nó de origem, criar um relacionamento com um nó de destino (Filme)
    for _ in range(quantidade):
        valor_origem = f"{propriedade_origem}_{random.randint(1, 10000)}"  # Gerar um valor aleatório para a propriedade do nó de origem
        valor_destino = f"filme_{random.randint(1, 10000)}"  # Gerar um valor aleatório para o título do nó de destino (Filme)
        
        # Cria o relacionamento entre o nó de origem e o nó de destino (Filme)
        tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }}), (destino:Filme {{ titulo: $propriedade_destino }}) "
               f"MERGE (origem)-[:{tipo_relacionamento}]->(destino)", propriedade_origem=valor_origem, propriedade_destino=valor_destino)

def close_driver():
    driver.close()

#Tipos de nós e seus possíveis subtipos
tipos_nodos = {
    "Pessoa": ["Diretor", "Produtor", "Avaliador"]
}

rotulos_nodos = ["Pessoa", "Diretor", "Produtor", "Avaliador", "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"]

# Exemplo de uso
quantidade_nodos = 10000
quantidade_relacionamentos = 50
with driver.session() as session:
    session.write_transaction(criar_nodos, "Filme", "titulo", "filme", quantidade_nodos) #criar nodos Filme
    for tipo_origem, subtipos in tipos_nodos.items():
        print(tipo_origem, subtipos)
        session.write_transaction(criar_nodos, tipo_origem, "nome", tipo_origem.lower(), quantidade_nodos) #criar nodos "Pessoa"
        for subtipo in subtipos:
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos, tipo_origem) # cria nodos "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos) #cria nodos "Diretor", "Produtor", "Avaliador"
            
    # for _ in range(quantidade_relacionamentos):
        #criar relacionamentos
        valorRotulo = random.randint(0, 6)
        rotulo_origem = rotulos_nodos[valorRotulo]
        print(rotulos_nodos[valorRotulo])
        session.write_transaction(criar_relacionamentos, rotulo_origem, rotulo_origem.lower(), "RELACIONADO_COM", quantidade_relacionamentos)
