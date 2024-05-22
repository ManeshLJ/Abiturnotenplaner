import tkinter as tk
from tkinter import ttk
import csv
import locale
import os

def get_csv_path():
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to the CSV file relative to the script directory
    csv_path = os.path.join(script_dir, 'Umrechnungstabelle.csv')
    return csv_path

def get_grade_boundaries(target_avg):
    csv_path = get_csv_path()
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

def validate_inputs(target_avg, total_points, mp1, mp2):
    errors = []
    try:
        # Set locale to US to handle period as decimal separator
        locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
        target_avg = locale.atof(target_avg)
        total_points = locale.atof(total_points)
        mp1 = locale.atof(mp1)
        mp2 = locale.atof(mp2)

        if not (1.0 <= target_avg <= 4.0):
            errors.append("Zielnotendurchschnitt muss zwischen 1.0 und 4.0 liegen.")
        if not (0 <= total_points <= 600):
            errors.append("Gesamtpunktzahl muss zwischen 0 und 600 liegen.")
        if not (0 <= mp1 <= 15):
            errors.append("MP1 muss zwischen 0 und 15 liegen.")
        if not (0 <= mp2 <= 15):
            errors.append("MP2 muss zwischen 0 und 15 liegen.")
    except ValueError:
        errors.append("Fehlerhafte Eingaben. Bitte überprüfen.")
    return errors

def calculate_values(mp1, mp2, target_avg, total_points):
    print("Debug: calculate_values - Inputs received:")
    print("mp1:", mp1)
    print("mp2:", mp2)
    print("target_avg:", target_avg)
    print("total_points:", total_points)

    f, g = get_grade_boundaries(target_avg)
    if f is None or g is None:
        print("Debug: calculate_values - Invalid grade boundaries")
        return [], None, None

    try:
        result_triples = []
        for m in range(16):
            for d in range(16):
                for e in range(16):
                    if (f - total_points - 4 * (mp1 + mp2)) <= 4 * (m + d + e) < (g - total_points - 4 * (mp1 + mp2)):
                        lower_bound = total_points - 4 * (m + d + e)
                        upper_bound = total_points - 4 * (m + d + e - 1)
                        if lower_bound <= 0:
                            lower_bound = 0
                        result_triples.append((m, d, e))
        print("Debug: calculate_values - result_triples:", result_triples)
        return result_triples, f, g
    except ValueError:
        print("Debug: calculate_values - ValueError occurred")
        return [], None, None

def update_table(result_triples):
    print("Debug: update_table - result_triples:", result_triples)

    for row in treeview.get_children():
        treeview.delete(row)

    if not result_triples:
        print("Debug: update_table - No result_triples provided")
        return

    for index, (m, d, e) in enumerate(result_triples):
        print("Debug: update_table - Inserting value triple - M =", m, ", D =", d, ", E =", e)
        if index % 2 == 0:
            bg_color = "#E0E0E0"  # Light grey for even rows
        else:
            bg_color = "#F0F0F0"  # Slightly lighter grey for odd rows
        treeview.insert("", index, values=(m, d, e), tags=('evenrow' if index % 2 == 0 else 'oddrow'))

    treeview.tag_configure('evenrow', background="#E0E0E0")
    treeview.tag_configure('oddrow', background="#F0F0F0")

    treeview.column("#1", anchor="center")  # Center-align M column
    treeview.column("#2", anchor="center")  # Center-align D column
    treeview.column("#3", anchor="center")  # Center-align E column

    print("Debug: update_table - Table updated")

def update_grade_boundaries(f, g):
    label_lower_bound.config(text=f"Untergrenze: {f}" if f is not None else "Untergrenze: N/A")
    label_upper_bound.config(text=f"Obergrenze: {g}" if g is not None else "Obergrenze: N/A")

