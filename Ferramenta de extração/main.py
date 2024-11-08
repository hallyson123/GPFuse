from ConexãoBanco import nos, start_time
from Neo4j import marcar_propriedades_compartilhadas, definir_enum
import time
import pickle

MAX_ENUMERATE = 20
THRESHOLD = 0.9
THRESHOLD_OCCURRENCE = 0.7

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
        # Supertipo seguido de subtipos
        if len(rotulos) >= 2:
            # Tupla de supertipo e subtipos
            chave_ordenada = tuple(no.supertipos + no.subtipos)
        else:
            chave_ordenada = tuple(rotulos)

        # Adicionar as propriedades do nó
        propriedades_dict = {}
        listaProp = []
        for propriedade, info_propriedade in no.propriedades.items():
            tipo_propriedade = max(info_propriedade["tipos"], key=info_propriedade["tipos"].get) # Tipo mais presente

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
            if info_propriedade["constraint"] and "UNIQUENESS" in info_propriedade["constraintList"] or "NODE_KEY" in info_propriedade["constraintList"]:
                if len(nos[rotulos].listaChaveUnica):
                    # if nos[rotulos].listaChaveUnica not in listaProp:
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
                "minList": tam_min_lista,
            }

        # Adicionar o nó ao dicionário final
        rotulos_str = ' & '.join(chave_ordenada)
        node_type = f"{rotulos_str}Type"
        pg_schema_dict["nodes"][chave_ordenada] = {
            "type": node_type,
            "properties": propriedades_dict,
            "uniqueProperties": listaProp,
            "supertypes": no.supertipos,
            "subtypes": no.subtipos,
        }
        # print(pg_schema_dict["nodes"][chave_ordenada])

    # Preencher o dicionário com os relacionamentos
    for rotulos, no in nos.items():
        for tipo_relacionamento, relacoes in no.relacionamentos.items():
            for destino, quantidade, propriedades in relacoes:
                # Armazenar propriedades chave
                chaves = []
                for nome, info_propriedade in propriedades.items():
                    # Unicidade
                    if len(info_propriedade['valores_unicos']) / info_propriedade['total'] >= THRESHOLD:
                        info_propriedade['is_singleton'] = True
                    info_propriedade['valores_unicos'].clear()

                    # Obrigatoriedade
                    if info_propriedade['total'] / quantidade >= THRESHOLD:
                        info_propriedade['is_mandatory'] = True

                    # Enumeração
                    if len(info_propriedade['valores_enum']) <= 1:
                        info_propriedade['is_enum'] = False
                        info_propriedade['valores_enum'].clear()

                    if info_propriedade.get('is_mandatory') and info_propriedade.get('is_singleton'):
                        chaves.append(nome)

                # Supertipo seguido de subtipos
                if len(rotulos) >= 2:
                    # Tupla de supertipo e subtipos
                    chave_ordenada_origem = tuple(no.supertipos + no.subtipos)
                    # print(chave_ordenada_origem)
                else:
                    chave_ordenada_origem = rotulos

                if len(destino) >= 2:
                    chave_ordenada_destino = tuple(no.supertipos + no.subtipos)
                    print(destino, chave_ordenada_destino)
                else:
                    chave_ordenada_destino = tuple(destino)

                # print(f"{chave_ordenada_origem}->{chave_ordenada_destino} [{destino}] ({len(destino)})")
                # print(rotulos, no.quantidade, propriedade, info_propriedade['total'])
                # print(rotulos, nos[rotulos].quantidade, destino, nos[destino].quantidade, tipo_relacionamento, quantidade)
                # print(no.cardinalidades[tipo_relacionamento])
                
                origem_card, destino_card = no.cardinalidades[tipo_relacionamento].split(';')
                origem_min, origem_max = origem_card[1:-1].split(':')
                destino_min, destino_max = destino_card[1:-1].split(':')

                merge = False
                more_occurrence = None
                if origem_max == "1" and destino_max == "1":
                    # Verificar se é necessário fusionar os nodos envolvidos no relacionamento (1;1)
                    if (quantidade / nos[rotulos].quantidade) > THRESHOLD_OCCURRENCE and (quantidade / nos[destino].quantidade) > THRESHOLD_OCCURRENCE:
                        merge = True

                    # Maior ocorrencia em origem
                    elif (quantidade / nos[rotulos].quantidade) > THRESHOLD_OCCURRENCE and (quantidade / nos[destino].quantidade) < THRESHOLD_OCCURRENCE:
                        more_occurrence = rotulos
                    # Maior ocorrencia em destino
                    elif (quantidade / nos[rotulos].quantidade) < THRESHOLD_OCCURRENCE and (quantidade / nos[destino].quantidade) > THRESHOLD_OCCURRENCE:
                        more_occurrence = destino

                pg_schema_dict["relationships"].append({
                    "origin": chave_ordenada_origem,
                    "relationship_type": tipo_relacionamento,
                    "quant": quantidade,
                    "destination": chave_ordenada_destino,
                    "cardinality": no.cardinalidades.get(tipo_relacionamento, ""),
                    "properties": propriedades,
                    "primary_key": chaves,
                    "merge": merge,
                    "more_occurrence": more_occurrence
                })

                # print(pg_schema_dict["relationships"])

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
            lista_max_min = f" {prop_info['typeList']} {prop_info['minList'], prop_info['maxList']}"
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

        schema = schema.rstrip(",\n")  # Remove a última vírgula
        schema += "}),\n\n"

    # Adicionar relacionamentos
    for rel in pg_schema_dict['relationships']:
        destino_str = ' & '.join(rel['destination'])
        origem_str = ' | '.join(rel['origin'])
        prop_rel = rel['properties']

        # Cria uma lista para armazenar as propriedades com tipo e contagem
        propriedades_str = []

        for nome, dados in prop_rel.items():
            # Verifica se é ENUM
            # print(nome, dados)
            if dados.get("is_enum", False):
                valores_enum = ', '.join(map(str, dados["valores_enum"]))
                propriedades_str.append(f"{nome}: ENUM ({valores_enum})")
            
            elif dados["is_list"]:
                tipo_item = dados["list_info"]["tipo_item"]
                tamanho_min = dados["list_info"]["tamanho_min"]
                tamanho_max = dados["list_info"]["tamanho_max"]
                propriedades_str.append(f"{nome}: ARRAY {tipo_item} ({tamanho_min}, {tamanho_max})")

            else:
                tipos_str = ', '.join([f"{tipo} ({count})" for tipo, count in dados["tipos"].items()])
                propriedades_str.append(f"{nome}: {tipos_str}")

        # Junta as propriedades formatadas em uma string
        propriedades_formatadas = ', '.join(propriedades_str)

        # Cria o esquema do relacionamento no formato PG-Schema
        if len(prop_rel) == 0:
            schema += f"(:{origem_str})-[{rel['relationship_type']}Type {rel['cardinality']}]->(:{destino_str}Type),\n"
        else:
            schema += f"(:{origem_str})-[{rel['relationship_type']}Type {{{propriedades_formatadas}}} {rel['cardinality']}]->(:{destino_str}Type),\n"

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
            # print(pg_schema_dict['nodes'])
            node_str = ':'.join(node)
            node_ = f"{node_str}Type"

            listaProp = []
            listaProp.extend(info["uniqueProperties"])  # Adiciona as propriedades à lista
            propriedades_concatenadas = ', '.join(listaProp)  # Concatena todas as propriedades em uma única string
            # print(info['uniqueProperties'])
            if len(info['uniqueProperties']) > 1 and len(info['uniqueProperties']) <= 2:
                schema += f"FOR (x:{node_}) SINGLETON x.({propriedades_concatenadas}),\n"
            if len(info['uniqueProperties']) == 1:
                schema += f"FOR (x:{node_}) SINGLETON x.{propriedades_concatenadas},\n"

    schema = schema.rstrip(",\n")  # Remover a última vírgula e quebra de linha
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

# Dicionário nos, excluido.
nos.clear()

file_path = "GraphRel/nos_dump.pkl"

# Salvar o dicionário 'nos' usando pickle
salvar_nos_pickle(pg_schema_dict, file_path)
