import tkinter as tk
from tkinter import ttk
import csv
import locale
import os

def get_csv_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
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

def validate_inputs(target_avg, total_points, mp1, mp2, m, d, e, mode):
    errors = []
    try:
        locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
        target_avg = locale.atof(target_avg)
        total_points = locale.atof(total_points)

        if not (1.0 <= target_avg <= 4.0):
            errors.append("Zielnotendurchschnitt muss zwischen 1.0 und 4.0 liegen.")
        if not (0 <= total_points <= 600):
            errors.append("Gesamtpunktzahl muss zwischen 0 und 600 liegen.")

        if mode == 'mp':
            mp1 = locale.atof(mp1)
            mp2 = locale.atof(mp2)
            if not (0 <= mp1 <= 15):
                errors.append("MP1 muss zwischen 0 und 15 liegen.")
            if not (0 <= mp2 <= 15):
                errors.append("MP2 muss zwischen 0 und 15 liegen.")
        elif mode == 'mde':
            m = locale.atof(m)
            d = locale.atof(d)
            e = locale.atof(e)
            if not (0 <= m <= 15):
                errors.append("M muss zwischen 0 und 15 liegen.")
            if not (0 <= d <= 15):
                errors.append("D muss zwischen 0 und 15 liegen.")
            if not (0 <= e <= 15):
                errors.append("E muss zwischen 0 und 15 liegen.")
    except ValueError:
        errors.append("Fehlerhafte Eingaben. Bitte überprüfen.")
    return errors

def calculate_values_from_mp(mp1, mp2, target_avg, total_points):
    f, g = get_grade_boundaries(target_avg)
    if f is None or g is None:
        return [], None, None

    result_triples = []
    for m in range(16):
        for d in range(16):
            for e in range(16):
                if (f - total_points - 4 * (mp1 + mp2)) <= 4 * (m + d + e) < (g - total_points - 4 * (mp1 + mp2)):
                    result_triples.append((m, d, e))
    return result_triples, f, g

def calculate_values_from_mde(m, d, e, target_avg, total_points):
    f, g = get_grade_boundaries(target_avg)
    if f is None or g is None:
        return [], None, None

    required_mp1_mp2_sum_lower = (f - total_points) / 4 - (m + d + e)
    required_mp1_mp2_sum_upper = (g - total_points) / 4 - (m + d + e)

    result_pairs = []
    for mp1 in range(16):
        for mp2 in range(16):
            if required_mp1_mp2_sum_lower <= (mp1 + mp2) < required_mp1_mp2_sum_upper:
                result_pairs.append((mp1, mp2))
    return result_pairs, f, g

def update_table(result_list):
    for row in treeview.get_children():
        treeview.delete(row)

    if not result_list:
        return

    for index, values in enumerate(result_list):
        bg_color = "#E0E0E0" if index % 2 == 0 else "#F0F0F0"
        treeview.insert("", index, values=values, tags=('evenrow' if index % 2 == 0 else 'oddrow'))

    treeview.tag_configure('evenrow', background="#E0E0E0")
    treeview.tag_configure('oddrow', background="#F0F0F0")

    treeview.column("#1", anchor="center")
    treeview.column("#2", anchor="center")
    treeview.column("#3", anchor="center")

def update_grade_boundaries(f, g):
    label_lower_bound.config(text=f"Untergrenze: {f}" if f is not None else "Untergrenze: N/A")
    label_upper_bound.config(text=f"Obergrenze: {g}" if g is not None else "Obergrenze: N/A")

