CREATE DATABASE blog_emannoel;

USE blog_emannoel;

CREATE TABLE usuario (
    idUsuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    username VARCHAR(15) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    foto VARCHAR(100),
    dataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE post (
    idPost INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(50) NOT NULL,
    conteudo TEXT NOT NULL,
    dataPost TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idUsuario INT,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
    ON DELETE CASCADE
);

-- Cadastrar um usuário teste
INSERT INTO usuario (nome, user, senha) VALUES ("Teste", "Teste", "Teste");

-- Adcionar novas colunas exemplo:
ALTER TABLE usuario 
ADD ativo BOOLEAN NOT NULL DEFAULT 1;

CREATE VIEW vw_total_posts AS
SELECT
COUNT(*) AS total_posts
FROM post p 
JOIN usuario u ON p.idUsuario = u.idUsuario
WHERE 
u.ativo = 1;

CREATE VIEW vw_usuarios AS
SELECT
COUNT(*) AS total_usuarios
FROM 
usuario
WHERE
ativo = 1;