def update_grade_boundaries_on_entry(*args):
    target_avg = entry_target_avg.get()
    total_points = entry_total_points.get()
    mp1 = entry_mp1.get()
    mp2 = entry_mp2.get()

    errors = validate_inputs(target_avg, total_points, mp1, mp2)
    if errors:
        feedback_label.config(text="\n".join(errors), fg="red")
        update_table([])  # Clear the table if inputs are invalid
        update_grade_boundaries(None, None)
        return
    else:
        feedback_label.config(text="Notengrenzen aktualisiert.", fg="green")

    if target_avg and total_points and mp1 and mp2:
        try:
            locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
            target_avg = locale.atof(target_avg)
            total_points = locale.atof(total_points)
            mp1 = locale.atof(mp1)
            mp2 = locale.atof(mp2)

            result_triples, f, g = calculate_values(mp1, mp2, target_avg, total_points)

            if f is None or g is None:
                feedback_label.config(text="Fehler: Umrechnungstabelle.csv fehlt oder Zielnotendurchschnitt nicht gefunden.", fg="red")
            else:
                feedback_label.config(text="Notengrenzen aktualisiert.", fg="green")

            update_grade_boundaries(f, g)
            update_table(result_triples)

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
root.geometry("850x450")

# Set background color to light grey for the whole GUI
root.configure(bg="#f0f0f0")

# Heading label
heading_label = tk.Label(root, text="Abiturnoterechner", font=("Helvetica", 20, "bold"), bg="#f0f0f0", fg="#333333")
heading_label.grid(row=0, column=0, columnspan=6, pady=(10, 20))

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0", foreground="#000000")
style.map('Treeview', background=[('selected', '#FFD700')], foreground=[('selected', '#000000')])

# Label and Entry widgets for target average
label_target_avg = tk.Label(root, text="Zielnotendurchschnitt (1.0-4.0):", padx=5, pady=5, bg="#f0f0f0")
label_target_avg.grid(row=1, column=0, sticky="e", padx=(10, 5))
entry_target_avg = tk.Entry(root)
entry_target_avg.grid(row=1, column=1, padx=(0, 10))

# Label widgets for grade boundaries
label_lower_bound = tk.Label(root, text="Untergrenze:", padx=5, pady=5, bg="#f0f0f0")
label_lower_bound.grid(row=1, column=2)

label_upper_bound = tk.Label(root, text="Obergrenze:", padx=5, pady=5, bg="#f0f0f0")
label_upper_bound.grid(row=1, column=3)

# Label and Entry widgets for total points
label_total_points = tk.Label(root, text="Gesamtpunktzahl Qualifikationsphase (0-600):", padx=5, pady=5, bg="#f0f0f0")
label_total_points.grid(row=2, column=0, sticky="e", padx=(10, 5))
entry_total_points = tk.Entry(root)
entry_total_points.grid(row=2, column=1, padx=(0, 10))

# Label and Entry widgets for MP1 and MP2
label_mp1 = tk.Label(root, text="MP1:", padx=5, pady=5, bg="#f0f0f0")
label_mp1.grid(row=3, column=0, sticky="e", padx=(10, 5))
entry_mp1 = tk.Entry(root, fg="blue", bg="#cce5ff")
entry_mp1.grid(row=3, column=1, padx=(0, 10))

label_mp2 = tk.Label(root, text="MP2:", padx=5, pady=5, bg="#f0f0f0")
label_mp2.grid(row=3, column=2, sticky="e", padx=(10, 5))
entry_mp2 = tk.Entry(root, fg="red", bg="#ffcccc")
entry_mp2.grid(row=3, column=3, padx=(0, 10))

# Treeview widget for displaying results
treeview = ttk.Treeview(root, columns=("M", "D", "E"), show="headings")
treeview.heading("M", text="M")
treeview.heading("D", text="D")
treeview.heading("E", text="E")

treeview.grid(row=4, column=0, columnspan=6, padx=10, pady=(20, 10), sticky="nsew")

style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#000000", font=('Helvetica', 10))
style.map("Treeview", background=[("selected", "#0078D7")], foreground=[("selected", "#ffffff")])

# Feedback label for errors and status updates
feedback_label = tk.Label(root, text="", padx=5, pady=5, bg="#f0f0f0", fg="red")
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
entry_mp1.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_mp2.bind("<KeyRelease>", update_grade_boundaries_on_entry)

# Assign default values and trigger the calculation
entry_target_avg.insert(0, "1.2")
entry_total_points.insert(0, "525")
entry_mp1.insert(0, "8")
entry_mp2.insert(0, "7")
update_grade_boundaries_on_entry()

root.mainloop()