def update_grade_boundaries_on_entry(*args):
    target_avg = entry_target_avg.get()
    total_points = entry_total_points.get()

    if mode == 'mp':
        mp1 = entry_mp1.get()
        mp2 = entry_mp2.get()
        m, d, e = 0, 0, 0
    else:
        mp1, mp2 = 0, 0
        m = entry_m.get()
        d = entry_d.get()
        e = entry_e.get()

    errors = validate_inputs(target_avg, total_points, mp1, mp2, m, d, e, mode)
    if errors:
        feedback_label.config(text="\n".join(errors), fg="red")
        update_table([]) 
        update_grade_boundaries(None, None)
        return
    else:
        feedback_label.config(text="Notengrenzen aktualisiert.", fg="green")

    if target_avg and total_points:
        try:
            locale.setlocale(locale.LC_NUMERIC, 'en_US.UTF-8')
            target_avg = locale.atof(target_avg)
            total_points = locale.atof(total_points)

            if mode == 'mp':
                mp1 = locale.atof(mp1)
                mp2 = locale.atof(mp2)
                result_list, f, g = calculate_values_from_mp(mp1, mp2, target_avg, total_points)
                treeview.heading("#1", text="M", command=lambda: sort_table("M"))
                treeview.heading("#2", text="D", command=lambda: sort_table("D"))
                treeview.heading("#3", text="E", command=lambda: sort_table("E"))
            else:
                m = locale.atof(m)
                d = locale.atof(d)
                e = locale.atof(e)
                result_list, f, g = calculate_values_from_mde(m, d, e, target_avg, total_points)
                treeview.heading("#1", text="MP1", command=lambda: sort_table("MP1"))
                treeview.heading("#2", text="MP2", command=lambda: sort_table("MP2"))
                treeview.heading("#3", text="", command=lambda: sort_table(""))

            if f is None or g is None:
                feedback_label.config(text="Fehler: Umrechnungstabelle.csv fehlt oder Zielnotendurchschnitt nicht gefunden.", fg="red")
            else:
                feedback_label.config(text="Notengrenzen aktualisiert.", fg="green")

            update_grade_boundaries(f, g)
            update_table(result_list)

        except ValueError:
            feedback_label.config(text="Fehlerhafte Eingaben. Bitte überprüfen.", fg="red")
    else:
        update_table([]) 
        feedback_label.config(text="Bitte alle Felder ausfüllen.", fg="red")

def toggle_mode():
    global mode
    if mode == 'mp':
        mode = 'mde'
        btn_toggle_mode.config(text="Wechseln zu MP1 und MP2 Eingabe")
        label_mp1.grid_remove()
        entry_mp1.grid_remove()
        label_mp2.grid_remove()
        entry_mp2.grid_remove()
        label_m.grid()
        entry_m.grid()
        label_d.grid()
        entry_d.grid()
        label_e.grid()
        entry_e.grid()
    else:
        mode = 'mp'
        btn_toggle_mode.config(text="Wechseln zu M, D und E Eingabe")
        label_m.grid_remove()
        entry_m.grid_remove()
        label_d.grid_remove()
        entry_d.grid_remove()
        label_e.grid_remove()
        entry_e.grid_remove()
        label_mp1.grid()
        entry_mp1.grid()
        label_mp2.grid()
        entry_mp2.grid()
    update_grade_boundaries_on_entry()

def sort_table(column):
    global ascending
    items = list(treeview.get_children())
    items.sort(key=lambda item: int(treeview.set(item, column)), reverse=not ascending)
    for index, item in enumerate(items):
        treeview.move(item, '', index)
    ascending = not ascending

root = tk.Tk()
root.title("Abiturnoterechner")
root.geometry("850x450")
root.configure(bg="#f0f0f0")

heading_label = tk.Label(root, text="Abiturnoterechner", font=("Helvetica", 16), bg="#f0f0f0")
heading_label.grid(row=0, column=0, columnspan=6, pady=10)

mode = 'mp'
ascending = True

btn_toggle_mode = tk.Button(root, text="Wechseln zu M, D und E Eingabe", command=toggle_mode, bg="#0078D7", fg="white", font=("Helvetica", 10, "bold"))
btn_toggle_mode.grid(row=1, column=0, columnspan=6, pady=10)

label_target_avg = tk.Label(root, text="Zielnotendurchschnitt:", padx=5, pady=5, bg="#f0f0f0")
label_target_avg.grid(row=2, column=0, sticky="e", padx=(10, 5))
entry_target_avg = tk.Entry(root)
entry_target_avg.grid(row=2, column=1, padx=(0, 10))

