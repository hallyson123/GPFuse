import pickle

# gerar o script SQL
def gerar_script_sql(pg_schema_dict):
    script_sql = ""

    script_sql += "CREATE DATABASE TesteRel; \n"
    script_sql += "\c TesteRel\n\n"

    # Criar tipo ENUM (nodos)
    for node_name, node_data in pg_schema_dict["nodes"].items():
        for prop, prop_data in node_data["properties"].items():
            if prop_data["is_enum"]:
                node = ''.join(node_name)
                tipo_enum = f"{node}_{prop}_enum"
                prop_data["typeEnum"] = tipo_enum
                script_sql += f"CREATE TYPE {tipo_enum.upper()} AS ENUM({prop_data['values']})\n"

    script_sql += "\n"

    # Criar tipo ENUM (relacionamentos)
    for rel in pg_schema_dict["relationships"]:
        rel_name = rel["relationship_type"].lower()
        origem = '_'.join(rel["origin"]).lower()
        destino = '_'.join(rel["destination"]).lower()
        rel_table = f"{origem}_{rel_name}Rel_{destino}"

        for prop, prop_data in rel["properties"].items():
            if prop_data["is_enum"]:
                tipo_enum = f"{rel_table}_{prop}_enum"
                prop_data["typeEnum"] = tipo_enum
                script_sql += f"CREATE TYPE {tipo_enum.upper()} AS ENUM({prop_data['valores_enum']})\n"

    script_sql += "\n"

    # Criar tabelas para os nós
    for node_name, node_data in pg_schema_dict["nodes"].items():
        if len(node_name) > 1:
            node = '_'.join(node_name)
        else:
            node = ''.join(node_name)
        tabela_nome = node.lower()

        script_sql += f"CREATE TABLE {tabela_nome} (\n"
        primary_key_set = False

        if not node_data["uniqueProperties"]:
            script_sql += "  id SERIAL PRIMARY KEY,\n"
            node_data["primary_key_info"] = [{"nome_propriedade": "id", "nome_chave": "id", "tipo_propriedade": "INTEGER", "composta": False}]
            primary_key_set = True

        for prop, prop_data in node_data["properties"].items():
            tipo = prop_data["type"]
            if tipo == "array":
                tipo = f"{prop_data['typeList']} ARRAY[{prop_data['minList']}, {prop_data['maxList']}]"
            if tipo == "str":
                tipo = f"VARCHAR({prop_data['tamStr']})" if prop_data["tamStr"] >= 100 else "VARCHAR(100)"
            if tipo == "int":
                tipo = "integer"
            if tipo == "float":
                tipo = "real"
            if prop_data["is_enum"]:
                tipo_enum = prop_data["typeEnum"]
                tipo = prop_data["typeEnum"]

            if prop_data["unique"]:
                tipo += " UNIQUE"
            if not prop_data["optional"]:
                tipo += " NOT NULL"

            tipo_fk = []
            if node_data["uniqueProperties"] and not primary_key_set:
                # print(node_name, prop, pg_schema_dict["nodes"][node_name]['properties'][prop]['type'])
                tipo_aux = pg_schema_dict["nodes"][node_name]['properties'][prop]['type']
                tipo_fk.append(tipo_aux.upper())
                # print(tipo_fk)

            script_sql += f"  {prop} {tipo.upper()},\n"

        if node_data["uniqueProperties"] and not primary_key_set:
            node_data["primary_key_info"] = []
            if len(node_data["uniqueProperties"]) == 1:
                prop_primary = node_data["uniqueProperties"][0]
                script_sql += f"  CONSTRAINT pk_{node.lower()} PRIMARY KEY ({prop_primary}) \n"
                
                node_data["primary_key_info"].append({"nome_propriedade": prop_primary, "nome_chave": f"{tabela_nome}", "tipo_propriedade": tipo_fk, "composta": False})
            
            else:
                chave_composta = node_data["uniqueProperties"]
                script_sql += f"  CONSTRAINT pk_{node.lower()} PRIMARY KEY ({chave_composta}), \n"

                node_data["primary_key_info"].append({"nome_propriedade": chave_composta, "nome_chave": f"{tabela_nome}", "tipo_propriedade": tipo_fk, "composta": True})

            primary_key_set = True

        script_sql = script_sql.rstrip(",\n")
        script_sql += "\n);\n\n"

    # Adicionar relacionamentos
    for rel in pg_schema_dict["relationships"]:
        # print(rel)
        rel_name = rel["relationship_type"].lower()
        origem = '_'.join(rel["origin"]).lower()
        destino = '_'.join(rel["destination"]).lower()

        origem_info = pg_schema_dict["nodes"][rel["origin"]]["primary_key_info"]

        if rel["destination"]:
            destino_info = pg_schema_dict["nodes"][rel["destination"]]["primary_key_info"] #VERIFICAR PQ N APARECE O DESTINO

        # Interpreta a cardinalidade para definir as constraints
        origem_card, destino_card = rel["cardinality"].split(';')
        origem_min, origem_max = origem_card[1:-1].split(':')
        destino_min, destino_max = destino_card[1:-1].split(':')

        rel_table = f"{origem}_{rel_name}Rel_{destino}"

        # MUITOS PARA MUITOS (N:N)
        if origem_max == "N" and destino_max == "N" and origem != destino:
            script_sql += f"CREATE TABLE {rel_table} (\n"

            foreign_keys = ""

            # Chaves estrangeiras para origem e destino (criar colunas )
            for pk in origem_info:
                nome_propriedade = pk['nome_propriedade']
                if pk['composta']:
                    for nome in nome_propriedade:
                        tipo = pg_schema_dict["nodes"][rel['origin']]['properties'][nome]['type']
                        if tipo == "str":
                            tipo = f"VARCHAR({prop_data.get('tamStr', 100)})"
                        if tipo == "int":
                            tipo = "INTEGER"
                        if tipo == "float":
                            tipo = "REAL"
                        script_sql += f"  {pk['nome_chave']}_{nome} {tipo.upper()},\n"
                        foreign_keys += f"  FOREIGN KEY ({pk['nome_chave']}_{nome}) REFERENCES {origem}({nome}),\n"
                else:
                    if pk['nome_propriedade'] == 'id':
                        script_sql += f"  {origem}_id {pk['tipo_propriedade']},\n"
                        foreign_keys += f"  FOREIGN KEY ({origem}_{nome_propriedade}) REFERENCES {origem}({pk['nome_propriedade']}),\n"
                    else:
                        tipo = pg_schema_dict["nodes"][rel['origin']]['properties'][pk['nome_propriedade']]['type']
                        if tipo == "str":
                            tipo = f"VARCHAR({prop_data.get('tamStr', 100)})"
                        if tipo == "int":
                            tipo = "INTEGER"
                        if tipo == "float":
                            tipo = "REAL"
                        script_sql += f"  {pk['nome_chave']}_{nome_propriedade} {tipo.upper()},\n"
                        foreign_keys += f"  FOREIGN KEY ({pk['nome_chave']}_{nome_propriedade}) REFERENCES {origem}({pk['nome_propriedade']}),\n"

            for pk in destino_info:
                nome_propriedade = pk['nome_propriedade']
                if pk['composta']:
                    for nome in nome_propriedade:
                        tipo = pg_schema_dict["nodes"][rel["destination"]]['properties'][nome]['type']
                        if tipo == "str":
                            tipo = f"VARCHAR({prop_data.get('tamStr', 100)})"
                        if tipo == "int":
                            tipo = "INTEGER"
                        if tipo == "float":
                            tipo = "REAL"
                        script_sql += f"  {pk['nome_chave']}_{nome} {tipo.upper()},\n"
                        foreign_keys += f"  FOREIGN KEY ({pk['nome_chave']}_{nome}) REFERENCES {destino}({nome}),\n"
                else:
                    if pk['nome_propriedade'] == 'id':
                        script_sql += f"  {destino}_id {pk['tipo_propriedade']},\n"
                        foreign_keys += f"  FOREIGN KEY ({destino}_{nome_propriedade}) REFERENCES {destino}({pk['nome_propriedade']}),\n"
                    else:
                        tipo = pg_schema_dict["nodes"][rel["destination"]]['properties'][pk['nome_propriedade']]['type']
                        if tipo == "str":
                            tipo = f"VARCHAR({prop_data.get('tamStr', 100)})"
                        if tipo == "int":
                            tipo = "INTEGER"
                        if tipo == "float":
                            tipo = "REAL"
                        if prop_data["is_enum"]:
                            tipo = prop_data["typeEnum"]
                        script_sql += f"  {pk['nome_chave']}_{nome_propriedade} {tipo.upper()},\n"
                        foreign_keys += f"  FOREIGN KEY ({pk['nome_chave']}_{nome_propriedade}) REFERENCES {destino}({pk['nome_propriedade']}),\n"

            # Propriedades do relacionamento
            for prop, prop_data in rel["properties"].items():
                # print(prop, prop_data)
                tipo = ','.join(prop_data["tipos"])
                # print(tipo)
                if tipo == "str":
                    tipo = f"VARCHAR({prop_data.get('tamStr', 100)})" #AJUSTAR
                if tipo == "int":
                    tipo = "INTEGER"
                if tipo == "float":
                    tipo = "REAL"
                if prop_data["is_enum"]:
                    tipo = prop_data["typeEnum"]

                # Adicionar constraints de unicidade ou obrigatoriedade
                if prop_data.get("is_singleton"):
                    tipo += "UNIQUE"
                if prop_data.get("is_mandatory"):
                    tipo += f" NOT NULL"
                
                script_sql += f"  {prop} {tipo.upper()},\n"

                # Criar contraints primary key
                if len(rel['primary_key']) >= 1:
                    if len(rel['primary_key']) == 1:
                        prop_primary = node_data["uniqueProperties"][0]
                        script_sql += f"  CONSTRAINT pk_{rel_table} PRIMARY KEY ({prop_primary}) \n"
                    else:
                        chave_composta = ', '.join(node_data["uniqueProperties"])
                        script_sql += f"  CONSTRAINT pk_{rel_table} PRIMARY KEY ({chave_composta}) \n"          

            script_sql += foreign_keys.rstrip(",\n")
            script_sql += "\n);\n\n"

            # print(origem, nome, pg_schema_dict["nodes"][rel['origin']]['properties'][nome]['type'])
            # script_sql += f"  {pk['nome_chave']}_{nome} {tipo_prop.upper()} REFERENCES {origem}({nome}),\n"" 

        # TRATAR AUTORELACIONAMENTO
        elif origem == destino:
            for pk in origem_info:
                nome_propriedade = pk['nome_propriedade']
                if pk['composta']:
                    for nome in nome_propriedade:
                        tipo = pg_schema_dict["nodes"][rel["origin"]]['properties'][nome]['type']
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {origem}_{rel_name}_origin_{nome} {tipo},\n"
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {origem}_{rel_name}_destination_{nome} {tipo},\n"
                        script_sql += f"FOREIGN KEY ({origem}_{rel_name}_origin) REFERENCES {origem}({nome}),\n"
                        script_sql += f"FOREIGN KEY ({origem}_{rel_name}_destination) REFERENCES {origem}({nome});\n\n"
                else:
                    if pk['nome_propriedade'] == 'id':
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {origem}_{rel_name}_origin INTEGER,\n"
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {origem}_{rel_name}_destination INTEGER,\n"
                        script_sql += f"FOREIGN KEY ({origem}_{rel_name}_origin) REFERENCES {origem}({pk['nome_propriedade']}),\n"
                        script_sql += f"FOREIGN KEY ({origem}_{rel_name}_destination) REFERENCES {origem}({pk['nome_propriedade']});\n\n"
                    else:
                        tipo = pg_schema_dict["nodes"][rel['origin']]['properties'][pk['nome_propriedade']]['type']
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {origem}_{rel_name}_origin {tipo},\n"
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {origem}_{rel_name}_destination {tipo},\n"
                        script_sql += f"FOREIGN KEY ({origem}_{rel_name}_origin) REFERENCES {origem}({nome_propriedade}),\n"
                        script_sql += f"FOREIGN KEY ({origem}_{rel_name}_destination) REFERENCES {origem}({nome_propriedade});\n\n"

        elif origem_max == "1" and destino_max == "N":  # 1:N
            for pk in origem_info:
                nome_propriedade = pk['nome_propriedade']
                if pk["composta"]:
                    for nome in nome_propriedade:
                        tipo = pg_schema_dict["nodes"][rel["origin"]]['properties'][nome]['type']
                        script_sql += f"ALTER TABLE {destino} ADD COLUMN {origem}_{nome} {tipo},\n"
                        script_sql += f"FOREIGN KEY ({origem}_{nome}) REFERENCES {origem}({nome});\n\n"
                else:
                    if pk['nome_propriedade'] == 'id':
                        script_sql += f"ALTER TABLE {destino} ADD COLUMN {origem}_id INTEGER,\n"
                        script_sql += f"FOREIGN KEY ({origem}_id) REFERENCES {origem}(id);\n\n"
                    else:
                        tipo = pg_schema_dict["nodes"][rel["origin"]]['properties'][nome_propriedade]['type']
                        script_sql += f"ALTER TABLE {destino} ADD COLUMN {origem}_{nome_propriedade} {tipo},\n"
                        script_sql += f"FOREIGN KEY ({origem}_{nome_propriedade}) REFERENCES {origem}({nome_propriedade});\n\n"

        elif origem_max == "N" and destino_max == "1":  # N:1
            for pk in destino_info:
                nome_propriedade = pk['nome_propriedade']
                if pk["composta"]:
                    for nome in nome_propriedade:
                        tipo = pg_schema_dict["nodes"][rel["destination"]]['properties'][nome]['type']
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {destino}_{nome} {tipo},\n"
                        script_sql += f"FOREIGN KEY ({destino}_{nome}) REFERENCES {destino}({nome});\n\n"
                else:
                    if pk['nome_propriedade'] == 'id':
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {destino}_id INTEGER,\n"
                        script_sql += f"FOREIGN KEY ({destino}_id) REFERENCES {origem}(id);\n\n"
                    else:
                        if rel["destination"]:
                            tipo = pg_schema_dict["nodes"][rel["destination"]]['properties'][nome_propriedade]['type']
                        script_sql += f"ALTER TABLE {origem} ADD COLUMN {destino}_{nome_propriedade} {tipo},\n"
                        script_sql += f"FOREIGN KEY ({destino}_{nome_propriedade}) REFERENCES {destino}({nome_propriedade});\n\n"

        elif origem_max == "1" and destino_max == "1":
            print(origem, destino)
            merge_origin = pg_schema_dict["nodes"][rel["origin"]]['merge']
            merge_destination = pg_schema_dict["nodes"][rel["destination"]]['merge']

            if merge_origin and merge_destination:
                print("SIM")
                # Caso 1: Alta ocorrência, criar tabela unificada
                script_sql += f"CREATE TABLE {origem}_unificada_{destino} (\n"
                
                # Adiciona colunas da tabela de origem
                for pk in origem_info:
                    script_sql += f"  {pk['nome_propriedade']} {pk['tipo_propriedade']},\n"

                # Adiciona colunas da tabela de destino
                for pk in destino_info:
                    script_sql += f"  {pk['nome_propriedade']} {pk['tipo_propriedade']},\n"
                
                # Define a chave primária composta
                script_sql += f"  PRIMARY KEY ({origem}_id, {destino}_id)\n"
                script_sql += ");\n\n"
            
            else:
                # Caso 2: Baixa ocorrência, chave estrangeira no destino
                script_sql += f"ALTER TABLE {destino} ADD COLUMN {origem}_id INT,\n"
                script_sql += f"FOREIGN KEY ({origem}_id) REFERENCES {origem}(id);\n\n"

    return script_sql

# Carregar o dicionário
file_path = "GraphRel/nos_dump.pkl"
# file_path = "GraphRel/airbnb.pkl"
# file_path = "GraphRel/movie.pkl"

with open(file_path, "rb") as f:
    pg_schema_dict = pickle.load(f)

# Gerar o script SQL
script_sql = gerar_script_sql(pg_schema_dict)

# Salvar o script em um arquivo SQL
with open("GraphRel/graph_to_rel.sql", "w") as f:
    f.write(script_sql)

print("Script SQL gerado com sucesso: graph_to_rel.sql")
