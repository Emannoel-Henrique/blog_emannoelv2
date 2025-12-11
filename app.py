from flask import Flask, render_template, request, redirect, flash, session
from db import *
import mysql.connector
import os
import time
from werkzeug.security import generate_password_hash, check_password_hash
from config import *  # importando o arquivo config.py


#Acessar as variáveis
secret_key = SECRET_KEY   # variáveis do arquivo config.py
usuario_admin = USUARIO_ADMIN  # variáveis do arquivo config.py
senha_admin = SENHA_ADMIN   # variáveis do arquivo config.py


# Informa o tipo do app
app = Flask(__name__)
app.secret_key = secret_key
#configra pasta de uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads/'



#Rota Página inicial
@app.route('/')
def index():
    postagens = listar_post()
    return render_template('index.html', postagens=postagens)

#Rota do form de post
@app.route('/novopost', methods=['GET','POST'])
def novopost():
    if 'idUsuario' not in session:
        flash("Faça login para postar!")
        return redirect('/login')
    
    if request.method == 'GET':
        return redirect('/')
    else:
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()
        idUsuario = session['idUsuario']
        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect ('/')
        
        post = adcionar_post(titulo, conteudo, idUsuario)
        
        if post:
            flash("Postagem realizada com sucesso!")
            return redirect ('/')
        else:
            flash("ERRO! Falha ao postar!")
            postagens = listar_post()
            return render_template('index.html', postagens=postagens)

#EDITAR POST
@app.route('/editarpost/<int:idPost>', methods=['GET','POST'])
def editarpost(idPost):
    # CORREÇÃO: Verificação correta de admin
    if 'username' not in session and 'admin' not in session:
        flash("Usuário não autorizado tentou editar um post!")
        return redirect('/')

    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            # Buscar o post e o autor
            cursor.execute("SELECT p.*, u.idUsuario FROM post p INNER JOIN usuario u ON p.idUsuario = u.idUsuario WHERE p.idPost = %s", (idPost,))
            post = cursor.fetchone()
            
            if not post:
                flash("Post não encontrado!")
                return redirect('/')
            
            # Verificar se o usuário é o autor ou admin
            if post['idUsuario'] != session.get('idUsuario') and 'admin' not in session:
                flash("Você não tem permissão para editar este post!")
                return redirect('/')
                
    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! {erro}")
        flash("Houve um erro! Tente mais tarde!")
        return redirect('/')

    if request.method == "GET":
        postagens = listar_post()
        return render_template('index.html', postagens=postagens, post=post)
    
    elif request.method == "POST":
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()

        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect(f'/editarpost/{idPost}')
        
        sucesso = atualizar_post(titulo, conteudo, idPost)
        if sucesso:
            flash("Postagem atualizada com sucesso!")
            return redirect('/')
        else:
            flash("Erro ao atualizar postagem!")
            return redirect(f'/editarpost/{idPost}')
       
                         

#DELETAR POST
@app.route('/delete/<int:idPost>', methods=['POST'])
def delete_post(idPost):
    if 'idUsuario' not in session and 'admin' not in session:
        flash("Usuário não autorizado estava tentando excluir um post!")
        return redirect('/')
    sucesso = excluir_post(idPost)
    if sucesso:
        flash("Postagem excluída com sucesso!")
        if 'admin' in session:
            return redirect('/dashboard')
        else:
            return redirect('/')
    else:
        flash("Erro ao excluir postagem!")
        postagens = listar_post()
        return render_template('index.html', postagens=postagens)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":  
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()
        
        if not usuario or not senha:
            flash("Preencha todos os campos!")
            return redirect('/login')
        
        # Verificar se é admin
        if usuario == usuario_admin and senha == senha_admin:
            session['admin'] = True
            return redirect('/dashboard')
        
        # Verificar usuário comum
        resultado, usuario_encontrado = verificar_usuario(usuario, senha)
        
        if resultado:
            if usuario_encontrado['ativo'] == 0:
                flash("Usuário Bloqueado! Contate o administrador.")
                return redirect('/login')

            session['idUsuario'] = usuario_encontrado['idUsuario']
            session['username'] = usuario_encontrado['username']

            # Se a senha é a padrão '1234', redirecionar para mudar senha
            if senha == '1234':
                return redirect('/nova_senha')

            flash("Login realizado com sucesso!")
            return redirect('/')
        else:
            flash("Usuário ou senha incorretos!")
            return redirect('/login')

