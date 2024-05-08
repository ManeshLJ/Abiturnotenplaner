import tkinter as tk
from tkinter import ttk
import csv
import locale

def get_grade_boundaries(target_avg):
    try:
        with open('Umrechnungstabelle.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                if float(row[0]) == target_avg:
                    return float(row[2]), float(row[1])
        print("Keine passenden Notengrenzen gefunden für den Ziel-Notendurchschnitt:", target_avg)
    except FileNotFoundError:
        print("Die Umrechnungstabelle.csv Datei wurde nicht gefunden.")
    except Exception as e:
        print("Ein Fehler ist aufgetreten:", e)
    return None, None

def calculate_values(m, d, e, target_avg, total_points):
    print("Debug: calculate_values - Inputs received:")
    print("m:", m)
    print("d:", d)
    print("e:", e)
    print("target_avg:", target_avg)
    print("total_points:", total_points)

    f, g = get_grade_boundaries(target_avg)
    try:
        # Calculate lower and upper bounds for grade boundaries
        result_pairs = []
        for i in range(16):
            for j in range(16):
                if (f - total_points - 4 * (m + d + e)) <= 4 * (i + j) < (g - total_points - 4 * (m + d + e)):
                    lower_bound = total_points - 4 * (i + j)
                    upper_bound = total_points - 4 * (i + j - 1)
                    if lower_bound <= 0:
                        lower_bound = 0
                    result_pairs.append((i, j))
        print("Debug: calculate_values - result_pairs:", result_pairs)
        return result_pairs, f, g
    except ValueError:
        print("Debug: calculate_values - ValueError occurred")
        return [], None, None

def update_table(result_pairs):
    print("Debug: update_table - result_pairs:", result_pairs)

    # Clear previous results
    for row in treeview.get_children():
        treeview.delete(row)

    # If result_pairs is empty, return
    if not result_pairs:
        print("Debug: update_table - No result_pairs provided")
        return

    # Insert value pairs into the table
    for index, (gsk, ph) in enumerate(result_pairs):
        print("Debug: update_table - Inserting value pair - Gsk =", gsk, ", Ph =", ph)
        treeview.insert("", index, values=(f"Gsk: {gsk}", f"Ph: {ph}"))

    print("Debug: update_table - Table updated")



def update_grade_boundaries(f, g):
    label_lower_bound.config(text=f"Untergrenze: {f}")
    label_upper_bound.config(text=f"Obergrenze: {g}")

def update_grade_boundaries_on_entry(*args):
    target_avg = entry_target_avg.get()
    total_points = entry_total_points.get()
    m = entry_m.get()
    d = entry_d.get()
    e = entry_e.get()

    # Check if all inputs are provided
    if target_avg and total_points and m and d and e:
        try:
            # Set locale to handle comma as decimal separator
            locale.setlocale(locale.LC_NUMERIC, 'de_DE.UTF-8')

            # Convert strings to float
            target_avg = locale.atof(target_avg)
            total_points = locale.atof(total_points)
            m = locale.atof(m)
            d = locale.atof(d)
            e = locale.atof(e)

            result_pairs, f, g = calculate_values(m, d, e, target_avg, total_points)

            # Display grade boundaries based on CSV values
            if f is not None and g is not None:
                update_grade_boundaries(f, g)

            # Update the table with calculated result_pairs
            update_table(result_pairs)

            print("Notengrenzen aktualisiert für den Ziel-Notendurchschnitt:", target_avg)
        except ValueError:
            pass  # Ignore faulty inputs
    else:
        # If any input field is empty, clear the table
        update_table([])  # Clear the table if inputs are incomplete


# GUI initialisieren
root = tk.Tk()
root.title("Mein GUI")

# Eingabefelder
label_target_avg = tk.Label(root, text="Zielnotendurchschnitt (1,0-4,0):")
label_target_avg.grid(row=0, column=0)
entry_target_avg = tk.Entry(root)
entry_target_avg.grid(row=0, column=1)

label_lower_bound = tk.Label(root, text="Untergrenze:")
label_lower_bound.grid(row=0, column=2)

label_upper_bound = tk.Label(root, text="Obergrenze:")
label_upper_bound.grid(row=0, column=3)

label_total_points = tk.Label(root, text="Gesamtpunktzahl Qualifikationsphase (0-600):")
label_total_points.grid(row=1, column=0)
entry_total_points = tk.Entry(root)
entry_total_points.grid(row=1, column=1)

label_m = tk.Label(root, text="M:")
label_m.grid(row=2, column=0)
entry_m = tk.Entry(root)
entry_m.grid(row=2, column=1)

label_d = tk.Label(root, text="D:")
label_d.grid(row=2, column=2)
entry_d = tk.Entry(root)
entry_d.grid(row=2, column=3)

label_e = tk.Label(root, text="E:")
label_e.grid(row=2, column=4)
entry_e = tk.Entry(root)
entry_e.grid(row=2, column=5)

# Ausgabe als Tabelle
treeview = ttk.Treeview(root, columns=("Gsk", "Ph"), show="headings")
treeview.heading("Gsk", text="Gsk")
treeview.heading("Ph", text="Ph")
treeview.grid(row=3, column=0, columnspan=6)

# Bind the function to the KeyRelease event of entry_target_avg
entry_target_avg.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_total_points.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_m.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_d.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_e.bind("<KeyRelease>", update_grade_boundaries_on_entry)

root.mainloop()
