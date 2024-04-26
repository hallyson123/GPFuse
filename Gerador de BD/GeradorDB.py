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
                    result_enum = tx.run(f"MATCH (n:{rotulo}) WHERE n.nome = $enumerate_propriedade RETURN n", enumerate_propriedade=atributo)
                    if result_enum.peek() is None:
                        tx.run(f"CREATE (:{rotulo} {{nome: $enumerate_propriedade}})", enumerate_propriedade=atributo)
                        enumerate_valor_max = enumerate_valor_max - 1
                    else:
                        print(f"Nodo com [{propriedade}: '{atributo}]' já existe.")
                else:
                    tx.run(f"CREATE (:{rotulo} {{{propriedade}: $atributo, lista_propriedade: $lista}})",
                           atributo=valor, lista=lista_valores)
        else:
            print(f"Nodo com [{propriedade}: '{valor}]' já existe.")

def criar_relacionamentos(tx, tipo_origem, propriedade_origem, quantidade):
    # Para cada nó de origem, criar um relacionamento com um nó de destino (Filme)
    result = tx.run(f"MATCH(origem:{tipo_origem}) RETURN count(origem) AS quantidade_rotulos")
    limite = result.single()["quantidade_rotulos"]
    quantidade_relacionamentos = random.randint(1, limite) 
    for _ in range(quantidade_relacionamentos):
        valor_origem = f"{propriedade_origem}_{random.randint(1, 100)}"  # Gerar um valor aleatório para a propriedade do nó de origem
        valor_destino = f"filme_{random.randint(1, 100)}"  # Gerar um valor aleatório para o título do nó de destino (Filme)
        
        # Determinar o tipo de relacionamento com base no tipo de nó de origem
        tipo_relacionamento = tipo_origem.upper()[:6]  # Pegar as três primeiras letras do tipo de origem
        # Criar o relacionamento entre o nó de origem e o nó de destino (Filme)
        tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }}), (destino:Filme {{ titulo: $propriedade_destino }}) "
               f"MERGE (origem)-[:{tipo_relacionamento}]->(destino)", propriedade_origem=valor_origem, propriedade_destino=valor_destino)
        
        # Verificar se o relacionamento foi criado com sucesso
        result = tx.run(f"MATCH (origem:{tipo_origem} {{ nome: $propriedade_origem }})-[:{tipo_relacionamento}]->(destino:Filme {{ titulo: $propriedade_destino }}) "
                        "RETURN COUNT(*) AS count", propriedade_origem=valor_origem, propriedade_destino=valor_destino)
        count = result.single()["count"]
        if count > 0:
            print(f"Relacionamento criado entre [{tipo_origem}] e [Filme] ({valor_origem})")
        else:
            print(f"Não foi possível criar relacionamento entre [{tipo_origem}] e [Filme] ({valor_origem})")

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
sites_avaliações = ["HBO Max", "Amazon Prime", "Netflix", "Globoplay", "Disney+", "Star+", "Paramount+", "Apple TV+"]

# Exemplo de uso
quantidade_nodos = 100
quantidade_relacionamentos = 100
max_enumerate = 10

with driver.session() as session:
    #Criar restriçao
    session.write_transaction(criar_restricao, "Filme", "titulo")

    #Criar nodos para testar enumerate
    for _ in range(max_enumerate):
        indice = random.randint(0, 7)
        session.write_transaction(criar_nodos, "Streaming", "nome", sites_avaliações[indice], max_enumerate, subtipo = None, enumerate_valor_max= max_enumerate)

    # Criar nodos Filme
    session.write_transaction(criar_nodos, "Filme", "titulo", "filme", quantidade_nodos) #criar nodos Filme
    
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
        # print(rotulos_nodos[valorRotulo])
        session.write_transaction(criar_relacionamentos, rotulo_origem, rotulo_origem.lower(), quantidade_relacionamentos)
