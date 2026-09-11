from flask import Flask, render_template, request, flash, redirect, url_for
import fdb
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'

host = "localhost"
database = r'C:\Users\Aluno\Desktop\Nova pasta\biblioteca\biblioteca\biblioteca.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(host=host, database=database, user=user, password=password)




@app.route('/')
def index():
    cursor = con.cursor() #Abrindo o cursor

    cursor.execute(""" SELECT l.id_livro,l.nome,l.autor,l.ano_publicado FROM LIVRO l
                   order by l.nome """)

    livros = cursor.fetchall() #Insere as informações em uma lista com tupla. Ex: [()]

    cursor.close() #Fechando o cursor
    return render_template('index.html', livros=livros)



@app.route('/novo')
def novo():
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

        cursor.execute("""INSERT INTO livro (nome,autor,ano_publicado) values( ? , ? , ? ) """,
                       (nome, autor, ano_publicado))
        con.commit()
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
        cursor.execute("""SELECT id_livro,nome,autor,ano_publicado FROM LIVRO WHERE id_livro = ? """,(id,))
        livro = cursor.fetchone()

        if not livro:
            flash('Livro não encontrado!')
            return redirect(url_for("index"))

        if request.method == 'POST':
            nome = request.form['titulo']
            autor = request.form['autor']
            ano_publicado = request.form['ano_publicacao']


            cursor.execute(""" UPDATE livro SET nome = ?, autor = ?, ano_publicado = ?
                           where id_livro = ?""",(nome,autor,ano_publicado, id))

            con.commit()
            flash("Livro editado com sucesso")
            return redirect(url_for('index'))

        return render_template('editar.html', livro=livro)
    except Exception as e :
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
        flash("Livro deletado com sucesso!")
        return redirect(url_for("index"))
    except Exception as e:
        con.rollback()
        flash(f"Ocorreu um erro -> {e}")
        return redirect(url_for("index"))
    finally:
        cursor.close()



@app.route('/')
def lista_usuario():
    cursor = con.cursor()

    cursor.execute("""SELECT u.id_usuario, u.nome, u.email, u.senha FROM usuario u
                   order by u.nome""")

    usuarios = cursor.fetchall()

    cursor.close()
    return render_template('cadastrar_usuario.html', usuarios=usuarios)





@app.route("/cadastrar", methods=['POST'])
def cadastrar():
    nome = request.form['nome']
    email = request.form['email']
    senha = request.form['senha']

    cursor = con.cursor()

    try:
        cursor.execute("""SELECT 1 FROM usuario u WHERE u.nome =?""",(nome,))
        if cursor.fetchone():
            flash("Erro: usuário ja cadastrado!")
            return redirect(url_for('cadastrar_usuario'))

        cursor.execute("""INSERT INTO usuario (nome,email,senha) values(?,?,?)""",
                       nome,email,senha)
        con.commit()
        flash("Usuário cadastrado com sucesso!")
    except Exception as e:
        flash(f"Ocorreu um erro -> {e}")
        con.rollback()
    finally:
        cursor.close()
    return redirect(url_for("lista_usuario"))







if __name__ == '__main__':
    app.run(debug=True)

