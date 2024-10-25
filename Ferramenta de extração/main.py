from ConexãoBanco import nos, start_time
from Neo4j import marcar_propriedades_compartilhadas, definir_enum
import time
import pickle

THRESHOLD = 0.9

print("-----------------------")
# Chamar a função para marcar propriedades compartilhadas
marcar_propriedades_compartilhadas(nos)
print("-----------------------")

def gerar_pg_schema_dicionario(nos):
    pg_schema_dict = {
        "graph_type": "TesteGraphType",
        "strict": True,
        "nodes": {},
        "relationships": [],
    }

    # Preencher o dicionário com as informações dos nós
    for rotulos, no in nos.items():
        # Adicionar as propriedades do nó
        propriedades_dict = {}
        listaProp = []
        for propriedade, info_propriedade in no.propriedades.items():
            tipo_propriedade = max(info_propriedade["tipos"], key=info_propriedade["tipos"].get) # Tipo mais presente

            lista = None
            tipo_maior_freq = None
            tam_max_lista = None
            tam_min_lista = None
            if info_propriedade["is_list"]:
                tipo_propriedade = "array"
                tipo_maior_freq = max(info_propriedade["tipos_listas"], key=info_propriedade["tipos_listas"].get)
                tam_min_lista = float('inf')
                tam_max_lista = float('-inf')

                for tamanho in info_propriedade["tamQuantLista"]:
                    if tamanho < tam_min_lista:
                        tam_min_lista = tamanho
                    if tamanho > tam_max_lista:
                        tam_max_lista = tamanho

            # Armazenar o tamanho máximo de uma String
            tamanho_str = 0
            if tipo_propriedade == "str":
                tamanho_str = max(len(valor) for valor in info_propriedade["PropValues"])
            
            # Definir Enum
            valores_enum = ', '.join(f'"{val}"' for val in info_propriedade.get("values"))
            definir_enum(no.quantidade, info_propriedade, no)

            # Constraint de obrigatoriedade
            if info_propriedade["total"] / no.quantidade >= THRESHOLD:
                opcional = False
            else:
                opcional = True

            # Constraint de unicidade
            unique = False
            if info_propriedade["constraint"] and "UNIQUENESS" in info_propriedade["constraintList"]:
                if len(nos[rotulos].listaChaveUnica):
                    listaProp.extend(nos[rotulos].listaChaveUnica)
                    unique = True
                else: 
                    listaProp.extend(info_propriedade["listProp"])
                    unique = True

            propriedades_dict[propriedade] = {
                "type": tipo_propriedade,
                "tamStr": tamanho_str,
                "optional": opcional,
                "unique": unique,
                "shared": info_propriedade["is_shared"],
                "is_enum": info_propriedade["is_enum"],
                "values": valores_enum,
                "is_list": info_propriedade["is_list"],
                "typeList": tipo_maior_freq,
                "maxList": tam_max_lista,
                "minList": tam_min_lista
            }

        # Adicionar o nó ao dicionário final
        rotulos_str = ' & '.join(rotulos)
        node_type = f"{rotulos_str}Type"
        pg_schema_dict["nodes"][rotulos] = {
            "type": node_type,
            "properties": propriedades_dict,
            "uniqueProperties": listaProp
        }

    # Preencher o dicionário com os relacionamentos
    for rotulos, no in nos.items():
        for tipo_relacionamento, relacoes in no.relacionamentos.items():
            for destino, _ in relacoes:
                pg_schema_dict["relationships"].append({
                    "origin": rotulos,
                    "relationship_type": tipo_relacionamento,
                    "destination": destino,
                    "cardinality": no.cardinalidades.get(tipo_relacionamento, "")
                })
                
    return pg_schema_dict

def gerar_saida_pg_schema(pg_schema_dict):
    schema = f"CREATE GRAPH TYPE {pg_schema_dict['graph_type']} "
    schema += "STRICT {\n" if pg_schema_dict['strict'] else "{\n"

    # Adicionar nós e suas propriedades
    for node, info in pg_schema_dict['nodes'].items():
        node_str = ' & '.join(node)
        schema += f"({info['type']} : {node_str} {{\n"

        for prop, prop_info in info['properties'].items():
            tipo_propriedade = prop_info['type'].upper()
            lista_max_min = f"{prop_info['typeList']} {prop_info['minList'], prop_info['maxList']}"
            lista = {lista_max_min} if prop_info['is_list'] else ""
            lista_ = ', '.join(lista)
            opcional = "OPTIONAL " if prop_info['optional'] else ""
            compartilhada = "*" if prop_info['shared'] else ""
            enum_str = ""
            if prop_info['is_enum']:
                enum_str = f"ENUM ({info['properties'][prop]['values']})"
                schema += f"    {opcional}{compartilhada}{prop} {enum_str},\n"
            else:
                schema += f"    {opcional}{compartilhada}{prop} {tipo_propriedade}{lista_}{enum_str},\n"

        schema = schema.rstrip(",\n")
        schema += "}),\n\n"

    # Adicionar relacionamentos
    for rel in pg_schema_dict['relationships']:
        destino_str = ' & '.join(rel['destination'])
        origem_str = ' | '.join(rel['origin'])
        schema += f"(:{origem_str})-[{rel['relationship_type']}Type {rel['cardinality']}]->(:{destino_str}Type),\n"

    schema += "\n"

    # Cosntraint Mandatory
    for node, info in pg_schema_dict['nodes'].items():
        node_str = ':'.join(node)
        node_ = f"{node_str}Type"
        for prop, prop_info in info['properties'].items():
            if prop_info['optional'] == False:
                schema += f"FOR (x:{node_}) MANDATORY x.{prop},\n"

    schema += "\n"

    # Constraint Singleton
    for node, info in pg_schema_dict['nodes'].items():
            node_str = ':'.join(node)
            node_ = f"{node_str}Type"

            listaProp = []
            listaProp.extend(info["uniqueProperties"])
            propriedades_concatenadas = ', '.join(listaProp)  # Concatena todas as propriedades em uma única string

            if len(info['uniqueProperties']) > 1 and len(info['uniqueProperties']) <= 2:
                schema += f"FOR (x:{node_}) SINGLETON x.({propriedades_concatenadas}),\n"
            if len(info['uniqueProperties']) == 1:
                schema += f"FOR (x:{node_}) SINGLETON x.{propriedades_concatenadas},\n"

    schema = schema.rstrip(",\n")
    schema += "\n}"

    return schema

def salvar_nos_pickle(nos, file_path):
    with open(file_path, 'wb') as f:
        pickle.dump(nos, f)
    print(f"Dicionário 'PG-Schema' salvo em: {file_path}")

# Criar o dicionário de PG-Schema
pg_schema_dict = gerar_pg_schema_dicionario(nos)

# Gerar a saída do PG-Schema
saida_pg_schema = gerar_saida_pg_schema(pg_schema_dict)
print(saida_pg_schema)

file_path = "GraphRel/nos_dump.pkl"

# Salvar o dicionário 'nos' usando pickle
salvar_nos_pickle(pg_schema_dict, file_path)
