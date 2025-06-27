import argparse
from neo4j import GraphDatabase
from faker import Faker
import random
import datetime

# Importar as funções dos outros arquivos
from criar_restricao import criar_restricao_se_nao_existe
from criar_nodos import criar_nodo
from criar_relacionamentos import (
    relacionar_pessoa_filme,
    relacionar_sponsor_filme,
    relacionar_streaming_filme
)

# --- CONFIGURAÇÃO ---
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "1F16EBD3"

# Inicializar o Faker para gerar dados falsos realistas
fake = Faker('pt_BR')

# Lista de Gêneros
GENEROS_PERMITIDOS = [
    'Ação', 'Aventura', 'Comédia', 'Drama', 'Ficção Científica', 
    'Fantasia', 'Terror', 'Suspense', 'Mistério', 'Romance', 
    'Documentário', 'Animação', 'Musical', 'Faroeste', 'Guerra', 
    'Policial', 'Biografia', 'Histórico', 'Esporte', 'Família'
]

# Lista de Tipos de Produtor
PRODUCER_TYPES = [
    'Executive Producer', 'Line Producer', 'Co-Producer', 'Associate Producer',
    'Supervising Producer', 'Consulting Producer', 'Segment Producer', 'Producer'
]

FILMES_PARA_CRIAR = [
    {"title": "O Poderoso Chefão", "release_year": 1972, "genre": "Drama", "winner_years_list": [1973]},
    {"title": "Pulp Fiction: Tempo de Violência", "release_year": 1994, "genre": "Policial", "winner_years_list": [1995]},
    {"title": "Matrix", "release_year": 1999, "genre": "Ficção Científica", "winner_years_list": [2000]},
    {"title": "Forrest Gump: O Contador de Histórias", "release_year": 1994, "genre": "Drama"},
    {"title": "Cidade de Deus", "release_year": 2002, "genre": "Drama"},
    {"title": "Parasita", "release_year": 2019, "genre": "Suspense", "winner_years_list": [2020]},
    {"title": "O Senhor dos Anéis: A Sociedade do Anel", "release_year": 2001, "genre": "Fantasia"},
    {"title": "A Origem", "release_year": 2010, "genre": "Ficção Científica"},
    {"title": "O Resgate do Soldado Ryan", "release_year": 1998, "genre": "Guerra"},
    {"title": "Procurando Nemo", "release_year": 2003, "genre": "Animação"}
]

PESSOAS_PARA_CRIAR = [
    # Atores e Atrizes
    {"id": "p_pacino", "name": "Al Pacino", "birth_date": "1940-04-25"},
    {"id": "p_brando", "name": "Marlon Brando", "birth_date": "1924-04-03"},
    {"id": "p_travolta", "name": "John Travolta", "birth_date": "1954-02-18"},
    {"id": "p_jackson", "name": "Samuel L. Jackson", "birth_date": "1948-12-21"},
    {"id": "p_thurman", "name": "Uma Thurman", "birth_date": "1970-04-29"},
    {"id": "p_reeves", "name": "Keanu Reeves", "birth_date": "1964-09-02"},
    {"id": "p_hanks", "name": "Tom Hanks", "birth_date": "1956-07-09"},
    {"id": "p_firmino", "name": "Leandro Firmino", "birth_date": "1978-06-23"},
    {"id": "p_haagensen", "name": "Phellipe Haagensen", "birth_date": "1984-07-02"},
    {"id": "p_dicaprio", "name": "Leonardo DiCaprio", "birth_date": "1974-11-11"},
    {"id": "p_wood", "name": "Elijah Wood", "birth_date": "1981-01-28"},
    {"id": "p_mckellen", "name": "Ian McKellen", "birth_date": "1939-05-25"},
    {"id": "p_degneres", "name": "Ellen DeGeneres", "birth_date": "1958-01-26"},
    
    # Diretores, Produtores, etc.
    {"id": "p_coppola", "name": "Francis Ford Coppola", "papeis": ["Director", "Producer"], "producer_type": "Executive Producer", "debut_film_year": 1963},
    {"id": "p_tarantino", "name": "Quentin Tarantino", "papeis": ["Director"], "debut_film_year": 1992},
    {"id": "p_wachowski_1", "name": "Lana Wachowski", "papeis": ["Director", "Producer"], "producer_type": "Producer"},
    {"id": "p_wachowski_2", "name": "Lilly Wachowski", "papeis": ["Director", "Producer"], "producer_type": "Producer"},
    {"id": "p_zemeckis", "name": "Robert Zemeckis", "papeis": ["Director"]},
    {"id": "p_meirelles", "name": "Fernando Meirelles", "papeis": ["Director"]},
    {"id": "p_bong", "name": "Bong Joon-ho", "papeis": ["Director"]},
    {"id": "p_jackson_peter", "name": "Peter Jackson", "papeis": ["Director", "Producer"]},
    {"id": "p_nolan", "name": "Christopher Nolan", "papeis": ["Director", "Producer"]},
    {"id": "p_spielberg", "name": "Steven Spielberg", "papeis": ["Director", "Producer"]},
    {"id": "p_stanton", "name": "Andrew Stanton", "papeis": ["Director"]},
    {"id": "p_ebert", "name": "Roger Ebert", "papeis": ["Reviewer"], "critic_profile_url": "https://www.rogerebert.com/"}
]

