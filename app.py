from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# =========================
# INITIALISATION DB
# =========================
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS etudiants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            age INTEGER,
            sexe TEXT,
            sommeil REAL,
            repas INTEGER,
            fastfood TEXT,
            sport INTEGER,
            fatigue TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# =========================
# PAGE ACCUEIL (FORMULAIRE)
# =========================
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        nom = request.form['nom']
        age = request.form['age']
        sexe = request.form['sexe']
        sommeil = request.form['sommeil']
        repas = request.form['repas']
        fastfood = request.form['fastfood']
        sport = request.form['sport']
        fatigue = request.form['fatigue']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO etudiants (nom, age, sexe, sommeil, repas, fastfood, sport, fatigue)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nom, age, sexe, sommeil, repas, fastfood, sport, fatigue))

        conn.commit()
        conn.close()

        print("Données enregistrées !")

    return render_template('index.html')


# =========================
# PAGE DONNEES (TABLEAU)
# =========================
@app.route('/donnees')
def afficher_donnees():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM etudiants")
    donnees = cursor.fetchall()

    conn.close()

    return render_template('donnees.html', donnees=donnees)


# =========================
# PAGE ANALYSE (GRAPHIQUES)
# =========================
@app.route('/analyse')
def analyse():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # moyennes
    cursor.execute("SELECT AVG(age), AVG(sommeil), AVG(repas), AVG(sport) FROM etudiants")
    moyennes = cursor.fetchone()

    # fatigue
    cursor.execute("SELECT fatigue, COUNT(*) FROM etudiants GROUP BY fatigue")
    fatigue_data = cursor.fetchall()

    # sommeil selon fatigue
    cursor.execute("SELECT fatigue, AVG(sommeil) FROM etudiants GROUP BY fatigue")
    sommeil_fatigue = cursor.fetchall()

    # corrélation
    cursor.execute("""
    SELECT sommeil,
    CASE 
        WHEN fatigue='Faible' THEN 1
        WHEN fatigue='Moyen' THEN 2
        WHEN fatigue='Élevé' THEN 3
    END
    FROM etudiants
    """)
    data_corr = cursor.fetchall()

    conn.close()

    # interprétation
    interpretation = ""

    if moyennes[1] < 6:
        interpretation += " Manque de sommeil.<br>"
    else:
        interpretation += " Sommeil correct.<br>"

    if fatigue_data:
        max_f = max(fatigue_data, key=lambda x: x[1])[0]
        interpretation += f"Fatigue dominante : {max_f}.<br>"

    interpretation += " La régression montre la relation entre sommeil et fatigue."

    return render_template(
        'analyse.html',
        moyennes=moyennes,
        fatigue_data=fatigue_data,
        sommeil_fatigue=sommeil_fatigue,
        data_corr=data_corr,
        interpretation=interpretation
    )


# =========================
# LANCEMENT
# =========================
if __name__ == '__main__':
    app.run(debug=True)