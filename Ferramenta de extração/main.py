from ConexãoBanco import nos
from Neo4j import marcar_propriedades_compartilhadas

print("-----------------------")
# Chamar a função para marcar propriedades compartilhadas
marcar_propriedades_compartilhadas(nos)
print("-----------------------")

# Exibindo os resultados
print("-----------------------")
for rotulos, no in nos.items():
    rotulos_str = ', '.join(rotulos)
    print(f"Rótulo: {rotulos_str}")
    print(f"Quantidade: {no.quantidade}")
    
    if no.supertipos:
        for supertipo in no.supertipos:
            print("    Supertipo: ", supertipo)

    if no.subtipos:
        for subtipo in no.subtipos:
            print("    Subtipos:", subtipo)

    # Propriedades
    quantidadeNosTotal = no.quantidade
    for propriedade, info_propriedade in no.propriedades.items():
        print(f"    {propriedade}:")

        for tipo, quantidade in info_propriedade["tipos"].items():
            print(f"        {tipo}, Quantidade: {quantidade}")

        if info_propriedade['is_enum']:
            # threshold = quantidadeNosTotal * 0.1
            # verificar = (info_propriedade["total"] / no.quantidade)
            threshold = (quantidadeNosTotal * 0.1) / 100
            verificar = (info_propriedade["total"] / no.quantidade)

            if (verificar < threshold):
                print("        Agora Enum é False")
                info_propriedade["is_enum"] = False
                info_propriedade["values"].clear()
            else:
                print("        True")

        print(f"        Is Enum: {info_propriedade['is_enum']}")

        if info_propriedade['is_enum'] == True:
            print(f"            Values: {info_propriedade['values']}")

        print(f"        Is List: {info_propriedade['is_list']}")

        if info_propriedade["is_list"] and "moda_lista" in info_propriedade:
            # Tamanhos de listas
            print(f"            Tamanhos de Listas: {info_propriedade['tamQuantLista']}")

            # Moda da lista
            moda_lista = info_propriedade["moda_lista"]

            # Encontrar a moda (valores que mais aparecem)
            contagem_valores = {valor: moda_lista.count(valor) for valor in set(moda_lista)}
            max_contagem = max(contagem_valores.values(), default=0)
            modas = [valor for valor, contagem in contagem_valores.items() if contagem == max_contagem]
            print(f"            Moda da Lista: {modas}")

            # Tipos armazenados nas listas
            tipos_listas = info_propriedade["tipos_listas"]
            tipos_listas_str = ', '.join([f"{tipo} ({quantidade})" for tipo, quantidade in tipos_listas.items()])
            print(f"            {tipos_listas_str}")

        if "constraint" in info_propriedade:
            print(f"        Constraint: {info_propriedade['constraint']}")

        if "is_shared" in info_propriedade:
            print(f"        is_shared: {info_propriedade['is_shared']}")

        print(f"        Total: {info_propriedade['total']}")

    # Imprimir relacionamentos
    print("-------")
    print("Relacionamentos:")
    for tipo_relacionamento, relacoes in no.relacionamentos.items():
        for destino, quantidade_rel in relacoes:
            destinos_str = ', '.join(destino)
            if tipo_relacionamento in no.cardinalidades:
                cardinalidade = no.cardinalidades[tipo_relacionamento]
                print(f"    [:{tipo_relacionamento}] -> ({destinos_str}) (Quantidade: {quantidade_rel}, Cardinalidade: {cardinalidade})")
            else:
                print(f"    [:{tipo_relacionamento}] -> ({destinos_str}) (Quantidade: {quantidade_rel})")
    print("-------")
    print("-----------------------")
