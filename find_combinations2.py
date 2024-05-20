import tkinter as tk
from tkinter import ttk
import csv
import locale
import os

def get_grade_boundaries(target_avg):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'Umrechnungstabelle.csv')
    
    try:
        with open(csv_path, newline='') as csvfile:
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
    if f is None or g is None:
        print("Debug: calculate_values - Invalid grade boundaries")
        return [], None, None

    try:
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

    for row in treeview.get_children():
        treeview.delete(row)

    if not result_pairs:
        print("Debug: update_table - No result_pairs provided")
        return

    for index, (gsk, ph) in enumerate(result_pairs):
        print("Debug: update_table - Inserting value pair - Gsk =", gsk, ", Ph =", ph)
        if index % 2 == 0:
            bg_color = "#FFE0B2"  # Brownish color for Gsk
        else:
            bg_color = "#FFCC80"  # Orange color for Ph
        treeview.insert("", index, values=(gsk, ph), tags=('evenrow' if index % 2 == 0 else 'oddrow'))

    treeview.column("#1", anchor="center")  # Center-align Gsk column
    treeview.column("#2", anchor="center")  # Center-align Ph column

    print("Debug: update_table - Table updated")

def update_grade_boundaries(f, g):
    label_lower_bound.config(text=f"Untergrenze: {f}" if f is not None else "Untergrenze: N/A")
    label_upper_bound.config(text=f"Obergrenze: {g}" if g is not None else "Obergrenze: N/A")

def update_grade_boundaries_on_entry(*args):
    target_avg = entry_target_avg.get()
    total_points = entry_total_points.get()
    m = entry_m.get()
    d = entry_d.get()
    e = entry_e.get()

    if target_avg and total_points and m and d and e:
        try:
            # Set locale to US to handle period as decimal separator
            locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
            target_avg = locale.atof(target_avg)
            total_points = locale.atof(total_points)
            m = locale.atof(m)
            d = locale.atof(d)
            e = locale.atof(e)

            result_pairs, f, g = calculate_values(m, d, e, target_avg, total_points)

            if f is None or g is None:
                feedback_label.config(text="Fehler: Umrechnungstabelle.csv fehlt oder Zielnotendurchschnitt nicht gefunden.", fg="red")
            else:
                feedback_label.config(text="Notengrenzen aktualisiert.", fg="green")

            update_grade_boundaries(f, g)
            update_table(result_pairs)

            print("Notengrenzen aktualisiert für den Ziel-Notendurchschnitt:", target_avg)
        except ValueError:
            feedback_label.config(text="Fehlerhafte Eingaben. Bitte überprüfen.", fg="red")
            pass  # Ignore faulty inputs
    else:
        update_table([])  # Clear the table if inputs are incomplete
        feedback_label.config(text="Bitte alle Felder ausfüllen.", fg="red")

# GUI initialisieren
root = tk.Tk()
root.title("Abiturnoterechner")
root.geometry("800x400")

# Set background color to turquoise for the whole GUI
root.configure(bg="#f0f0f0")

# Heading label
heading_label = tk.Label(root, text="Abiturnoterechner", font=("Helvetica", 20, "bold"), bg="#f0f0f0", fg="#333333")
heading_label.grid(row=0, column=0, columnspan=6, pady=(10, 20))

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0", foreground="#000000", font=('Helvetica', 10))
style.map('Treeview', background=[('selected', '#FFD700')], foreground=[('selected', '#000000')])

# Label and Entry widgets for target average
label_target_avg = tk.Label(root, text="Zielnotendurchschnitt (1.0-4.0):", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_target_avg.grid(row=1, column=0, sticky="e", padx=(10, 5))
entry_target_avg = tk.Entry(root)
entry_target_avg.grid(row=1, column=1, padx=(0, 10))

# Label widgets for grade boundaries
label_lower_bound = tk.Label(root, text="Untergrenze:", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_lower_bound.grid(row=1, column=2)

label_upper_bound = tk.Label(root, text="Obergrenze:", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_upper_bound.grid(row=1, column=3)

# Label and Entry widgets for total points
label_total_points = tk.Label(root, text="Gesamtpunktzahl Qualifikationsphase (0-600):", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_total_points.grid(row=2, column=0, sticky="e", padx=(10, 5))
entry_total_points = tk.Entry(root)
entry_total_points.grid(row=2, column=1, padx=(0, 10))

# Label and Entry widgets for subjects
label_m = tk.Label(root, text="M:", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_m.grid(row=3, column=0, sticky="e", padx=(10, 5))
entry_m = tk.Entry(root)
entry_m.grid(row=3, column=1, padx=(0, 10))
entry_m.config(fg="blue", bd=3, bg="#cce5ff")

label_d = tk.Label(root, text="D:", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_d.grid(row=3, column=2, sticky="e", padx=(10, 5))
entry_d = tk.Entry(root)
entry_d.grid(row=3, column=3, padx=(0, 10))
entry_d.config(fg="red", bd=3, bg="#ffcccc")

label_e = tk.Label(root, text="E:", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10))
label_e.grid(row=3, column=4, sticky="e", padx=(10, 5))
entry_e = tk.Entry(root)
entry_e.grid(row=3, column=5, padx=(0, 10))
entry_e.config(fg="purple", bd=3, bg="#ebd8ff")

# Treeview widget for displaying results
treeview = ttk.Treeview(root, columns=("Gsk", "Ph"), show="headings")
treeview.heading("Gsk", text="Gsk")
treeview.heading("Ph", text="Ph")
treeview.grid(row=4, column=0, columnspan=6, padx=10, pady=(20, 10), sticky="nsew")

style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#000000", font=('Helvetica', 10))
style.map("Treeview", background=[("selected", "#0078D7")], foreground=[("selected", "#ffffff")])

# Feedback label for errors and status updates
feedback_label = tk.Label(root, text="", padx=5, pady=5, bg="#f0f0f0", font=('Helvetica', 10), fg="red")
feedback_label.grid(row=5, column=0, columnspan=6)

# Configure column weights for resizing
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_rowconfigure(4, weight=1)

# Bind the function to the KeyRelease event of entry widgets
entry_target_avg.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_total_points.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_m.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_d.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_e.bind("<KeyRelease>", update_grade_boundaries_on_entry)

# Assign default values and trigger the calculation
entry_target_avg.insert(0, "1.2")
entry_total_points.insert(0, "525")
entry_m.insert(0, "13")
entry_d.insert(0, "13")
entry_e.insert(0, "13")
update_grade_boundaries_on_entry()

root.mainloop()
