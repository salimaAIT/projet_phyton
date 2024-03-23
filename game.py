from flask import Flask, request, render_template, redirect, session,Blueprint, flash, url_for,g
from werkzeug.security import check_password_hash, generate_password_hash
from pathlib import Path
import sqlite3
import os
import random


app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = 'database.db'

# Fonction pour créer la connexion à la base de données
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Crée une base de données si elle existe pas 
if not Path('database.db').exists():
   with app.app_context():
     db = get_db()
     with app.open_resource('schema.sql', mode='r') as f:
         db.cursor().executescript(f.read())
     db.commit()

# Routage pour la page d'accueil
@app.route('/')
def index():
    cur = get_db().cursor()
    return render_template('index.html')

# Routage pour la page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
         flash('Login successful!', 'success') 
         session['username'] = username
         return redirect(url_for('devine_le_nombre')) 
    else:
        return 'Nom d\'utilisateur ou mot de passe incorrect'
    
  return render_template('login.html')



# Routage pour la page d'inscription
@app.route('/register', methods=('GET', 'POST'))
def register():
 if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        return 'Cet utilisateur existe déjà'

    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    db.commit()
    return render_template('login.html')

 return render_template('register.html')

# Routage pour la page de déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Fonction pour exécuter des requêtes SQL
def query_db(query, args=(), one=False):
    cur = get_db().cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Fonction pour enregistrer le score dans la base de données 
def enregistrer_score_utilisateur(username, score):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO scores (username, score) VALUES (?, ?)", (username, score))
    conn.commit()



# Fonction pour initialiser une nouvelle partie de devine le nombre
def init_devine_le_nombre():
    session['nombre_a_deviner'] = random.randint(1, 100)
    session['nombre_de_essais'] = 0
    session['limite_essais'] = 10

@app.route('/guess_number', methods=['GET', 'POST'])
def devine_le_nombre():
    if 'nombre_a_deviner' not in session:
        init_devine_le_nombre()

    if request.method == 'POST':
        essai = int(request.form['essai'])
        session['nombre_de_essais'] += 1

        if essai < session['nombre_a_deviner']:
            message = "Le nombre que tu cherches est plus grand."
        elif essai > session['nombre_a_deviner']:
            message = "Le nombre que tu cherches est plus petit."
        else:
            message = f"Bravo ! Tu as deviné le nombre en {session['nombre_de_essais']} essais."
            enregistrer_score_utilisateur(session['username'], session['nombre_de_essais'])
            session.pop('nombre_a_deviner')
            session.pop('nombre_de_essais')
            session.pop('limite_essais')
            return render_template('result.html', message=message)

        if session['nombre_de_essais'] >= session['limite_essais']:
            message = f"Désolé, tu as épuisé tes {session['limite_essais']} essais. Le nombre était {session['nombre_a_deviner']}."
            session.pop('nombre_a_deviner')
            session.pop('nombre_de_essais')
            session.pop('limite_essais')
            return render_template('result.html', message=message)

        return render_template('guess_number.html', message=message)

    return render_template('guess_number.html')

if __name__ == '__main__':
    app.run(debug=True)
