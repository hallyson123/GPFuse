import pickle

# gerar o script SQL
def gerar_script_sql(pg_schema_dict):
    script_sql = ""

    script_sql += "CREATE DATABASE TesteRel; \n"
    script_sql += "\c TesteRel\n\n"

    # Criar tipo ENUM
    for node_name, node_data in pg_schema_dict["nodes"].items():
        for prop, prop_data in node_data["properties"].items():
            if prop_data["is_enum"]:
                node = ''.join(node_name)
                tipo_enum = f"{node}_{prop}_enum"
                prop_data["typeEnum"] = tipo_enum
                script_sql += f"CREATE TYPE {tipo_enum.upper()} AS ENUM({prop_data['values']})\n"

    script_sql += "\n"

    # Iterar sobre os nós e criar tabelas
    for node_name, node_data in pg_schema_dict["nodes"].items():
        if len(node_name) > 1:
            node = '_'.join(node_name)
        else:
            node = ''.join(node_name)
        tabela_nome = node.lower()

        script_sql += f"CREATE TABLE {tabela_nome} (\n"
        primary_key_set = False 

        # Adicionar ID como primaria caso não tenha PK
        if not node_data["uniqueProperties"]:
            script_sql += "  id SERIAL PRIMARY KEY,\n"
            primary_key_set = True

        # Adicionar as colunas da tabela com as propriedades
        for prop, prop_data in node_data["properties"].items():
            # Determinar tipo da coluna
            tipo = prop_data["type"]
            if tipo == "array":
                tipo = f"{prop_data['typeList']} ARRAY[{prop_data['minList']}, {prop_data['maxList']}]"
            if tipo == "str":
                if prop_data["tamStr"] < 100:
                    tipo = f"VARCHAR(100)"
                else:
                    tipo = f"VARCHAR({prop_data["tamStr"]})"
            if tipo == "int":
                tipo = "integer"
            if tipo == "float":
                tipo = f"real"

            if prop_data["is_enum"]:
                tipo = prop_data["typeEnum"]

            # Adicionar constraints de unicidade
            if prop_data["unique"]:
                tipo += " UNIQUE"
            # Adicionar constraints de obrigatoriedade
            if not prop_data["optional"]:
                tipo += " NOT NULL"

            script_sql += f"  {prop} {tipo.upper()},\n"

        # Chave primaria
        if node_data["uniqueProperties"] and not primary_key_set:
            if len(node_data["uniqueProperties"]) == 1:
                prop_primary = node_data["uniqueProperties"][0]
                script_sql += f"  CONSTRAINT pk_{node} PRIMARY KEY ({prop_primary}) \n"
            else:
            # Chave composta
                chave_composta = ', '.join(node_data["uniqueProperties"])
                script_sql += f"  CONSTRAINT pk_{node} PRIMARY KEY ({chave_composta}), \n"
            primary_key_set = True

        script_sql = script_sql.rstrip(",\n")
        script_sql += "\n);\n\n"

        # Especialização (filho recebe FK do pai)
        if len(node_name) > 1:
            pai_tuple = node_name[0]
            pai = ''.join(pai_tuple)
            pai_key = (pai,)

            pai_fk = pg_schema_dict["nodes"][pai_key]["uniqueProperties"]  # Chaves únicas do pai
            fk_columns = []  # Armazena as colunas que formam a FK

            for prop in pai_fk:
                tipo_pai = pg_schema_dict["nodes"][pai_key]["properties"][prop]["type"]
                tam = pg_schema_dict["nodes"][pai_key]["properties"][prop]["tamStr"]
                if tipo_pai == "str":
                    if tam < 100:
                        tipo_pai = "VARCHAR(100)"
                    else:
                        tipo_pai = f"VARCHAR({tam})"
                if tipo_pai == "float":
                    tipo_pai = "REAL"
                if tipo_pai == "int":
                    tipo_pai = "INTEGER"

                script_sql += f"ALTER TABLE {tabela_nome} ADD COLUMN {pai.lower()}_{prop} {tipo_pai.upper()};\n"
                fk_columns.append(f"{pai.lower()}_{prop}")

            # Criar a constraint da FK
            fk_columns_str = ", ".join(fk_columns)
            pai_columns_str = ", ".join(pai_fk)
            script_sql += f"ALTER TABLE {tabela_nome} ADD CONSTRAINT fk_{tabela_nome}_{pai.lower()} FOREIGN KEY ({fk_columns_str}) REFERENCES {pai.lower()}({pai_columns_str});\n\n"

    return script_sql

# Carregar o dicionário
file_path = "GraphRel/nos_dump.pkl"
# file_path = "GraphRel/airbnb.pkl"

with open(file_path, "rb") as f:
    pg_schema_dict = pickle.load(f)

# Gerar o script SQL
script_sql = gerar_script_sql(pg_schema_dict)

# Salvar o script em um arquivo SQL
with open("GraphRel/graph_to_rel.sql", "w") as f:
    f.write(script_sql)

print("Script SQL gerado com sucesso: graph_to_rel.sql")