RELACIONAMENTOS_PARA_CRIAR = [
    {"pessoa_id": "p_pacino", "filme_titulo": "O Poderoso Chefão"},
    {"pessoa_id": "p_brando", "filme_titulo": "O Poderoso Chefão"},
    {"pessoa_id": "p_coppola", "filme_titulo": "O Poderoso Chefão"},
    {"pessoa_id": "p_travolta", "filme_titulo": "Pulp Fiction: Tempo de Violência"},
    {"pessoa_id": "p_jackson", "filme_titulo": "Pulp Fiction: Tempo de Violência"},
    {"pessoa_id": "p_thurman", "filme_titulo": "Pulp Fiction: Tempo de Violência"},
    {"pessoa_id": "p_tarantino", "filme_titulo": "Pulp Fiction: Tempo de Violência"},
    {"pessoa_id": "p_reeves", "filme_titulo": "Matrix"},
    {"pessoa_id": "p_wachowski_1", "filme_titulo": "Matrix"},
    {"pessoa_id": "p_wachowski_2", "filme_titulo": "Matrix"},
    {"pessoa_id": "p_hanks", "filme_titulo": "Forrest Gump: O Contador de Histórias"},
    {"pessoa_id": "p_hanks", "filme_titulo": "O Resgate do Soldado Ryan"},
    {"pessoa_id": "p_zemeckis", "filme_titulo": "Forrest Gump: O Contador de Histórias"},
    {"pessoa_id": "p_firmino", "filme_titulo": "Cidade de Deus"},
    {"pessoa_id": "p_haagensen", "filme_titulo": "Cidade de Deus"},
    {"pessoa_id": "p_meirelles", "filme_titulo": "Cidade de Deus"},
    {"pessoa_id": "p_bong", "filme_titulo": "Parasita"},
    {"pessoa_id": "p_wood", "filme_titulo": "O Senhor dos Anéis: A Sociedade do Anel"},
    {"pessoa_id": "p_mckellen", "filme_titulo": "O Senhor dos Anéis: A Sociedade do Anel"},
    {"pessoa_id": "p_jackson_peter", "filme_titulo": "O Senhor dos Anéis: A Sociedade do Anel"},
    {"pessoa_id": "p_dicaprio", "filme_titulo": "A Origem"},
    {"pessoa_id": "p_nolan", "filme_titulo": "A Origem"},
    {"pessoa_id": "p_spielberg", "filme_titulo": "O Resgate do Soldado Ryan"},
    {"pessoa_id": "p_stanton", "filme_titulo": "Procurando Nemo"},
    {"pessoa_id": "p_degneres", "filme_titulo": "Procurando Nemo"},
    {"pessoa_id": "p_ebert", "filme_titulo": "Matrix"}, 
    {"pessoa_id": "p_ebert", "filme_titulo": "Cidade de Deus"},
]


