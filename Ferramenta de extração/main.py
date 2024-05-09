from ConexãoBanco import nos
from Neo4j import marcar_propriedades_compartilhadas, definir_enum

print("-----------------------")
# Chamar a função para marcar propriedades compartilhadas
marcar_propriedades_compartilhadas(nos)
print("-----------------------")

# Exibindo os resultados
def gerar_saida_pg_schema(nos):
    schema = "CREATE GRAPH TYPE TesteGraphType STRICT {\n"

    #percorre sobre os nós e suas propriedades
    for rotulos, no in nos.items():
        rotulos_str = ' & '.join(rotulos)
        schema += f"({rotulos_str}Type : {rotulos_str} {{\n"

        #Sobre as propriedades do nó
        for propriedade, info_propriedade in no.propriedades.items():
            tipo_propriedade = max(info_propriedade["tipos"], key=info_propriedade["tipos"].get) #tipo da propriedade com a maior ocorrência

            # Verificar se a propriedade é uma enumeração
            quantidadeNosTotal = no.quantidade
            definir_enum(quantidadeNosTotal, info_propriedade, no)

            #Verificar se a propriedade é opcional
            # total_nodo = no.quantidade
            # total_propriedade = info_propriedade["total"]
            if no.quantidade != info_propriedade["total"]:
                # print(total_nodo, total_propriedade)
                opcional = True
            else:
                # print(total_nodo, total_propriedade)
                opcional = False
            
            if info_propriedade.get("is_enum"):
                valores_enum = ', '.join(f'"{val}"' for val in info_propriedade.get("values"))
                
                if opcional:
                    schema += f"    OPTIONAL {propriedade} ENUM ({valores_enum}),\n"
                else:
                    schema += f"    {propriedade} ENUM ({valores_enum}),\n"

            else:
                # Ajustar o tipo LIST conforme o PG-SCHEMA
                if info_propriedade["is_list"]:
                    tipo_propriedade = "array"
                    tipo_maior_freq = max(info_propriedade["tipos_listas"], key=info_propriedade["tipos_listas"].get) # Pega o tipo mais frequente armazanado na lista
                    # tam_max_lista = max(info_propriedade["tamQuantLista"], key=info_propriedade["tamQuantLista"].get)
                    # tam_min_lista = min(info_propriedade["tamQuantLista"], key=info_propriedade["tamQuantLista"].get)
                    
                    # Inicializar o tamanho mínimo e máximo
                    tam_min_lista = float('inf')
                    tam_max_lista = float('-inf')
                    
                    # Percorrer os itens do dicionário tamQuantLista para encontrar o tamanho mínimo e máximo
                    for tamanho in info_propriedade["tamQuantLista"]:
                        if tamanho < tam_min_lista:
                            tam_min_lista = tamanho
                        if tamanho > tam_max_lista:
                            tam_max_lista = tamanho

                    if opcional:
                        schema += f"    OPTIONAL {propriedade} {tipo_propriedade.upper()} {tipo_maior_freq} ({tam_min_lista}, {tam_max_lista}),\n"
                    else:
                        schema += f"    {propriedade} {tipo_propriedade.upper()} {tipo_maior_freq} ({tam_min_lista}, {tam_max_lista}),\n"
                else:
                    if opcional:
                        schema += f"    OPTIONAL {propriedade} {tipo_propriedade.upper()},\n"
                    else:
                        schema += f"    {propriedade} {tipo_propriedade.upper()},\n"

        schema = schema.rstrip(",\n")  #Remover a última vírgula e quebra de linha
        schema += "}),\n\n"

    # Iterar sobre os relacionamentos
    relacionamentos = set()  # Conjunto para armazenar os tipos de relacionamento já adicionados
    for rotulos, no in nos.items():
        for tipo_relacionamento, relacoes in no.relacionamentos.items():
            for destino, quantidade_rel in relacoes:
                destinos_str = ' & '.join(destino)
                cardinalidade = no.cardinalidades.get(tipo_relacionamento, "")  # Verificar se há cardinalidade
                tipos_origem = ' | '.join(rotulos) if len(rotulos) > 1 else rotulos[0]

                # Verificar se o tipo de relacionamento já foi adicionado anteriormente
                if (tipos_origem, tipo_relacionamento, destinos_str) not in relacionamentos:
                    # Adicionar relacionamento apenas se não tiver sido adicionado antes
                    schema += f"(:{tipos_origem})-[{tipo_relacionamento}Type {cardinalidade}]->(:{destinos_str}Type),\n"
                    relacionamentos.add((tipos_origem, tipo_relacionamento, destinos_str))

    schema = schema.rstrip(",\n")  # Remover a última vírgula e quebra de linha
    schema += "\n}"

    return schema

#gerar a saída PG-SCHEMA
saida_pg_schema = gerar_saida_pg_schema(nos)
print(saida_pg_schema)