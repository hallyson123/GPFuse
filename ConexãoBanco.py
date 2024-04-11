from neo4j import GraphDatabase
from Neo4j import percorrer_nos_e_armazenar_info, coletar_relacionamentos

uri = "bolt://localhost:****"  # Substitua pelo seu URI
username = "neo4j"
password = "senha"

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    nos = {}  # Dicionário para armazenar instâncias da classe No
    with driver.session() as session:
        session.read_transaction(percorrer_nos_e_armazenar_info, nos)
        session.read_transaction(coletar_relacionamentos, nos)
        