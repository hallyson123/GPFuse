import random

def criar_nodos(tx, rotulo, propriedade, atributo, quantidade, subtipo=None, enumerate_valor_max=None):
    for _ in range(quantidade):
        valor = f"{atributo}_{random.randint(1, 1000)}"  # Adiciona um valor aleatório para evitar duplicatas
        lista_valores = [random.randint(1, 1000) for _ in range(random.randint(1, 10))]  # Lista de valores aleatórios
        # Verificar se o nó já existe
        result = tx.run(f"MATCH (n:{rotulo}) WHERE n.{propriedade} = $atributo RETURN n", atributo=valor)
        
        if result.peek() is None:
            # Se o nó não existir
            if subtipo:
                propriedade_sem_compartilhamento = f"sem_shared_{random.randint(1, 1000)}"
                tx.run(f"CREATE (:{rotulo}:{subtipo} {{{propriedade}: $atributo, lista_propriedade: $lista, sem_compartilhamento: $prop_sem_compart}})"
                       , atributo=valor, lista=lista_valores, prop_sem_compart=propriedade_sem_compartilhamento)
            else:
                # Verificar se a propriedade deve ser enumerada
                if enumerate_valor_max is not None:
                    result_enum = tx.run(f"MATCH (n:{rotulo}) WHERE n.nome = $enumerate_propriedade RETURN n", enumerate_propriedade=atributo)
                    if result_enum.peek() is None:
                        tx.run(f"CREATE (:{rotulo} {{nome: $enumerate_propriedade}})", enumerate_propriedade=atributo)
                        enumerate_valor_max = enumerate_valor_max - 1
                    else:
                        print(f"Nodo com [{propriedade}: '{atributo}]' já existe.")
                else:
                    tx.run(f"CREATE (:{rotulo} {{{propriedade}: $atributo, lista_propriedade: $lista}})",
                           atributo=valor, lista=lista_valores)
        else:
            print(f"Nodo com [{propriedade}: '{valor}]' já existe.")