label_total_points = tk.Label(root, text="Gesamtpunkte:", padx=5, pady=5, bg="#f0f0f0")
label_total_points.grid(row=2, column=2, sticky="e", padx=(10, 5))
entry_total_points = tk.Entry(root)
entry_total_points.grid(row=2, column=3, padx=(0, 10))

label_mp1 = tk.Label(root, text="MP1:", padx=5, pady=5, bg="#f0f0f0")
label_mp1.grid(row=3, column=0, sticky="e", padx=(10, 5))
entry_mp1 = tk.Entry(root)
entry_mp1.grid(row=3, column=1, padx=(0, 10))

label_mp2 = tk.Label(root, text="MP2:", padx=5, pady=5, bg="#f0f0f0")
label_mp2.grid(row=3, column=2, sticky="e", padx=(10, 5))
entry_mp2 = tk.Entry(root)
entry_mp2.grid(row=3, column=3, padx=(0, 10))

label_m = tk.Label(root, text="M:", padx=5, pady=5, bg="#f0f0f0")
label_m.grid(row=3, column=0, sticky="e", padx=(10, 5))
entry_m = tk.Entry(root)
entry_m.grid(row=3, column=1, padx=(0, 10))

label_d = tk.Label(root, text="D:", padx=5, pady=5, bg="#f0f0f0")
label_d.grid(row=3, column=2, sticky="e", padx=(10, 5))
entry_d = tk.Entry(root)
entry_d.grid(row=3, column=3, padx=(0, 10))

label_e = tk.Label(root, text="E:", padx=5, pady=5, bg="#f0f0f0")
label_e.grid(row=3, column=4, sticky="e", padx=(10, 5))
entry_e = tk.Entry(root)
entry_e.grid(row=3, column=5, padx=(0, 10))

label_m.grid_remove()
entry_m.grid_remove()
label_d.grid_remove()
entry_d.grid_remove()
label_e.grid_remove()
entry_e.grid_remove()

treeview = ttk.Treeview(root, columns=("M", "D", "E"), show="headings")
treeview.heading("M", text="M", command=lambda: sort_table("M"))
treeview.heading("D", text="D", command=lambda: sort_table("D"))
treeview.heading("E", text="E", command=lambda: sort_table("E"))

treeview.grid(row=4, column=0, columnspan=6, padx=10, pady=(20, 10), sticky="nsew")

style = ttk.Style()
style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#000000", font=('Helvetica', 10))
style.map("Treeview", background=[("selected", "#0078D7")], foreground=[("selected", "#ffffff")])

label_lower_bound = tk.Label(root, text="Untergrenze: N/A", padx=5, pady=5, bg="#f0f0f0")
label_lower_bound.grid(row=5, column=0, columnspan=3, sticky="w", padx=10)

label_upper_bound = tk.Label(root, text="Obergrenze: N/A", padx=5, pady=5, bg="#f0f0f0")
label_upper_bound.grid(row=5, column=3, columnspan=3, sticky="e", padx=10)

feedback_label = tk.Label(root, text="", padx=5, pady=5, bg="#f0f0f0", fg="red")
feedback_label.grid(row=6, column=0, columnspan=6)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)
root.grid_columnconfigure(5, weight=1)
root.grid_rowconfigure(4, weight=1)

entry_target_avg.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_total_points.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_mp1.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_mp2.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_m.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_d.bind("<KeyRelease>", update_grade_boundaries_on_entry)
entry_e.bind("<KeyRelease>", update_grade_boundaries_on_entry)

entry_target_avg.insert(0, "1.2")
entry_total_points.insert(0, "525")
entry_mp1.insert(0, "13")
entry_mp2.insert(0, "13")
entry_m.insert(0, "13")
entry_d.insert(0, "13")
entry_e.insert(0, "13")
update_grade_boundaries_on_entry()

root.mainloop()
