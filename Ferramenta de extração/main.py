from ConexãoBanco import nos
from Neo4j import marcar_propriedades_compartilhadas

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
            tipo_propriedade = next(iter(info_propriedade["tipos"]))  # Obter o primeiro tipo encontrado

            # Verificar se a propriedade é uma enumeração
            if info_propriedade.get("is_enum"):
                valores_enum = ', '.join(f'"{val}"' for val in info_propriedade.get("values"))
                schema += f"    {propriedade} ENUM ({valores_enum}),\n"
            else:
                schema += f"    {propriedade} {tipo_propriedade.upper()},\n"

        schema = schema.rstrip(",\n")  #Remover a última vírgula e quebra de linha
        schema += "}),\n"

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