def gerar_banco_base():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        # Limpar o banco de dados para garantir um começo limpo
        print("Limpando o banco de dados...")
        session.run("MATCH (n) DETACH DELETE n")

        # PASSO 1: CRIAR RESTRIÇÕES
        print("--- Garantindo Restrições ---")
        session.execute_write(criar_restricao_se_nao_existe, "Person", "id")
        session.execute_write(criar_restricao_se_nao_existe, "Film", "title")
        session.execute_write(criar_restricao_se_nao_existe, "Sponsor", "name")
        session.execute_write(criar_restricao_se_nao_existe, "Streaming", "name")
        print("\n")

        # PASSO 2: GERAR NODOS
        print("--- Gerando Nodos ---")
        
        # Gerar Filmes a partir da lista
        for filme_data in FILMES_PARA_CRIAR:
            session.execute_write(criar_nodo, ["Film"], "title", filme_data)
        print(f"{len(FILMES_PARA_CRIAR)} Filmes criados.")
        
        # Gerar Pessoas a partir da lista
        for pessoa_data in PESSOAS_PARA_CRIAR:
            rotulos = ["Person"] + pessoa_data.pop('papeis', [])
            session.execute_write(criar_nodo, rotulos, "id", pessoa_data)
        print(f"{len(PESSOAS_PARA_CRIAR)} Pessoas criadas.")

        # Gerar Sponsors e Streaming
        nomes_sponsors = [f"Sponsor Company {i}" for i in range(5)]
        for nome in nomes_sponsors:
            dados = {"name": nome, "country": "USA"}
            session.execute_write(criar_nodo, ["Sponsor"], "name", dados)
        print(f"{len(nomes_sponsors)} Sponsors criados.")
        nomes_streaming = ["Netflix", "Amazon Prime Video", "Disney+", "HBO Max"]
        for nome in nomes_streaming:
            dados = {"name": nome, "website": f"www.{nome.replace(' ', '').lower()}.com"}
            session.execute_write(criar_nodo, ["Streaming"], "name", dados)
        print(f"{len(nomes_streaming)} Streaming services criados.\n")

        # PASSO 3: GERAR RELACIONAMENTOS
        print("--- Gerando Relacionamentos ---")
        
        # Relacionamentos Pessoa-Filme a partir da lista
        for rel in RELACIONAMENTOS_PARA_CRIAR:
            session.execute_write(relacionar_pessoa_filme, rel["pessoa_id"], rel["filme_titulo"])
        print(f"{len(RELACIONAMENTOS_PARA_CRIAR)} relacionamentos Pessoa-Filme criados.")

        # Relacionamentos de Sponsor e Streaming
        filmes = [f['title'] for f in FILMES_PARA_CRIAR]
        for nome_sponsor in nomes_sponsors:
            filme_a_patrocinar = random.choice(filmes)
            props = {"budget": random.randint(10000000, 150000000)}
            session.execute_write(relacionar_sponsor_filme, nome_sponsor, filme_a_patrocinar, props)
        print("Relacionamentos Sponsor-Filme criados.")
        
        for titulo_filme in filmes:
            if random.random() > 0.4: # 60% de chance de estar em um streaming
                plataforma = random.choice(nomes_streaming)
                start_date = datetime.date(random.randint(2020, 2024), random.randint(1, 12), random.randint(1, 28))
                end_date = start_date + datetime.timedelta(days=random.randint(180, 730))
                props = {"start_broadcasting": start_date.isoformat(), "end_broadcasting": end_date.isoformat()}
                session.execute_write(relacionar_streaming_filme, plataforma, titulo_filme, props)
        print("Relacionamentos Streaming-Filme criados.")

    driver.close()
    print("\nProcesso de geração de banco de dados concluído!")

