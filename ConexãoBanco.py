from neo4j import GraphDatabase
from Neo4j import percorrer_nos_e_armazenar_info, coletar_relacionamentos

# uri = "bolt://3.219.215.172:7687"  # Substitua pelo seu URI
# username = "neo4j"
# password = "machinery-hammers-pail"

uri = "neo4j+s://a5521bb9.databases.neo4j.io"  # Substitua pelo seu URI
username = "neo4j"
password = "za9wj_xORNzz6v_pL2NVH-Gp7fS7p7YthqLbVfK0XY8"

with GraphDatabase.driver(uri, auth=(username, password)) as driver:
    nos = {}  # Dicionário para armazenar instâncias da classe No
    with driver.session() as session:
        session.read_transaction(percorrer_nos_e_armazenar_info, nos)
        session.read_transaction(coletar_relacionamentos, nos)
        