def verificar_usuario(username, senha):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM usuario WHERE username = %s;"
            cursor.execute(sql, (username,))
            
            usuario_encontrado = cursor.fetchone()
            
            if usuario_encontrado and check_password_hash(usuario_encontrado['senha'], senha):
                return True, usuario_encontrado 
            else:
                return False, None
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BD! {erro}")
        return False, None


#Area do adm
@app.route('/dashboard')
def dashboard():
    # CORREÇÃO: condição mais clara
    if not session.get('admin'):  
        return redirect('/')

    usuarios = listar_usuarios()
    posts = listar_post()
    return render_template('dashboard.html', posts=posts, usuarios=usuarios)   

#Rota do lougout
@app.route('/logout')
def logout():
     session.clear()
     return redirect('/')

# Rota para cadastro de usuário
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    elif request.method == 'POST':
        nome = request.form['nome'].strip() 
        usuario = request.form['username'].lower().strip()
        senha = request.form['senha'].strip()

        if not nome or not usuario or not senha:
            flash('Preencha todos os campos!')
            return redirect('/cadastro')

        senha_hash = generate_password_hash(senha)

        foto = 'placeholder.jpg'  # Valor padrão para foto
        resultado, erro = adcionar_usuario(nome, usuario, senha_hash, foto)
        
        
        if resultado:
            flash("Usuário cadastrado com sucesso!")
            return redirect('/login')
        else:
            if erro.errno == 1062:
                flash("Esse usuário já existe!")
            else:
                flash("Erro ao cadastrar, Procure o suporte")
            return redirect('/cadastro')

@app.route('/usuario/reset/<int:idUsuario>')
def resetar_senha(idUsuario):
    if not session.get('admin'):
        return redirect('/')

    sucesso = resetar_senha_db(idUsuario)

    if sucesso:
        flash("Senha resetada para '1234' com sucesso!")
    else:
        flash("Erro ao resetar a senha!")
    return redirect('/dashboard')

@app.route('/nova_senha')
def nova_senha_view():
    if 'idUsuario' not in session:
        return redirect('/')
    return render_template('nova_senha.html')

@app.route('/usuario/novasenha', methods=['GET','POST'])
def novasenha():
    if 'idUsuario' not in session:
        return redirect('/')
    
    if request.method == "GET":
        return render_template('nova_senha.html')

    if request.method == "POST":
        senha = request.form['senha'].strip()
        confirmacao = request.form['confirmacao'].strip()

        if not senha or not confirmacao:
            flash('Preencha corretamente as senhas!')
            return render_template('nova_senha.html')
        if senha != confirmacao:
            flash('As senhas não correspondem')
            return render_template('nova_senha.html')
        if senha == '1234':
            flash('A senha precisa ser alterada!')
            return render_template('nova_senha.html')
        if senha == ' ':
            flash('A senha não pode ser vazia!')
            return render_template('nova_senha.html')
        
        senha_hash = generate_password_hash(senha)
        idUsuario = session['idUsuario']
        sucesso = alterar_senha(senha_hash, idUsuario)
        if sucesso:
            flash("Senha alterada com sucesso!")
            if 'username' in session:
                return redirect('/perfil')
            return redirect('/login')
        else:
            flash("Erro no cadastro da nova senha!")
            return render_template('nova_senha.html')


@app.errorhandler(404)
def pagina_nao_encontrada(e):
    return render_template('erro404.html'), 404