# --- FUNÇÃO PRINCIPAL DE GERAÇÃO ---
def gerar_banco_sintetico(num_pessoas, num_filmes, num_sponsors, densidade_rel):
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

    with driver.session() as session:
        # PASSO 1: CRIAR RESTRIÇÕES
        print("--- Garantindo Restrições ---")
        session.execute_write(criar_restricao_se_nao_existe, "Person", "id")
        session.execute_write(criar_restricao_se_nao_existe, "Film", "title")
        session.execute_write(criar_restricao_se_nao_existe, "Sponsor", "name")
        session.execute_write(criar_restricao_se_nao_existe, "Streaming", "name")
        print("\n")

        # PASSO 2: GERAR NODOS
        print("--- Gerando Nodos ---")
        
        # Gerar Sponsors, Streaming e Filmes
        nomes_sponsors = [fake.company() for _ in range(int(num_sponsors))]
        for nome in nomes_sponsors:
            dados = {"name": nome, "country": fake.country()}
            session.execute_write(criar_nodo, ["Sponsor"], "name", dados)
        print(f"{len(nomes_sponsors)} Sponsors criados.")
        nomes_streaming = ["Netflix", "Amazon Prime Video", "Disney+", "HBO Max", "Apple TV+"]
        for nome in nomes_streaming:
            dados = {"name": nome, "website": f"www.{nome.replace(' ', '').lower()}.com"}
            session.execute_write(criar_nodo, ["Streaming"], "name", dados)
        print(f"{len(nomes_streaming)} Streaming services criados.")
        titulos_filmes = [f"{fake.catch_phrase()} {i}" for i in range(int(num_filmes))]
        for titulo in titulos_filmes:
            dados = {
                "title": titulo,
                "release_year": random.randint(1980, 2025),
                "winner_years_list": [random.randint(1980, 2025) for _ in range(random.randint(0, 10))]
            }
            if random.random() > 0.2:
                dados['genre'] = random.choice(GENEROS_PERMITIDOS)
            session.execute_write(criar_nodo, ["Film"], "title", dados)
        print(f"{num_filmes} Filmes criados.")
        
        ids_pessoas = [f"person_{i:03}" for i in range(int(num_pessoas))]
        for pid in ids_pessoas:
            rotulos = ["Person"]
            dados = {
                "id": pid,
                "name": fake.name(),
                "phone_list": [fake.phone_number() for _ in range(random.randint(0, 100))]
            }
            
            if random.random() > 0.1: # 90% de chance de ter data de nascimento
                dados["birth_date"] = fake.date_of_birth(minimum_age=25, maximum_age=80).isoformat()
            
            # Cada papel tem uma chance independente de ser adicionado
            # Uma pessoa pode não ter nenhum papel, um, ou vários.
            if random.random() > 0.6: # 40% de chance de ser Diretor
                rotulos.append("Director")
                if random.random() > 0.2: # 80% de chance de ter o atributo opcional
                    dados["debut_film_year"] = random.randint(1990, 2020)

            if random.random() > 0.6: # 40% de chance de ser Produtor
                rotulos.append("Producer")
                if random.random() > 0.1: # 90% de chance de ter o atributo opcional
                    dados["producer_type"] = random.choice(PRODUCER_TYPES)

            if random.random() > 0.6: # 40% de chance de ser Revisor
                rotulos.append("Reviewer")
                if random.random() > 0.2: # 80% de chance de ter o atributo opcional
                    dados["critic_profile_url"] = f"https://criticos.com/{dados['name'].replace(' ', '-').lower()}"
            
            session.execute_write(criar_nodo, rotulos, "id", dados)
        print(f"{num_pessoas} Pessoas criadas, algumas com papéis e outras sem.\n")

        # PASSO 3: GERAR RELACIONAMENTOS
        print("--- Gerando Relacionamentos ---")
        if ids_pessoas and titulos_filmes:
            for pid in ids_pessoas:
                num_rel = random.randint(0, int(densidade_rel))
                for _ in range(num_rel):
                    session.execute_write(relacionar_pessoa_filme, pid, random.choice(titulos_filmes))
            print("Relacionamentos Pessoa-Filme criados.")

        if nomes_sponsors and titulos_filmes:
            # Itera sobre cada filme para decidir se ele terá um e apenas um sponsor
            for titulo_filme in titulos_filmes:
                # Chance de 20% de um filme ter um patrocinador
                if random.random() < 0.2:
                    # Se tiver, escolhe um e apenas um sponsor aleatório da lista
                    sponsor_escolhido = random.choice(nomes_sponsors)
                    
                    props = {"budget": random.randint(500000, 50000000)}
                    
                    # Cria o relacionamento único
                    session.execute_write(relacionar_sponsor_filme, sponsor_escolhido, titulo_filme, props)
            print("Relacionamentos Sponsor-Filme criados.")

        if nomes_streaming and titulos_filmes:
            for titulo_filme in titulos_filmes:
                num_plataformas = random.randint(1, 3)
                plataformas_escolhidas = random.sample(nomes_streaming, num_plataformas)
                for plataforma in plataformas_escolhidas:
                    start_date = fake.date_between(start_date="-3y", end_date="today")
                    end_date = start_date + datetime.timedelta(days=random.randint(30, 1095))
                    props = {
                        "start_broadcasting": start_date.isoformat(),
                        "end_broadcasting": end_date.isoformat()
                    }
                    session.execute_write(relacionar_streaming_filme, plataforma, titulo_filme, props)
            print("Relacionamentos Streaming-Filme criados.")

    driver.close()
    print("\nProcesso de geração de banco sintético concluído!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gera um banco de dados sintético no Neo4j.")
    
    parser.add_argument("--pessoas", type=int, default=2500, help="Número de pessoas a serem geradas.")
    parser.add_argument("--filmes", type=int, default=1500, help="Número de filmes a serem gerados.")
    parser.add_argument("--sponsors", type=int, default=100, help="Número de patrocinadores a serem gerados.")
    parser.add_argument("--densidade", type=int, default=3, help="Fator de densidade para relacionamentos (1 a N).")
    
    args = parser.parse_args()
    
    # Cria os dados reais
    gerar_banco_base()

    gerar_banco_sintetico(
        num_pessoas=args.pessoas,
        num_filmes=args.filmes,
        num_sponsors=args.sponsors,
        densidade_rel=args.densidade
    )