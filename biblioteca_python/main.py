from flask import Flask, render_template, request, flash, redirect, url_for, session
import fdb
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = '123456'

host = "localhost"
database = r'C:\Users\Aluno\Desktop\Nova pasta\biblioteca\biblioteca\biblioteca.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)


@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute(""" SELECT l.id_livro,l.nome,l.autor,l.ano_publicado FROM LIVRO l
                   order by l.nome """)
    livros = cursor.fetchall()
    cursor.close()
    return render_template('index.html', livros=livros)


@app.route('/novo')
def novo():
    if 'id_usuario' not in session:
        flash('Precisa estar logado!')
        return redirect(url_for('tela_login'))
    else:
        return render_template('novo.html')


@app.route('/criar', methods=['POST'])
def criar():
    nome = request.form['titulo']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicacao']

    cursor = con.cursor()

    try:
        cursor.execute(""" SELECT 1 FROM livro l WHERE l.nome = ?""", (nome,))

        if cursor.fetchone():
            flash("Erro: Livro ja cadastrado! ❌")
            return redirect(url_for('novo'))

        cursor.execute("""INSERT INTO livro (nome,autor,ano_publicado) 
                       values( ? , ? , ? ) RETURNING id_livro""",
                       (nome, autor, ano_publicado))

        id_livro = cursor.fetchone()[0]
        con.commit()

        arquivo = request.files['imagem']
        arquivo.save(f'uploads/capa{id_livro}.jpg')

        flash("Livro cadastrado com sucesso! 📕")

    except Exception as e:
        flash(f"Ocorreu um erro -> {e} 🤡")
        con.rollback()

    finally:
        cursor.close()

    return redirect(url_for("index"))


@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT id_livro,nome,autor,ano_publicado FROM LIVRO 
                       WHERE id_livro = ? """, (id,))

        livro = cursor.fetchone()

        if not livro:
            flash('Livro não encontrado!')
            return redirect(url_for("index"))

        if request.method == 'POST':
            nome = request.form['titulo']
            autor = request.form['autor']
            ano_publicado = request.form['ano_publicacao']

            cursor.execute(""" UPDATE livro SET nome = ?, autor = ?, ano_publicado = ?
                           where id_livro = ?""",
                           (nome, autor, ano_publicado, id))

            con.commit()
            flash("Livro editado com sucesso")
            return redirect(url_for('index'))

        return render_template('editar.html', livro=livro)

    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro -> {e}")
        return redirect(url_for('index'))

    finally:
        cursor.close()


@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()

    try:
        cursor.execute("""DELETE FROM LIVRO WHERE id_livro = ?""", (id,))
        con.commit()

        flash("Livro deletado com sucesso!")
        return redirect(url_for("index"))

    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro -> {e}")
        return redirect(url_for("index"))

    finally:
        cursor.close()


@app.route('/usuarios')
def lista_usuario():
    cursor = con.cursor()

    cursor.execute("""SELECT u.id_usuario, u.nome, u.email, u.senha FROM usuario u
                   order by u.nome""")

    usuarios = cursor.fetchall()

    cursor.close()

    return render_template('lista_usuario.html', usuarios=usuarios)


@app.route('/cadastrar')
def cadastrar_usuario():
    return render_template('cadastrar_usuario.html')


@app.route("/cadastrar_usuario", methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    if not senha_forte(senha):
        flash("A senha precisa ter 8 ou mais caracteres, uma letra maiúscula e um número!")
        return redirect(url_for('cadastrar_usuario'))

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT 1 FROM usuario u WHERE u.email = ?""", (email,))

        if cursor.fetchone():
            flash("Erro: usuário ja cadastrado!")
            return redirect(url_for('cadastrar_usuario'))

        senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

        cursor.execute("""INSERT INTO usuario (nome,email,senha) 
                       values(?,?,?)""",
                       (nome, email, senha_hash))

        con.commit()

        flash("Usuário cadastrado com sucesso!")

    except Exception as e:
        flash(f"Ocorreu um erro -> {e}")
        con.rollback()

    finally:
        cursor.close()

    return redirect(url_for("tela_login"))


@app.route('/editar_usuario/<int:id>', methods=['GET','POST'])
def editar_usuario(id):

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT id_usuario,nome,email,senha FROM usuario 
                       WHERE id_usuario = ? """, (id,))

        usuario = cursor.fetchone()

        if not usuario:
            flash('Usuário não encontrado!')
            return redirect(url_for("lista_usuario"))

        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']

            if not senha_forte(senha):
                flash("A senha precisa ter 8 ou mais caracteres, uma letra maiúscula e um número!")
                return redirect(url_for('editar_usuario', id=id))

            senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

            cursor.execute(""" UPDATE usuario SET nome = ?, email = ?, senha = ?
                           where id_usuario = ?""",
                           (nome, email, senha_hash, id))

            con.commit()

            flash("Usuário editado com sucesso")
            return redirect(url_for('lista_usuario'))

        return render_template('editar_usuario.html', usuario=usuario)

    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro -> {e}")
        return redirect(url_for('lista_usuario'))

    finally:
        cursor.close()


@app.route('/deletar_usuario/<int:id>', methods=['POST'])
def deletar_usuario(id):

    cursor = con.cursor()

    try:
        cursor.execute("""DELETE FROM usuario WHERE id_usuario = ?""", (id,))
        con.commit()

        flash("Usuario deletado com sucesso!")
        return redirect(url_for("lista_usuario"))

    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro -> {e}")
        return redirect(url_for("lista_usuario"))

    finally:
        cursor.close()


# login

@app.route('/login')
def tela_login():
    return render_template('login.html')


@app.route('/entrar', methods=['POST'])
def entrar():
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT id_usuario,nome,email,senha FROM usuario 
                       WHERE email = ?""", (email,))

        usuario = cursor.fetchone()

        if usuario:
            if bcrypt.check_password_hash(usuario[3], senha):
                session['id_usuario'] = usuario[0]
                flash('Logado!')
                return redirect(url_for('index'))

        flash("Email ou senha incorretos!")
        return redirect(url_for("tela_login"))

    except Exception as e:
        flash(f"Ocorreu um erro -> {e}")
        return redirect(url_for("tela_login"))

    finally:
        cursor.close()


@app.route('/logout')
def logout():
    session.pop('id_usuario', None)
    flash("Logout realizado com sucesso!")
    return redirect(url_for('tela_login'))


#Verificar senha

def senha_forte(senha):
    if len(senha) < 8:
        return False
    elif senha.islower():
        return False
    elif senha.isalpha():
        return False
    elif senha.isdigit():
        return False
    else:
        return True


if __name__ == '__main__':
    app.run(debug=True)
