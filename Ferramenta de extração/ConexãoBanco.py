from neo4j import GraphDatabase
from Neo4j import percorrer_nos_e_armazenar_info, coletar_relacionamentos, retornar_constraint
import time

uri = "bolt://localhost:????"  # Substitua pelo seu URI
username = "user"
password = "senha"

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    nos = {}  # Dicionário para armazenar instâncias da classe No
    with driver.session() as session:
        start_time = time.time()  # Marcar o tempo de início
        session.read_transaction(percorrer_nos_e_armazenar_info, nos)
        session.read_transaction(coletar_relacionamentos, nos)
        session.read_transaction(retornar_constraint, nos)
        