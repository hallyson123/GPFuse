from neo4j import GraphDatabase
from Neo4j import percorrer_nos_e_armazenar_info, percorrer_relacionamentos

uri = "bolt://3.239.19.213:7687"  # Substitua pelo seu URI
username = "neo4j"
password = "nation-combs-concept"

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    nos = {}  # Dicionário para armazenar instâncias da classe No
    with driver.session() as session:
        session.read_transaction(percorrer_nos_e_armazenar_info, nos)
        session.read_transaction(percorrer_relacionamentos, nos)