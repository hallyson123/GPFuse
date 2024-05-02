from neo4j import GraphDatabase
import random
from criar_nodos import criar_nodos
from criar_relacionamentos import rel_pessoas_filmes, rel_financiadores_filmes
from criar_restricao import criar_restricao

uri = "bolt://localhost:7687"  # Substitua pelo seu URI
user = "neo4j"
password = "1F16EBD3"

driver = GraphDatabase.driver(uri, auth=(user, password))

#Tipos de nós e seus possíveis subtipos
tipos_nodos = {
    "Pessoa": ["Diretor", "Produtor", "Avaliador"]
}

rotulos_nodos = ["Pessoa", "Diretor", "Produtor", "Avaliador", "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"]
sites_avaliações = ["HBO Max", "Amazon Prime", "Netflix", "Globoplay", "Disney+", "Star+", "Paramount+", "Apple TV+"]

# Exemplo de uso
quantidade_nodos = 200
quantidade_relacionamentos = 100
max_enumerate = 10
obrigatorio = True

with driver.session() as session:
    #Criar restriçao
    session.write_transaction(criar_restricao, "Filme", "titulo")
    session.write_transaction(criar_restricao, "Streaming", "nome")
    session.write_transaction(criar_restricao, "Financiador", "nome")

    #Criar nodos para testar enumerate
    for _ in range(max_enumerate):
        indice = random.randint(0, 7)
        session.write_transaction(criar_nodos, "Streaming", "nome", sites_avaliações[indice], max_enumerate, subtipo = None, enumerate_valor_max= max_enumerate)

    #Criar nodos Pessoa e seus subtipos
    for tipo_origem, subtipos in tipos_nodos.items():
        session.write_transaction(criar_nodos, tipo_origem, "nome", tipo_origem.lower(), quantidade_nodos) #criar nodos "Pessoa"
        for subtipo in subtipos:
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos, tipo_origem) # cria nodos "Pessoa:Diretor", "Pessoa:Produtor", "Pessoa:Avaliador"
            session.write_transaction(criar_nodos, subtipo, "nome", subtipo.lower(), quantidade_nodos) #cria nodos "Diretor", "Produtor", "Avaliador"
            
    #criar relacionamentos (1,N):(0,N)
    for _ in range(quantidade_relacionamentos):
        valorRotulo = random.randint(0, 6)
        rotulo_origem = rotulos_nodos[valorRotulo]
        session.write_transaction(rel_pessoas_filmes, rotulo_origem, rotulo_origem.lower(), quantidade_relacionamentos)

    #criar relacionamentos (0,1):(1,1)
    for _ in range(max_enumerate):
        propriedade = f"financiador_{random.randint(1, 10)}"
        session.write_transaction(criar_nodos, "Financiador", "nome", propriedade, max_enumerate, subtipo = None, enumerate_valor_max= max_enumerate)

    session.write_transaction(rel_financiadores_filmes, 10)