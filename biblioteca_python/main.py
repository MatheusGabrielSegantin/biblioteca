from flask import Flask, render_template, request, flash, redirect, url_for
import fdb


app = Flask(__name__)

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
            flash("Erro: Livro ja cadastrado!")
            return redirect(url_for('novo'))


    except Exception as e:

    finally:







if __name__ == '__main__':
    app.run(debug=True)

