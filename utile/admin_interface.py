import tkinter as tk
from tkinter import messagebox
import psycopg2
from tkinter import ttk

# String-ul de conexiune
conn_string = "postgresql://neondb_owner:npg_RhIHry6Vozl5@ep-sparkling-sun-a2l6j3wg-pooler.eu-central-1.aws.neon.tech/neondb?sslmode=require"

# Funcție pentru conectare la baza de date
def connect_db():
    try:
        conn = psycopg2.connect(conn_string)
        return conn
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare la conectare: {e}")
        return None

# Funcție pentru afișarea datelor dintr-o tabelă
def show_data(table_name):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            
            # Curăță lista existentă
            for i in listbox.get_children():
                listbox.delete(i)
            
            # Adaugă datele în listbox
            for row in rows:
                listbox.insert("", "end", values=row)
            
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la interogare: {e}")

# Funcție pentru adăugarea de date
def add_data(table_name, values):
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} VALUES {values};")
            conn.commit()
            messagebox.showinfo("Succes", "Date adăugate cu succes!")
            cursor.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la adăugare: {e}")

# Funcție pentru verificarea conexiunii
def check_connection():
    conn = connect_db()
    if conn:
        messagebox.showinfo("Succes", "Conexiunea la baza de date a fost stabilită cu succes!")
        conn.close()
    else:
        messagebox.showerror("Eroare", "Conexiunea la baza de date a eșuat!")

# Crearea ferestrei principale
root = tk.Tk()
root.title("Administrare Bază de Date")

# Câmp pentru introducerea numelui tabelei
table_label = tk.Label(root, text="Nume Tabelă:")
table_label.grid(row=0, column=0)
table_entry = tk.Entry(root)
table_entry.grid(row=0, column=1)

# Buton pentru afișarea datelor
show_button = tk.Button(root, text="Afișează Date", command=lambda: show_data(table_entry.get()))
show_button.grid(row=0, column=2)

# Listbox pentru afișarea datelor
columns = ("Coloana1", "Coloana2", "Coloana3")  # Schimbă în funcție de structura tabelei
listbox = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    listbox.heading(col, text=col)
listbox.grid(row=1, column=0, columnspan=3)

# Câmp pentru introducerea valorilor
values_label = tk.Label(root, text="Valori (separate prin virgulă):")
values_label.grid(row=2, column=0)
values_entry = tk.Entry(root)
values_entry.grid(row=2, column=1)

# Buton pentru adăugarea datelor
add_button = tk.Button(root, text="Adaugă Date", command=lambda: add_data(table_entry.get(), tuple(values_entry.get().split(','))))
add_button.grid(row=2, column=2)

# Adaugă un buton pentru verificarea conexiunii
check_button = tk.Button(root, text="Verifică Conexiunea", command=check_connection)
check_button.grid(row=3, column=0, columnspan=3)

# Pornirea interfeței
root.mainloop() 