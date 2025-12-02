import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import priority_queue as pq

heap = []
root = None
nama_entry = None
umur_entry = None
keluhan_text = None
prioritas_var = None
queue_listbox = None

def create_widgets():
    global nama_entry, umur_entry, keluhan_text, prioritas_var, queue_listbox
    
    left_frame = tk.Frame(root, padx=20, pady=20)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    tk.Label(left_frame, text="PENDAFTARAN PASIEN", font=("Arial", 14, "bold")).pack(pady=10)    
    
    tk.Label(left_frame, text="Nama Pasien:").pack(anchor=tk.W)
    nama_entry = tk.Entry(left_frame, width=30)
    nama_entry.pack(pady=5)
    
    tk.Label(left_frame, text="Umur:").pack(anchor=tk.W)
    umur_entry = tk.Entry(left_frame, width=30)
    umur_entry.pack(pady=5)
    
    tk.Label(left_frame, text="Keluhan:").pack(anchor=tk.W)
    keluhan_text = tk.Text(left_frame, width=30, height=4)
    keluhan_text.pack(pady=5)
    
    tk.Label(left_frame, text="Prioritas:").pack(anchor=tk.W)
    prioritas_var = tk.StringVar(value="3")
    
    rb_frame = tk.Frame(left_frame)
    rb_frame.pack(anchor=tk.W, pady=5)
    
    rb1 = tk.Radiobutton(rb_frame, text="DARURAT (Prioritas 1)", variable=prioritas_var,
                         value="1", bg="#ffcccc", activebackground="#ffcccc", 
                         font=("Arial", 10, "bold"), padx=10, pady=5)
    rb1.pack(anchor=tk.W, fill=tk.X, pady=2)
    
    rb2 = tk.Radiobutton(rb_frame, text="MENDESAK (Prioritas 2)", variable=prioritas_var, 
                         value="2", bg="#fff4cc", activebackground="#fff4cc",
                         font=("Arial", 10), padx=10, pady=5)
    rb2.pack(anchor=tk.W, fill=tk.X, pady=2)
    
    rb3 = tk.Radiobutton(rb_frame, text="NORMAL (Prioritas 3)", variable=prioritas_var, 
                         value="3", bg="#ccffcc", activebackground="#ccffcc",
                         font=("Arial", 10), padx=10, pady=5)
    rb3.pack(anchor=tk.W, fill=tk.X, pady=2)
    
    tk.Button(left_frame, text="Tambah ke Antrian", command=add_patient, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), pady=10).pack(pady=20, fill=tk.X)
    
    right_frame = tk.Frame(root, padx=20, pady=20)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    tk.Label(right_frame, text="DAFTAR ANTRIAN", font=("Arial", 14, "bold")).pack(pady=10)
    
    tk.Button(right_frame, text="Panggil Pasien Selanjutnya", command=call_next, bg="#2196F3", fg="white", font=("Arial", 11, "bold"), pady=8).pack(pady=10, fill=tk.X)
    
    scrollbar = tk.Scrollbar(right_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    queue_listbox = tk.Listbox(right_frame, width=50, height=20, yscrollcommand=scrollbar.set, font=("Courier", 10))
    queue_listbox.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=queue_listbox.yview)
    
    tk.Button(right_frame, text="Hapus Pasien Terpilih", command=delete_patient, bg="#f44336", fg="white", font=("Arial", 10)).pack(pady=10, fill=tk.X)

def add_patient():
    global heap
    nama = nama_entry.get().strip()
    umur = umur_entry.get().strip()
    keluhan = keluhan_text.get("1.0", tk.END).strip()
    prioritas = int(prioritas_var.get())
    
    if not nama or not umur or not keluhan:
        messagebox.showwarning("ISI!", "Data dilengkapi bos!")
        return
    
    try:
        umur = int(umur)
    except:
        messagebox.showerror("ANGKA!", "Umur ya angka bos!")
        return
    
    pasien = {
        'id': int(datetime.now().timestamp() * 1000),
        'nama': nama,
        'umur': umur,
        'keluhan': keluhan,
        'priority': prioritas,
        'waktu': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    pq.enqueue(heap, pasien)
    save_data()
    refresh_queue()
    
    nama_entry.delete(0, tk.END)
    umur_entry.delete(0, tk.END)
    keluhan_text.delete("1.0", tk.END)
    prioritas_var.set("3")
    
    messagebox.showinfo("Sukses", f"Pasien {nama} berhasil ditambahkan!")

def call_next():
    global heap
    if pq.is_empty(heap):
        messagebox.showinfo("Info", "Tidak ada pasien dalam antrian!")
        return
    
    pasien = pq.dequeue(heap)
    save_data()
    refresh_queue()
    
    messagebox.showinfo("Panggil Pasien", f"Memanggil:\n\nNama: {pasien['nama']}\nUmur: {pasien['umur']} tahun\nKeluhan: {pasien['keluhan']}")

def delete_patient():
    global heap
    selection = queue_listbox.curselection()
    if not selection:
        messagebox.showwarning("Maksud?", "Pilih pasien yang ingin dihapus dulu!")
        return
    
    index = selection[0]
    all_patients = pq.get_all(heap)
    patient_to_delete = all_patients[index]
    
    if messagebox.askyesno("Konfirmasi", f"Hapus pasien {patient_to_delete['nama']}?"):
        new_patients = [p for p in all_patients if p['id'] != patient_to_delete['id']]
        heap.clear()
        for p in new_patients:
            pq.enqueue(heap, p)
        
        save_data()
        refresh_queue()

def refresh_queue():
    queue_listbox.delete(0, tk.END)
    all_patients = pq.get_all(heap)
    
    if not all_patients:
        queue_listbox.insert(tk.END, "[ Tidak ada pasien dalam antrian ]")
    else:
        for i, p in enumerate(all_patients, 1):
            priority_label = {1: "[DARURAT]", 2: "[MENDESAK]", 3: "[NORMAL]"}
            status = ">>> SELANJUTNYA <<<" if i == 1 else ""
            line = f"#{i} | {p['nama']} ({p['umur']}th) | {priority_label[p['priority']]} {status}"
            
            queue_listbox.insert(tk.END, line)
            
            if i == 1:
                queue_listbox.itemconfig(i-1, bg='#cce5ff', fg='#000099', selectbackground='#99ccff')
            elif p['priority'] == 1:
                queue_listbox.itemconfig(i-1, bg='#ffcccc', fg='#990000', selectbackground='#ffaaaa')
            elif p['priority'] == 2:
                queue_listbox.itemconfig(i-1, bg='#fff4cc', fg='#996600', selectbackground='#ffe699')
            else:
                queue_listbox.itemconfig(i-1, bg='#ccffcc', fg='#006600', selectbackground='#aaffaa')

def save_data():
    try:
        with open('data_pasien.json', 'w') as f:
            json.dump(pq.get_all(heap), f, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

def load_data():
    global heap
    try:
        with open('data_pasien.json', 'r') as f:
            data = json.load(f)
            for pasien in data:
                pq.enqueue(heap, pasien)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error loading data: {e}")

root = tk.Tk()
root.title("PriorityAid: Sistem Antrian Pasien dengan Priority Queue")
root.geometry("900x600")

load_data()
create_widgets()
refresh_queue()

root.mainloop()