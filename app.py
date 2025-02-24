from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_babel import Babel, _
import psycopg2
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configurare limbi suportate
app.config['LANGUAGES'] = ['en', 'fr', 'ro']
app.config['BABEL_DEFAULT_LOCALE'] = 'en'

# Inițializare Babel
babel = Babel(app)

# Selectare limbă
@babel.localeselector
def get_locale():
    g.language = session.get('language', request.accept_languages.best_match(app.config['LANGUAGES']))
    return g.language

# Conexiune la PostgreSQL
conn_string = "postgresql://neondb_owner:npg_RhIHry6Vozl5@ep-sparkling-sun-a2l6j3wg-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    try:
        return psycopg2.connect(conn_string)
    except Exception as e:
        flash(f"Eroare la conectare: {e}", "error")
        return None

@app.route('/set_language/<language>')
def set_language(language):
    if language in app.config['LANGUAGES']:
        session['language'] = language
        session.modified = True  # Forțează salvarea sesiunii
    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_company', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        city = request.form['city']
        country = request.form['country']
        phone = request.form['phone']
        website = request.form['website']
        industry = request.form['industry']

        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO company (name, address, city, country, phone, website, industry) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (name, address, city, country, phone, website, industry)
                )
                conn.commit()
                flash(_("Companie adăugată cu succes!"), "success")
            except Exception as e:
                flash(f"Eroare la adăugare: {e}", "error")
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for('index'))
    return render_template('add_company.html')

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        email = request.form['email']
        password_hash = request.form['password_hash']
        full_name = request.form['full_name']
        role = request.form['role']
        phone = request.form['phone']
        company_id = request.form['company_id']
        avatar_url = request.form['avatar_url']

        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO app_user (email, password_hash, full_name, role, phone, company_id, avatar_url) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (email, password_hash, full_name, role, phone, company_id, avatar_url)
                )
                conn.commit()
                flash(_("Utilizator adăugat cu succes!"), "success")
            except Exception as e:
                flash(f"Eroare la adăugare: {e}", "error")
            finally:
                cursor.close()
                conn.close()
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password_hash = request.form['password_hash']

        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM app_user WHERE email = %s AND password_hash = %s;", (email, password_hash))
                user = cursor.fetchone()
                if user:
                    session['user'] = {
                        'id': user[0],
                        'email': user[1],
                        'full_name': user[3],
                        'role': user[4],
                        'company_id': user[6]  # Adăugăm company_id în sesiune
                    }
                    flash(_("Autentificare reușită!"), "success")
                    return redirect(url_for('index'))
                else:
                    flash(_("Email sau parolă incorectă!"), "error")
            except Exception as e:
                flash(f"Eroare la autentificare: {e}", "error")
            finally:
                cursor.close()
                conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash(_("Te-ai deconectat cu succes!"), "success")
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Date Companie
        company_name = request.form['company_name']
        company_address = request.form['company_address']
        company_phone = request.form['company_phone']
        company_country = request.form['company_country']

        # Date Administrator
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                
                # Adăugăm compania
                cursor.execute(
                    "INSERT INTO company (name, address, phone, country) VALUES (%s, %s, %s, %s) RETURNING id;",
                    (company_name, company_address, company_phone, company_country)
                )
                company_id = cursor.fetchone()[0]
                
                # Adăugăm administratorul
                cursor.execute(
                    "INSERT INTO app_user (email, password_hash, full_name, role, company_id) VALUES (%s, %s, %s, %s, %s);",
                    (email, password, full_name, 'admin', company_id)
                )
                
                conn.commit()
                flash(_("Înregistrare reușită! Te poți autentifica acum."), "success")
                return redirect(url_for('login'))
                
            except Exception as e:
                conn.rollback()
                flash(f"Eroare la înregistrare: {e}", "error")
            finally:
                cursor.close()
                conn.close()
    
    return render_template('register.html')

@app.route('/admin')
def admin_dashboard():
    if 'user' not in session or session['user']['role'] != 'admin' or 'company_id' not in session['user']:
        flash(_("Acces restricționat!"), "error")
        return redirect(url_for('index'))
    
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            # Obține utilizatorii companiei
            cursor.execute("SELECT * FROM app_user WHERE company_id = %s;", (session['user']['company_id'],))
            users = cursor.fetchall()
            
            # Obține logurile companiei
            cursor.execute("SELECT * FROM activity_log WHERE company_id = %s ORDER BY timestamp DESC;", (session['user']['company_id'],))
            logs = cursor.fetchall()
            
            return render_template('admin_dashboard.html', users=users, logs=logs)
        except Exception as e:
            flash(f"Eroare: {e}", "error")
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('index'))

def log_activity(user_id, action):
    if 'user' not in session or 'company_id' not in session['user']:
        return
    
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_log (user_id, company_id, action) VALUES (%s, %s, %s);",
                (user_id, session['user']['company_id'], action)
            )
            conn.commit()
        except Exception as e:
            print(f"Eroare la logare activitate: {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
