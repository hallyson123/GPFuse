## Ferramenta de Extração e Gerador de Banco de Dados Orientado a Grafos ##

<p>Este projeto consiste em uma ferramenta desenvolvida em Python para a extração de esquemas e geração de bancos de dados orientado a grafos. Utiliza-se a biblioteca Neo4j para o desenvolvimento do projeto.</p>

### Funcionalidades ###
- Essas funcionalidades combinadas permitem tanto a análise de estrutura de um banco de dados de grafos existente quanto a criação de um novo banco de dados populado com dados fictícios para fins de teste e desenvolvimento.

## Requisitos

- **Python**: A ferramenta foi desenvolvida utilizando a linguagem de programação Python.
- **Neo4j**: A ferramenta utiliza a biblioteca Neo4j para interagir com o bancos de dados orientado a grafos. Certifique-se de ter o Neo4j instalado e configurado corretamente.
- **Bibliotecas Necessárias**:
  - `neo4j`
  - `pickle`

## Como usar

- Com o Neo4j já configurado e aberto no banco de dados que deseja, na GPFuse vá em `ConexãoBanco.py` e configure as variáveis `uri`, `username` e `password` para fazer a conexão.
- É possível configurar um valor para definir se uma propriedade é obrigatória e também configurar um valor máximo para uma propriedade ser enumerate. Para isso, vá em `main.py` e modifique `THRESHOLD`e `MAX_ENUMERATE`.
  - `THRESHOLD_OCCURRENCE` é usado para fusionar os nodos envolvidos em relacionamentos (1:1) na `GraphRel`.
- Modifique a pasta de saída do dicionário em `file_path` conforme necessário. 
  - Este dicionário será utilizado posteriormente como entrada na ferramenta `GraphRel` para a migração de dados.
- VS Code:
  - Abra um terminal e vá até a pasta `Ferramenta de extração`.
  - Execute o comando: `python.exe .\main.py`
  
## Resultados

- Esquema no formato `PG-Schema`.
- Utilizando a biblioteca `Pickle` um dicionário é gerado para auxiliar a migração de dados na ferramenta `GraphRel`.