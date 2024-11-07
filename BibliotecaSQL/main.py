from flask import Flask, render_template, request, flash, redirect, url_for, session
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'senha069'

host = 'localhost'
database = r'C:\Users\Aluno\Downloads\BANCO\BANCO.FDB'
user = 'sysdba'
password = 'sysdba'

con = fdb.connect(
    host=host,
    database=database,
    user=user,
    password=password
)


class Livro:
    def __init__(self, id_livro, titulo, autor, ano_publicado):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicado = ano_publicado


@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICADO FROM livros")
    livros = cursor.fetchall()
    cursor.close()
    return render_template('livros.html', livros=livros)


@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo Livro')


@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicado = request.form['ano_publicado']
    cursor = con.cursor()

    try:
        cursor.execute('SELECT 1 FROM livros WHERE titulo = ?', (titulo,))
        if cursor.fetchone():
            flash('Erro: livro já criado.')
            return redirect(url_for('novo'))

        cursor.execute(
            'INSERT INTO livros (TITULO, AUTOR, ANO_PUBLICADO) VALUES (?, ?, ?)',
            (titulo, autor, ano_publicado)
        )
        con.commit()
        flash('Livro criado com sucesso.')

    finally:
        cursor.close()

    return redirect(url_for('index'))

@app.route('/atualizar')
def atualizar():
    return render_template('editar.html',titulo='Editar livros')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()
    cursor.execute('SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICADO FROM livros WHERE ID_LIVRO = ?', (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash('Livro não encontrado.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicado = request.form['ano_publicado']

        cursor.execute(
            "UPDATE livros SET TITULO = ?, AUTOR = ?, ANO_PUBLICADO = ? WHERE ID_LIVRO = ?",
            (titulo, autor, ano_publicado, id)
        )

        con.commit()
        cursor.close()
        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar Livro')

@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    cursor = con.cursor()
    try:
        cursor.execute('DELETE FROM LIVROS WHERE ID_LIVRO = ? ', (id,))
        con.commit()
        flash("Livro deletado com sucesso!", "success")
    except Exception as e:
        con.rollback()
        flash('Erro ao deletar', 'error')
    finally:
        cursor.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
