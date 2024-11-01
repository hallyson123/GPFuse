CREATE DATABASE TesteRel; 
\c TesteRel

CREATE TYPE DIRETOR_LISTA_PROPRIEDADE_ENUM AS ENUM("597", "430")
CREATE TYPE FINANCIADOR_NOME_ENUM AS ENUM("financiador_4", "financiador_10", "financiador_2", "financiador_9", "financiador_5", "financiador_6", "financiador_1", "financiador_7", "financiador_3", "financiador_8")
CREATE TYPE STREAMING_NOME_ENUM AS ENUM("Disney+", "Amazon Prime", "Star+", "Paramount+", "Netflix", "Apple TV+", "Globoplay", "HBO Max")

CREATE TABLE pessoa (
  peso REAL,
  CPF INTEGER UNIQUE NOT NULL,
  nome VARCHAR(100) UNIQUE NOT NULL,
  hobbies INT ARRAY[1, 10],
  lista_propriedade INT ARRAY[1, 10],
  CONSTRAINT pk_Pessoa PRIMARY KEY (CPF, nome), 
);

CREATE TABLE pessoa_diretor (
  id SERIAL PRIMARY KEY,
  CPF INTEGER NOT NULL,
  nome VARCHAR(100) NOT NULL,
  sem_compartilhamento VARCHAR(100) NOT NULL,
  lista_propriedade INT ARRAY[1, 10] NOT NULL
);

ALTER TABLE pessoa_diretor ADD COLUMN pessoa_CPF INTEGER;
ALTER TABLE pessoa_diretor ADD COLUMN pessoa_nome VARCHAR(100);
ALTER TABLE pessoa_diretor ADD CONSTRAINT fk_pessoa_diretor_pessoa FOREIGN KEY (pessoa_CPF, pessoa_nome) REFERENCES pessoa(CPF, nome);

CREATE TABLE pessoa_produtor (
  id SERIAL PRIMARY KEY,
  CPF INTEGER NOT NULL,
  nome VARCHAR(100) NOT NULL,
  sem_compartilhamento VARCHAR(100) NOT NULL,
  lista_propriedade INT ARRAY[1, 10] NOT NULL
);

ALTER TABLE pessoa_produtor ADD COLUMN pessoa_CPF INTEGER;
ALTER TABLE pessoa_produtor ADD COLUMN pessoa_nome VARCHAR(100);
ALTER TABLE pessoa_produtor ADD CONSTRAINT fk_pessoa_produtor_pessoa FOREIGN KEY (pessoa_CPF, pessoa_nome) REFERENCES pessoa(CPF, nome);

CREATE TABLE pessoa_avaliador (
  id SERIAL PRIMARY KEY,
  CPF INTEGER NOT NULL,
  nome VARCHAR(100) NOT NULL,
  sem_compartilhamento VARCHAR(100) NOT NULL,
  lista_propriedade INT ARRAY[1, 10] NOT NULL
);

ALTER TABLE pessoa_avaliador ADD COLUMN pessoa_CPF INTEGER;
ALTER TABLE pessoa_avaliador ADD COLUMN pessoa_nome VARCHAR(100);
ALTER TABLE pessoa_avaliador ADD CONSTRAINT fk_pessoa_avaliador_pessoa FOREIGN KEY (pessoa_CPF, pessoa_nome) REFERENCES pessoa(CPF, nome);

CREATE TABLE filme (
  titulo VARCHAR(100) UNIQUE NOT NULL,
  CONSTRAINT pk_Filme PRIMARY KEY (titulo) 
);

CREATE TABLE financiador (
  nome FINANCIADOR_NOME_ENUM UNIQUE NOT NULL,
  CONSTRAINT pk_Financiador PRIMARY KEY (nome) 
);

CREATE TABLE streaming (
  nome STREAMING_NOME_ENUM UNIQUE NOT NULL,
  CONSTRAINT pk_Streaming PRIMARY KEY (nome) 
);
