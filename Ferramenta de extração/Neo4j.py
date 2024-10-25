from ClassNo import No

MAX_ENUMERATE = 20
THRESHOLD = 0.9

def percorrer_nos_e_armazenar_info(tx, nos):
    result = tx.run(
        "MATCH (p)"
        "RETURN labels(p) AS nodeType, properties(p) AS props"
    )
    i = 0
    for record in result:
        i += 1
        rotulos = tuple(record["nodeType"])
        # print(f"Nodos: {rotulos} {i}")
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
                    # print(f"{rotulo} JA TEM")
                    break
                else:
                    supertipo, subtipos = consultar_e_identificar_supertipo_subtipo(tx, rotulos)
                    # print("SUPER:", supertipo)
                    # print("SUB:", subtipos)
                    if supertipo and subtipos:
                        nos[rotulos].adicionar_supertipo(supertipo)
                        for subtipo in subtipos:
                            # print("SUB:", subtipo)
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
    if valor:
        quantidade_elem = valor.count(valor[0])
    else:
        quantidade_elem = 0
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
    i = 0
    for record in result:
        i += 1
        rotulo_origem = tuple(record["origem"])
        tipo_relacionamento = record["relType"]
        rotulo_destino = tuple(record["destLabel"])
        quantidade_origem = record["count"]

        origem = ':'.join(rotulo_origem)
        destino = ':'.join(rotulo_destino)

        # print(f"Rel: {origem} {i}")

        if rotulo_origem not in nos:
            nos[rotulo_origem] = No(rotulo_origem)
        nos[rotulo_origem].adicionar_relacionamento(tipo_relacionamento, rotulo_destino, quantidade_origem)

        # #CARDINALIDADE
        result_cardinalidade_origem = tx.run( #Retorna as propriedades (origem) que estão associadas a tantos nodos (destino)
            f"match(p:{origem})-[:{tipo_relacionamento}]->(m:{destino}) "
            f"WITH p, count(m) AS quantidadeOrigem "
            f"WHERE quantidadeOrigem > 1 "
            f"return properties(p), quantidadeOrigem LIMIT 1 "
        )

        cardinalidadeOrigem = 0
        for record_card_origem in result_cardinalidade_origem:
            if record_card_origem["quantidadeOrigem"] > 1:
                cardinalidadeOrigem = "N"
                # print(cardinalidadeOrigem)
                break
            else:
                cardinalidadeOrigem = 1
                # print(cardinalidadeOrigem)

        result_cardinalidade_destino = tx.run( #Retorna as propriedades (destino) que estão associadas a tantos nodos (origem)
            f"match(p:{origem})-[:{tipo_relacionamento}]->(m:{destino}) "
            f"WITH m, count(p) AS quantidadeDestino "
            f"WHERE quantidadeDestino > 1 "
            "return properties(m), quantidadeDestino LIMIT 1 "
        )

        cardinalidadeDestino = 0
        for record_card_destino in result_cardinalidade_destino:
            if record_card_destino["quantidadeDestino"] > 1:
                cardinalidadeDestino = "N"
                # print(cardinalidadeDestino)
                break
            else:
                cardinalidadeDestino = 1
                # print(cardinalidadeDestino)

        ThresholdOP = 0.9
        #OPCIONALIDADE
        result_op_destino = tx.run(
            f"MATCH (q:{destino}) "
            f"where not ()-[:{tipo_relacionamento}]->(q) "
            "return count(q) as countOpDestino "
        )
        for record_op_destino in result_op_destino:
            countOP_d = record_op_destino["countOpDestino"]
            verificarOPD = countOP_d / quantidade_origem
            if verificarOPD >= ThresholdOP:
                countOP_destino = 1
            else:
                countOP_destino = 0

        result_op_origem = tx.run(
            f"MATCH (p:{origem}) "
            f"where not (p)-[:{tipo_relacionamento}]->() "
            "return count(p) as countOpOrigem "
        )
        for record_op_origem in result_op_origem:
            countOP_o = record_op_origem["countOpOrigem"]
            verificarOPO = countOP_o / quantidade_origem
            if verificarOPO >= ThresholdOP:
                countOP_origem = 1
            else:
                countOP_origem = 0


        cardinalidade = f"({1 if countOP_destino == 0 else 0}:{"N" if cardinalidadeDestino == "N" else 1});({1 if countOP_origem == 0 else 0}:{"N" if cardinalidadeOrigem == "N" else 1})"
        nos[rotulo_origem].atualizar_cardinalidade(tipo_relacionamento, cardinalidade)
        # print(countOP_origem, countOP_destino, cardinalidadeOrigem, cardinalidadeDestino)
        # print(f"{origem}({countOP_origem}), {destino}({countOP_destino}), {origem}({cardinalidadeOrigem}), {destino}({cardinalidadeDestino}) = {tipo_relacionamento}")

        # cardinalidade = f"({1 if countOP_destino == 0 else 0}:?);({1 if countOP_origem == 0 else 0}:?)"
        # nos[rotulo_origem].atualizar_cardinalidade(tipo_relacionamento, cardinalidade)

        # cardinalidade = f"(?:?);(?:?)"
        # nos[rotulo_origem].atualizar_cardinalidade(tipo_relacionamento, cardinalidade)
        # print(countOP_origem, countOP_destino, "?", "?")

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
    for rotulo in rotulos:
        if rotulo != supertipo:
            subtipos.append(rotulo) 

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
    
    constraints_found = False  # Verifica se o comando SHOW CONSTRAINT retorna algo

    for record in result:
        constraints_found = True  # Se o loop entrar, significa que encontrou constraints
        name = record["name"]
        type = record["type"]
        entityType = record["entityType"]
        labelsOrTypes = record["labelsOrTypes"]
        properties = record["properties"]
        ownedIndex = record["ownedIndex"]
        propertyType = record["propertyType"]

        if entityType == "NODE":
            labelsOrTypes_key = tuple(labelsOrTypes)

            # Iterar sobre cada rótulo individualmente
            for rotulo in labelsOrTypes_key:
                rotulo_key = (rotulo,)  # Convertendo para uma tupla de um único elemento
                if rotulo_key in nos:  # Use rotulo_key em vez de labelsOrTypes_key
                    propriedades_do_rotulo = nos[rotulo_key].propriedades

                    if len(properties) > 1:
                        # Se a lista de propriedades tiver mais de um elemento, marque-as como listas e adicione-as à listaProp corretamente
                        for prop in properties:
                            if prop in propriedades_do_rotulo:
                                propriedades_do_rotulo[prop]['constraint'] = True
                                propriedades_do_rotulo[prop]["constraintList"].append(type)
                                propriedades_do_rotulo[prop]['listConstProp'] = True
                                propriedades_do_rotulo[prop]['unicidadeNeo4j'] = True
                                propriedades_do_rotulo[prop]['listProp'].append(prop)  # Adiciona cada propriedade individualmente à listProp
                    else:
                        # Se houver apenas uma propriedade, adicione-a à listProp corretamente
                        properties_tupla = properties[0]
                        if properties_tupla in propriedades_do_rotulo:
                            propriedade = propriedades_do_rotulo[properties_tupla]
                            propriedade["constraint"] = True 
                            propriedade["constraintList"].append(type)
                            propriedade["listProp"].append(properties_tupla)  # Adiciona a propriedade individualmente à listProp

    # Se nenhuma constraint foi encontrada
    if constraints_found == False:
        for rotulo, no in nos.items():
            for prop, info_propriedade in no.propriedades.items():
                if (len(info_propriedade["PropValues"]) == info_propriedade["total"]) and (len(info_propriedade["PropValues"]) / info_propriedade["total"] >= THRESHOLD):
                    propriedade_unica = True  # assumimos que a propriedade é única

                    # Se a propriedade for única, marcar como constraint
                    if propriedade_unica:
                        info_propriedade["constraint"] = True
                        info_propriedade["constraintList"].append("UNIQUENESS")
                        nos[rotulo].listaChaveUnica.append(prop)

def definir_enum(quantidadeNosTotal, info_propriedade, no):
    threshold = (quantidadeNosTotal * 0.1) / 100 
    verificar = (info_propriedade["total"] / no.quantidade)

    if ((verificar < threshold) or len(info_propriedade["values"]) <= 1):
        # print("        Agora Enum é False")
        info_propriedade["is_enum"] = False
        info_propriedade["values"].clear()
    else:
        return