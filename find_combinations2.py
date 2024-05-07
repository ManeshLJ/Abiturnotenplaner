import tkinter as tk
from tkinter import ttk

def calculate_values(m, d, e, f):
    try:
        # Berechne Wertepaare für Gsk und Ph, die die Bedingung erfüllen
        result_pairs = []
        for i in range(16):
            for j in range(16):
                if int(f) - 4 * (int(d) + int(m) + int(e)) < 4 * (i + j):
                    result_pairs.append((i, j))
        return result_pairs
    except ValueError:
        return []

def update_table(result_pairs):
    # Lösche vorherige Ergebnisse
    for row in treeview.get_children():
        treeview.delete(row)

    # Trage die Wertepaare in die Tabelle ein
    for index, (gsk, ph) in enumerate(result_pairs):
        treeview.insert("", index, values=(gsk, ph))

def calculate(*args):
    m = entry_m.get()
    d = entry_d.get()
    e = entry_e.get()
    f = entry_f.get()

    if m and d and e and f:  # Überprüfen, ob alle Eingabefelder ausgefüllt sind
        try:
            m = int(m)
            d = int(d)
            e = int(e)
            f = int(f)

            result_pairs = calculate_values(m, d, e, f)
            update_table(result_pairs)  # Aktualisiere die Tabelle mit den berechneten Wertepaaren
            for index, (gsk, ph) in enumerate(result_pairs):
                print(f"Wertepaar {index + 1}: Gsk={gsk}, Ph={ph}")
        except ValueError:
            pass  # Fehlerhafte Eingaben ignorieren

# GUI initialisieren
root = tk.Tk()
root.title("Mein GUI")

# Eingabefelder
label_f = tk.Label(root, text="F (0-300):")
label_f.grid(row=0, column=0)
entry_f = tk.Entry(root)
entry_f.grid(row=0, column=1, columnspan=2)

label_m = tk.Label(root, text="M (0-15):")
label_m.grid(row=1, column=0)
entry_m = tk.Entry(root)
entry_m.grid(row=1, column=1)

label_d = tk.Label(root, text="D (0-15):")
label_d.grid(row=1, column=2)
entry_d = tk.Entry(root)
entry_d.grid(row=1, column=3)

label_e = tk.Label(root, text="E (0-15):")
label_e.grid(row=1, column=4)
entry_e = tk.Entry(root)
entry_e.grid(row=1, column=5)

# Ausgabe als Tabelle
treeview = ttk.Treeview(root, columns=("Gsk", "Ph"), show="headings")
treeview.heading("Gsk", text="Gsk")
treeview.heading("Ph", text="Ph")
treeview.grid(row=2, column=0, columnspan=6)

# Berechnung automatisch durchführen
entry_f.bind("<KeyRelease>", calculate)
entry_m.bind("<KeyRelease>", calculate)
entry_d.bind("<KeyRelease>", calculate)
entry_e.bind("<KeyRelease>", calculate)

root.mainloop()
