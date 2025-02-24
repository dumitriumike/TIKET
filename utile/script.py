import psycopg2

# String-ul de conexiune
conn_string = "postgresql://neondb_owner:npg_RhIHry6Vozl5@ep-sparkling-sun-a2l6j3wg-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

try:
    # Conectare la baza de date
    conn = psycopg2.connect(conn_string)
    print("Conexiune reușită!")
    
    # Crearea unui cursor pentru a executa interogări
    cursor = conn.cursor()
    
    # Exemplu de interogare
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print("Versiunea bazei de date:", db_version)
    
    # Închiderea cursorului și conexiunii
    cursor.close()
    conn.close()
    
except Exception as e:
    print("Eroare la conectare:", e) 