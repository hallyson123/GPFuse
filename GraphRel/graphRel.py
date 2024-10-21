import re

# Função para ler o arquivo de entrada contendo o PG-Schema Like
def ler_pg_schema(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Função para parsear o esquema do PG-Schema Like
def analisar_pg_schema(pg_schema):
    nodos = {}
    relacionamentos = []
    constraints = []

    # capturar os nodos e suas propriedades
    nodo_pattern = re.compile(r"\((\w+Type) : (\w+) \{([^\}]*)\}\)")
    rel_pattern = re.compile(r"\(:([^\)]+)\)-\[([^\]]+)\]->\(:([^\)]+)\)")
    mandatory_pattern = re.compile(r"FOR \(x:(\w+Type)\) MANDATORY x.(\w+)")
    singleton_pattern = re.compile(r"FOR \(x:(\w+Type)\) SINGLETON x.(\w+)")

    # Parse nodos
    for match in nodo_pattern.finditer(pg_schema):
        node_type, node_name, properties = match.groups()
        props = [prop.strip() for prop in properties.split(',')]
        nodos[node_name] = {'type': node_type, 'properties': props}

    # Parse relacionamentos
    for match in rel_pattern.finditer(pg_schema):
        origem, rel_type, destino = match.groups()
        relacionamentos.append({'origem': origem, 'relacionamento': rel_type, 'destino': destino})

    # Parse constraints MANDATORY e SINGLETON
    for match in mandatory_pattern.finditer(pg_schema):
        node_type, prop = match.groups()
        constraints.append({'type': 'MANDATORY', 'node': node_type, 'property': prop})

    for match in singleton_pattern.finditer(pg_schema):
        node_type, prop = match.groups()
        constraints.append({'type': 'SINGLETON', 'node': node_type, 'property': prop})

    return nodos, relacionamentos, constraints

# Função para criar as regras de conversão a partir do PG-Schema
def criar_regras_de_conversao(nodos, relacionamentos, constraints):
    regras = []
    
    # Regras de conversão para nodos (tabelas)
    for node_name, node_info in nodos.items():
        regra_nodo = f"Convertendo o nodo '{node_name}' para a tabela '{node_name.lower()}' com as propriedades {node_info['properties']}"
        regras.append(regra_nodo)

    # Regras para relacionamentos (chaves estrangeiras)
    for rel in relacionamentos:
        regra_rel = f"Converter o relacionamento '{rel['relacionamento']}' entre '{rel['origem']}' e '{rel['destino']}' para chave estrangeira em '{rel['origem'].lower()}'"
        regras.append(regra_rel)

    # Regras para constraints MANDATORY e SINGLETON
    for constraint in constraints:
        if constraint['type'] == 'MANDATORY':
            regra_mandatory = f"A propriedade '{constraint['property']}' em '{constraint['node'].lower()}' deve ser NOT NULL"
            regras.append(regra_mandatory)
        elif constraint['type'] == 'SINGLETON':
            regra_singleton = f"A propriedade '{constraint['property']}' em '{constraint['node'].lower()}' deve ser UNIQUE"
            regras.append(regra_singleton)

    return regras

# Função para converter nodos e relacionamentos para tabelas e chaves
def converter_para_relacional(nodos, relacionamentos, constraints):
    tabelas = {}
    foreign_keys = []

    # Converter nodos para tabelas
    for node_name, node_info in nodos.items():
        tabela_nome = node_name.lower()  # Nome da tabela
        tabelas[tabela_nome] = []
        
        for prop in node_info['properties']:
            tabelas[tabela_nome].append(prop)

    # Adicionar constraints de MANDATORY e SINGLETON
    for constraint in constraints:
        tabela_nome = constraint['node'].lower().replace("type", "")
        if constraint['type'] == "MANDATORY":
            for coluna in tabelas[tabela_nome]:
                if coluna == constraint['property']:
                    tabelas[tabela_nome].append(f"{coluna} NOT NULL")
        if constraint['type'] == "SINGLETON":
            tabelas[tabela_nome].append(f"UNIQUE ({constraint['property']})")

    # Converter relacionamentos para tabelas ou chaves estrangeiras
    for rel in relacionamentos:
        origem = rel['origem'].lower()
        destino = rel['destino'].lower()
        foreign_keys.append(f"ALTER TABLE {origem} ADD FOREIGN KEY ({destino}_id) REFERENCES {destino}(id);")

    return tabelas, foreign_keys

# Função para salvar as regras de conversão em um arquivo
def salvar_regras(regras, file_path='GraphRel/regras_conversão.txt'):
    with open(file_path, 'w') as f:
        for regra in regras:
            f.write(f"{regra}\n")
    print(f"Regras de conversão salvas em {file_path}")

# Função principal da ferramenta
def graphRel(file_path):
    # 1. Ler o arquivo PG-Schema Like
    pg_schema = ler_pg_schema(file_path)

    # 2. Parsear o esquema
    nodos, relacionamentos, constraints = analisar_pg_schema(pg_schema)

    # 3. Criar regras de conversão
    regras = criar_regras_de_conversao(nodos, relacionamentos, constraints)
    
    # 4. Salvar as regras em um arquivo
    salvar_regras(regras)

    # 5. Converter para modelo relacional
    tabelas, foreign_keys = converter_para_relacional(nodos, relacionamentos, constraints)

    # 6. Gerar o script SQL
    script_sql = ""
    for tabela, colunas in tabelas.items():
        script_sql += f"CREATE TABLE {tabela} (\n"
        script_sql += "  id INT PRIMARY KEY,\n"
        script_sql += "  " + ",\n  ".join(colunas) + "\n"
        script_sql += ");\n\n"
    
    for fk in foreign_keys:
        script_sql += fk + "\n"

    # 7. Salvar o script SQL em um arquivo
    with open('GraphRel/graph_to_rel.sql', 'w') as f:
        f.write(script_sql)

    print("Migração concluída. Script SQL gerado: graph_to_rel.sql")

file_path = "GraphRel/pg_schema.txt"  # Arquivo contendo o PG-Schema Like
graphRel(file_path)
