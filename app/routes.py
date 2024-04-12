from flask import render_template, request, redirect, url_for, session, flash
import pyodbc
from app import app
from app.templates.doc import APP

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configurações do banco de dados SQL Server
DB_SERVER = '40.114.35.162'
DB_NAME = 'master'
DB_USER = 'administrador'
DB_PASSWORD = '20ca11ad20!!'

def conectar_banco():
    try:
        conn = pyodbc.connect(f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}')
        return conn
    except Exception as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar as credenciais no banco de dados
        conn = conectar_banco()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT [user], pwd FROM usr WHERE [user] = ?", (username,))
                user = cursor.fetchone()
                if user and password == user.pwd:
                    # Se as credenciais estiverem corretas, definimos uma variável de sessão para indicar que o usuário está logado
                    session['logged_in'] = True
                    session['username'] = username
                    return APP.index()
                else:
                    # Se as credenciais estiverem incorretas, renderizamos a página de login novamente com uma mensagem de erro
                    return render_template('login.html', error="Usuário ou senha incorretos.")
            except Exception as e:
                print("Erro ao consultar o banco de dados:", e)
                # Se ocorrer um erro durante o processo de login, renderizamos a página de login novamente com uma mensagem de erro
                return render_template('login.html', error="Ocorreu um erro ao fazer login. Por favor, tente novamente.")
            finally:
                conn.close()
        else:
            # Se houver um erro de conexão com o banco de dados, renderizamos a página de login novamente com uma mensagem de erro
            return render_template('login.html', error="Erro de conexão com o banco de dados. Tente novamente mais tarde.")

    # Se a solicitação for GET, renderizamos a página de login normalmente
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Limpar a sessão do usuário
    session.clear()
    # Redirecionar para a página de login
    return redirect(url_for('login'))

@app.route('/doc_page')
def doc_page():
    # Verifica se o usuário está logado
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Se o usuário estiver logado, renderize a página de cópias de documentos
    return redirect('http://127.0.0.1:8050/')  # Altere para o URL correto do seu servidor Dash

@app.route('/registrar', methods=['POST'])
def registrar():
    if request.method == 'POST':
        username = request.form['registerUsername']
        email = request.form['registerEmail']
        password = request.form['registerPassword']
        
        # Inserir dados no banco de dados
        conn = conectar_banco()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO usr ([user], email, pwd) VALUES (?, ?, ?)", (username, email, password))
                conn.commit()
                flash('Registro realizado com sucesso. Entre em contato com o moderador.')
                return redirect(url_for('login'))
            except Exception as e:
                print("Erro ao salvar dados no banco de dados:", e)
                flash('Ocorreu um erro ao registrar. Entre em contato com o moderadr.')
                return redirect(url_for('login'))
            finally:
                conn.close()
        else:
            flash('Erro de conexão com o banco de dados. Tente novamente mais tarde.')
            return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
