import pandas as pd
import jsonlines
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# === GUI Setup ===
root = tk.Tk()
root.title("Phone Number & Email Enricher by Shaheer Ishfaq")
root.geometry("500x380")

status_top = tk.StringVar()
status_bottom = tk.StringVar()
status_top.set("Ready")
status_bottom.set("")

def log(top=None, bottom=None):
    if top is not None:
        status_top.set(top)
    if bottom is not None:
        status_bottom.set(bottom)
    root.update_idletasks()

def set_ui_state(active: bool):
    state = "normal" if active else "disabled"
    csv_entry.config(state=state)
    jsonl_entry.config(state=state)
    colname_entry.config(state=state)
    browse_csv_btn.config(state=state)
    browse_jsonl_btn.config(state=state)
    start_button.config(state=state)

def browse_csv():
    path = filedialog.askopenfilename(title="Select your CSV file", filetypes=[("CSV files", "*.csv")])
    if path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, path)

def browse_jsonl():
    path = filedialog.askopenfilename(title="Select JSONL index file", filetypes=[("JSONL files", "*.jsonl")])
    if path:
        jsonl_entry.delete(0, tk.END)
        jsonl_entry.insert(0, path)

def threaded_enrichment():
    csv_path = csv_entry.get().strip().strip('"')
    jsonl_path = jsonl_entry.get().strip().strip('"')
    col_name = colname_entry.get().strip()

    if not os.path.isfile(csv_path) or not os.path.isfile(jsonl_path):
        messagebox.showerror("Error", "One or both file paths are invalid.")
        set_ui_state(True)
        return
    if not col_name:
        messagebox.showerror("Error", "You must enter the LinkedIn ID column name.")
        set_ui_state(True)
        return

    output_path = os.path.splitext(csv_path)[0] + "_enriched.csv"

    try:
        log(top="📥 Reading CSV...", bottom="")
        df = pd.read_csv(csv_path)
        if col_name not in df.columns:
            messagebox.showerror("Error", f"Column '{col_name}' not found in CSV.")
            set_ui_state(True)
            return

        df[col_name] = df[col_name].astype(str).str.strip()
        total_rows = len(df)
        non_empty_ids = df[col_name].astype(bool).sum()
        empty_ids = total_rows - non_empty_ids
        target_ids = set(df[col_name])

        log(top=f"🎯 Found {non_empty_ids:,} LinkedIn IDs in your CSV ({empty_ids:,} empty rows)", bottom="")

        log(bottom="🔍 Scanning JSONL index...")
        mini_index = {}
        scanned = 0
        matched = 0
        CHUNK = 100_000

        with jsonlines.open(jsonl_path, mode='r') as reader:
            for record in reader:
                scanned += 1
                liid = record.get('liid', '').strip()
                if liid in target_ids:
                    mini_index[liid] = record
                    matched += 1

                if scanned % CHUNK == 0:
                    log(bottom=f"📦 Scanned {scanned:,} lines — Matched {matched:,} rows")

                if matched == non_empty_ids:
                    break

        log(bottom=f"✅ Match complete: {matched:,} / {non_empty_ids:,} IDs matched")

        def enrich_row(liid):
            rec = mini_index.get(liid)
            if not rec:
                return pd.Series({
                    'full_name': 'NOT FOUND',
                    'location': 'NOT FOUND',
                    'phones': 'NOT FOUND',
                    'emails': 'NOT FOUND',
                    'linkedin_url': 'NOT FOUND'
                })
            return pd.Series({
                'full_name': rec.get('n', ''),
                'location': rec.get('a', ''),
                'phones': ', '.join(rec.get('t', [])) if isinstance(rec.get('t'), list) else '',
                'emails': ', '.join(rec.get('e', [])) if isinstance(rec.get('e'), list) else '',
                'linkedin_url': rec.get('linkedin', '')
            })

        log(top="🛠️ Enriching rows...", bottom="")
        enriched = df[col_name].apply(enrich_row)
        final_df = pd.concat([df, enriched], axis=1)
        final_df.to_csv(output_path, index=False)
        log(top="✅ Done!", bottom=f"📁 File saved to: {output_path}")
        messagebox.showinfo("Success", f"Enrichment complete.\nFile saved to:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
        log(top="❌ Failed", bottom="")
    finally:
        set_ui_state(True)  # Re-enable UI at the end

def start_enrichment():
    set_ui_state(False)
    thread = threading.Thread(target=threaded_enrichment)
    thread.start()

# === GUI Layout ===

tk.Label(root, text="CSV File:").pack(pady=5)
csv_entry = tk.Entry(root, width=60)
csv_entry.pack()
browse_csv_btn = tk.Button(root, text="Browse CSV", command=browse_csv)
browse_csv_btn.pack(pady=2)

tk.Label(root, text="JSONL File:").pack(pady=5)
jsonl_entry = tk.Entry(root, width=60)
jsonl_entry.pack()
browse_jsonl_btn = tk.Button(root, text="Browse JSONL", command=browse_jsonl)
browse_jsonl_btn.pack(pady=2)

tk.Label(root, text="LinkedIn ID Column Name:").pack(pady=5)
colname_entry = tk.Entry(root, width=40)
colname_entry.pack()

start_button = tk.Button(root, text="Start Enrichment", command=start_enrichment)
start_button.pack(pady=10)

tk.Label(root, textvariable=status_top, fg="blue", wraplength=480, justify="center").pack(pady=5)
tk.Label(root, textvariable=status_bottom, fg="blue", wraplength=480, justify="center").pack(pady=0)

root.mainloop()