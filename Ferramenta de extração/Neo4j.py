from ClassNo import No

MAX_ENUMERATE = 5

def percorrer_nos_e_armazenar_info(tx, nos):
    result = tx.run(
        "MATCH (p)"
        "RETURN labels(p) AS nodeType, properties(p) AS props"
    )
    for record in result:
        rotulos = tuple(record["nodeType"])
        if rotulos not in nos:
            nos[rotulos] = No(rotulos)
        nos[rotulos].quantidade += 1  # incrementar a quantidade

        # Adicionando propriedades ao nó
        propriedades = record["props"]
        for nome, valor in propriedades.items():
            tipo = "UNKNOWN"
            if valor is not None:
                tipo = type(valor).__name__
            nos[rotulos].adicionar_propriedade(nome, tipo, valor)

            if isinstance(valor, list):
                percorrerNosLista(tx, nos, rotulos, nome, valor)

        # Identificar supertipos e subtipos se o nó tiver 2 ou 3 rótulos
        if len(rotulos) == 2 or len(rotulos) == 3:
            for rotulo in rotulos:
                if rotulo in nos[rotulos].supertipos or rotulo in nos[rotulos].subtipos:
                    break
                else:
                    supertipo, subtipos = consultar_e_identificar_supertipo_subtipo(tx, rotulos)

                    if supertipo and subtipos:
                        nos[rotulos].adicionar_supertipo(supertipo)
                        for subtipo in subtipos:
                            nos[rotulos].adicionar_subtipo(subtipo)

def percorrerNosLista(tx, nos, rotulos, nome, valor):
    nos[rotulos].propriedades[nome]["is_enum"] = False
    nos[rotulos].propriedades[nome].setdefault("moda_lista", [])  # Inicializar a lista se ainda não existir
    nos[rotulos].propriedades[nome]["total"] += 1

    tamanho = len(valor)
    nos[rotulos].propriedades[nome]["tamQuantLista"].setdefault(tamanho, 0)
    nos[rotulos].propriedades[nome]["tamQuantLista"][tamanho] += 1

    moda_lista = nos[rotulos].propriedades[nome]["moda_lista"]
    moda_lista.append(tamanho)

    # Inicializa a estrutura tipos_listas como um dicionário
    tipos_lista = nos[rotulos].propriedades[nome]["tipos_listas"]

    # Atualiza os tipos armazenados nas listas
    tipos_elementos = set(type(elem).__name__ for elem in valor)
    tipo_elem = ', '.join(sorted(tipos_elementos))  # Tipos como string
    quantidade_elem = valor.count(valor[0])
    multiplicacao = tamanho * quantidade_elem
    tipos_lista[tipo_elem] = tipos_lista.get(tipo_elem, 0) + multiplicacao

    valores_unicos = set(nos[rotulos].propriedades[nome].get("values", []))
    valores_unicos.update(valor)

    # Verificar se a propriedade deve ser enumerada
    if not nos[rotulos].propriedades[nome]["is_enum"]:
        if len(valores_unicos) <= MAX_ENUMERATE:
            valores_limitados = []
            #limitar os valores tipo String em 20 caracteres
            for val in valores_unicos:
                if isinstance(val, str):
                    valores_limitados.append(val[:20])
                else:
                    valores_limitados.append(val)
                    
            nos[rotulos].propriedades[nome]["values"] = list(valores_limitados)
            nos[rotulos].propriedades[nome]["is_enum"] = True
    elif "values" in nos[rotulos].propriedades[nome]:
        del nos[rotulos].propriedades[nome]["values"]
        nos[rotulos].propriedades[nome]["is_enum"] = False

    # Contagem do tipo "list"
    if isinstance(valor, list):
        if "list" in nos[rotulos].propriedades[nome]["tipos"]:
            nos[rotulos].propriedades[nome]["tipos"]["list"] += 1
        else:
            nos[rotulos].propriedades[nome]["tipos"]["list"] = 1

