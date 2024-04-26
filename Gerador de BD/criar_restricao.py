def criar_restricao(tx, rotulo, propriedade):
    result = tx.run("SHOW CONSTRAINT")
    constraint_exists = False
    for record in result:
        nodo_rotulo = record["labelsOrTypes"]
        pripriedade_rotulo = record["properties"]

        if rotulo in nodo_rotulo and propriedade in pripriedade_rotulo:
            print(f"Restrição com o nodo [{rotulo}] e propriedade [{propriedade}] já existe.")
            constraint_exists = True
            break
    
    if not constraint_exists:
        tx.run(f"CREATE CONSTRAINT Unique{rotulo} FOR (n:{rotulo}) REQUIRE n.{propriedade} IS UNIQUE")
