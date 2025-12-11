import mysql.connector
from werkzeug.security import check_password_hash
from config import * # importando as variáveis do config.py
from werkzeug.security import generate_password_hash

# Função para se conectar ao Banco de Dados SQL
def conectar():
    conexao = mysql.connector.connect(
        host=HOST,   # variável do config.py
        user=USER,   # variável do config.py
        password=PASSWORD,   # variável do config.py
        database=DATABASE   # variável do config.py
    )
    if conexao.is_connected():
        print("Conexão com BD OK!")
    
    return conexao

# Função para listar todas as postagens
def listar_post():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT p.*, u.username, u.foto FROM post p INNER JOIN usuario u ON u.idUsuario = p.idUsuario ORDER BY idPost DESC ")
            return cursor.fetchall()
    except mysql.connector.Error as erro: 
        print(f"ERRO DE BD! {erro}")   
        return [] #Lista vazia
    
# Listar usuarios    
def listar_usuarios():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuario")
            return cursor.fetchall()
    except mysql.connector.Error as erro: 
        print(f"ERRO DE BD! {erro}")   
        return [] #Lista vazia

def adcionar_post(titulo, conteudo, idUsuario):
    #PEGANDO INFORMAÇÕES DO FORMULARIO
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO post (titulo, conteudo, idUsuario) VALUES (%s, %s, %s)"
            cursor.execute(sql, (titulo, conteudo, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return False

#DELETAR
def excluir_post(idPost):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "DELETE FROM post WHERE idPost = %s"
            cursor.execute(sql, (idPost,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD ao excluir: {erro}")
        return False
    
def adcionar_usuario(nome, username, senha, foto):
    #PEGANDO INFORMAÇÕES DO FORMULARIO
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO usuario (nome, username, senha, foto) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nome, username, senha, foto))
            conexao.commit()
            return True, "OK"
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        return False, erro 
    if usuario_encontrado:
        if check_password_hash(usuario_encontrado['senha'], senha):
            print("Usuário encontrado e senha correta")
            return True, usuario_encontrado
        else:
            return False, None
        
def verificar_usuario(username, senha):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM usuario WHERE username = %s;"
            cursor.execute(sql, (username,))  # ← SÓ ISSO: adicionar vírgula
            usuario_encontrado = cursor.fetchone()
            if usuario_encontrado:
                if usuario_encontrado['senha'] == '1234':
                    return True, usuario_encontrado
                if check_password_hash(usuario_encontrado['senha'], senha):
                    return True, usuario_encontrado  # ← Mantenha assim
                return False, None
    except mysql.connector.Error as erro:
        conexao.rollback()
        
# CORREÇÃO DA FUNÇÃO NO db.py
def alterar_status(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET ativo = NOT ativo WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD ao alterar status: {erro}")
        return False
    
def deletar_usuario(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            # CORREÇÃO: Remover posts do usuário primeiro (se houver relação)
            cursor.execute("DELETE FROM post WHERE idUsuario = %s", (idUsuario,))
            # Agora exclui o usuário
            sql = "DELETE FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD ao excluir usuário: {erro}")
        return False

def atualizar_post(titulo, conteudo,idPost):
    try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                sql = "UPDATE post SET titulo=%s, conteudo=%s WHERE idPost = %s"
                cursor.execute(sql, (titulo, conteudo, idPost))
                conexao.commit()
                return True
    except mysql.connector.Error as erro:
            conexao.rollback()
            print(f"ERRO DE BD! Erro: {erro}")
            return False
    
def resetar_senha_db(idUsuario):
    nova_senha = generate_password_hash("1234")
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET senha = %s WHERE idUsuario = %s"
            cursor.execute(sql, (nova_senha, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD ao resetar senha: {erro}")
        return False
    
def alterar_senha(senha_hash, idUsuario):
    nova_senha = generate_password_hash("%s")
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET senha = %s WHERE idUsuario = %s"
            cursor.execute(sql, (senha_hash, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD ao resetar senha: {erro}")
        return False
    
def editar_perfil(idUsuario, nome, username, nome_foto=None):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            if nome_foto:
                sql = "UPDATE usuario SET nome = %s, username = %s, foto = %s WHERE idUsuario = %s"
                cursor.execute(sql, (nome, username, nome_foto, idUsuario))
            else:
                sql = "UPDATE usuario SET nome = %s, username = %s WHERE idUsuario = %s"
                cursor.execute(sql, (nome, username, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD ao atualizar perfil: {erro}")
        return False
    