def coletar_relacionamentos(tx, nos):
    #ROTULOS E INFORMAÇÕES
    result = tx.run(
        "MATCH (p)-[r]->(q)"
        "RETURN labels(p) AS origem, type(r) AS relType, labels(q) AS destLabel, count(r) AS count"
    )

    for record in result:
        rotulo_origem = tuple(record["origem"])
        tipo_relacionamento = record["relType"]
        rotulo_destino = tuple(record["destLabel"])
        quantidade_origem = record["count"]

        origem = ':'.join(rotulo_origem)
        destino = ':'.join(rotulo_destino)

        if rotulo_origem not in nos:
            nos[rotulo_origem] = No(rotulo_origem)
        nos[rotulo_origem].adicionar_relacionamento(tipo_relacionamento, rotulo_destino, quantidade_origem)

        #CARDINALIDADE
        result_cardinalidade_origem = tx.run( #Retorna as propriedades (origem) que estão associadas a tantos nodos (destino)
            f"match(p:{origem})-[:{tipo_relacionamento}]->(m:{destino}) "
            f"return properties(p), count(m) as quantidadeOrigem "
        )

        cardinalidadeOrigem = 0
        for record_card_origem in result_cardinalidade_origem:
            if record_card_origem["quantidadeOrigem"] > 1:
                cardinalidadeOrigem = "N"
                print(cardinalidadeOrigem)
                break
            else:
                cardinalidadeOrigem = 1
                print(cardinalidadeOrigem)

        result_cardinalidade_destino = tx.run( #Retorna as propriedades (destino) que estão associadas a tantos nodos (origem)
            f"match(p:{origem})-[:{tipo_relacionamento}]->(m:{destino}) "
            "return properties(m), count(p) as quantidadeDestino "
        )

        cardinalidadeDestino = 0
        for record_card_destino in result_cardinalidade_destino:
            if record_card_destino["quantidadeDestino"] > 1:
                cardinalidadeDestino = "N"
                print(cardinalidadeDestino)
                break
            else:
                cardinalidadeDestino = 1
                print(cardinalidadeDestino)

        #OPCIONALIDADE
        result_op_destino = tx.run(
            f"MATCH (q:{destino}) "
            f"where not ()-[:{tipo_relacionamento}]->(q) "
            "return count(q) as countOpDestino "
        )
        for record_op_destino in result_op_destino:
            countOP_destino = record_op_destino["countOpDestino"]

        result_op_origem = tx.run(
            f"MATCH (p:{origem}) "
            f"where not (p)-[:{tipo_relacionamento}]->() "
            "return count(p) as countOpOrigem "
        )
        for record_op_origem in result_op_origem:
            countOP_origem = record_op_origem["countOpOrigem"]

        cardinalidade = f"({1 if countOP_destino == 0 else 0}:{"N" if cardinalidadeDestino == "N" else 1});({1 if countOP_origem == 0 else 0}:{"N" if cardinalidadeOrigem == "N" else 1})"
        nos[rotulo_origem].atualizar_cardinalidade(tipo_relacionamento, cardinalidade)
        print(countOP_origem, countOP_destino, cardinalidadeOrigem, cardinalidadeDestino)

def consultar_e_identificar_supertipo_subtipo(tx, rotulos):
    supertipo = None
    subtipos = []

    maior_quantidade = 0 #armazenar a maior quantidade de ocorrências

    for rotulo in rotulos: # Loop para comparar a quantidade de ocorrências de cada rótulo
        result = tx.run(
            f"MATCH(p:{rotulo}) "
            f"RETURN count(p) AS count, '{rotulo}' AS nome "
        )

        for record in result:
            nome = record["nome"]
            # print(nome)
            quantidade = record["count"]

            # Atualiza o supertipo se a quantidade atual for maior que a quantidade máxima encontrada
            if quantidade > maior_quantidade:
                supertipo = nome
                maior_quantidade = quantidade

    #subtipo como o rótulo restante
    # print(rotulos)
    for rotulo in rotulos:
        if rotulo != supertipo:
            subtipos.append(rotulo)
            # print(f"{rotulo} é o supertipo")    

    return supertipo, subtipos

def marcar_propriedades_compartilhadas(nos):
    for rotulos, no in nos.items():
        if no.supertipos and no.subtipos:
            for propriedade, info_propriedade in no.propriedades.items():
                if not info_propriedade["is_shared"]:
                    for supertipo in no.supertipos:
                        supertipo_key = (supertipo,)
                        if supertipo_key in nos:
                            if propriedade in nos[supertipo_key].propriedades:
                                no.propriedades[propriedade]["is_shared"] = True
                                nos[supertipo_key].propriedades[propriedade]["is_shared"] = True

                    for subtipo in no.subtipos:
                        subtipo_key = (subtipo,)
                        if subtipo_key in nos:
                            if propriedade in nos[subtipo_key].propriedades:
                                no.propriedades[propriedade]["is_shared"] = True
                                nos[subtipo_key].propriedades[propriedade]["is_shared"] = True

def retornar_constraint(tx, nos):
    result = tx.run("SHOW CONSTRAINT")

    for record in result:
        name = record["name"]
        type = record["type"]
        entityType = record["entityType"]
        labelsOrTypes = record["labelsOrTypes"]
        properties = record["properties"]
        ownedIndex = record["ownedIndex"]
        propertyType = record["propertyType"]

        # print(name, type, entityType, labelsOrTypes, properties, ownedIndex, propertyType)

        if entityType == "NODE":
            labelsOrTypes_key = tuple(labelsOrTypes)
            if labelsOrTypes_key in nos:
                propriedades_do_rotulo = nos[labelsOrTypes_key].propriedades
                # Convertendo a lista properties em uma tupla
                properties_tupla = '[]'.join(properties)
                if properties_tupla in propriedades_do_rotulo:
                    propriedade = propriedades_do_rotulo[properties_tupla]
                    propriedade["constraint"] = True 
                    print(propriedade["constraint"])
        else:
            print()