@app.errorhandler(500)
def erro_interno(e):
    return render_template('erro500.html'), 500


@app.route('/usuario/status/<int:idUsuario>')
def status_usuario(idUsuario):
    if not session.get('admin'):
        flash("Você não tem permissão para alterar status!")
        return redirect('/')
    
    sucesso = alterar_status(idUsuario)

    if sucesso:
        flash("Status do usuário alterado com sucesso!")
    else:
        flash("Erro ao alterar status do usuário!")
    return redirect('/dashboard')

@app.route('/usuario/excluir/<int:idUsuario>')
def excluir_usuario(idUsuario):
    # CORREÇÃO: Verificação mais robusta
    if not session.get('admin'):
        flash("Usuário não autorizado tentou excluir um usuário!")
        return redirect('/')

    # CORREÇÃO: Verificar se não está tentando excluir a si mesmo
    if idUsuario == session.get('idUsuario'):
        flash("Você não pode excluir sua própria conta!")
        return redirect('/dashboard')

    sucesso = deletar_usuario(idUsuario)
    if sucesso:
        flash("Usuário excluído com sucesso!")
    else:
        flash("Erro ao excluir usuário!")
    return redirect('/dashboard')

@app.route('/perfil', methods=['GET','POST'])
def perfil():
    if 'idUsuario' not in session:
        return redirect('/login')

    # Buscar dados do usuário (para ambos GET e POST)
    lista_usuarios = listar_usuarios()
    usuario = None
    for u in lista_usuarios:
        if u['idUsuario'] == session['idUsuario']:
            usuario = u
            break
    
    if usuario is None:
        flash("Usuário não encontrado!")
        return redirect('/')

    if request.method == 'GET':
        return render_template('perfil.html', 
                               nome=usuario['nome'], 
                               username=usuario['username'], 
                               foto=usuario['foto'])

    elif request.method == 'POST':
        # Aqui você vai processar as alterações do perfil
        nome = request.form['nome'].strip()
        username = request.form['user'].strip()
        foto = request.files['foto']

        # Validações básicas
        if not nome or not username:
            flash("Nome e username não podem estar vazios!")
            return redirect('/perfil')

        nome_foto = usuario['foto']  # Mantém a foto atual por padrão

        # Processar a foto se foi enviada
        if foto and foto.filename != '':
            # Validar extensão
            extensao = foto.filename.rsplit('.', 1)[-1].lower()
            if extensao not in ['jpg', 'webp', 'png', 'jfif', 'jpeg']:
                flash("Extensão de imagem inválida! Use JPG, PNG, WEBP ou JFIF.")
                return redirect('/perfil')
            
            # Validar tamanho
            foto.seek(0, 2)  # Vai para o final do arquivo
            tamanho = foto.tell()  # Pega a posição (tamanho)
            foto.seek(0)  # Volta para o início
            
            if tamanho > 4 * 1024 * 1024:
                flash("Imagem muito grande! Tamanho máximo é 4MB.")
                return redirect('/perfil')
            
            # Gerar nome único para a foto
            idUsuario = session['idUsuario']
            nome_foto = f"{idUsuario}_{int(time.time())}.{extensao}"
            
            # Salvar a foto
            try:
                caminho_completo = os.path.join(app.config['UPLOAD_FOLDER'], nome_foto)
                foto.save(caminho_completo)
            except Exception as e:
                print(f"Erro ao salvar foto: {e}")
                flash("Erro ao salvar a imagem!")
                return redirect('/perfil')
                
        # Atualizar no banco de dados
        sucesso = editar_perfil(session['idUsuario'], nome, username, nome_foto)
        
        if sucesso:
            session['username'] = username  # Atualiza na sessão
            flash("Perfil atualizado com sucesso!")
        else:
            flash("Erro ao atualizar perfil!")
        
        return redirect('/perfil')
    




# Executar app, Obrigatorio no final do arquivo
if __name__ == '__main__':
    app.run(debug=True)  

   

   #testeblog