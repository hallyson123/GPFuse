from ConexãoBanco import nos

# Exibindo os resultados
print("-----------------------")
for rotulos, no in nos.items():
    rotulos_str = ', '.join(rotulos)
    print(f"Rótulo: {rotulos_str}")
    print(f"Quantidade: {no.quantidade}")

    # Propriedades
    for propriedade, info_propriedade in no.propriedades.items():
        print(f"    {propriedade}:")
        for tipo, quantidade in info_propriedade["tipos"].items():
            print(f"        {tipo}, Quantidade: {quantidade}")
        print(f"        Is Enum: {info_propriedade['is_enum']}")
        
        if info_propriedade['is_enum'] == True:
            print(f"        Values: {info_propriedade['values']}")
        print(f"        Total: {info_propriedade['total']}")

    # Relacionamentos
    print("-------")
    if no.relacionamentos:
        print("Relacionamentos -> Destinos:")
        for rel_type, rel_info in no.relacionamentos.items():
            destinos_str = ', '.join([', '.join(rotulo) for rotulo in rel_info['rotulos_destino']])
            print(f"    [{rel_type}] -> {destinos_str} (Quantidade: {rel_info['quantidade']})")
    else:
        print("Relacionamentos -> Destinos:")
        print("     Não há relacionamentos.")
    print("-------")
    print("-----------------------")
