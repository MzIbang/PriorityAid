import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import priority_queue as pq

class PriorityAidApp:
    def __init__(self, root):
        self.root = root
        self.heap = []
        self.filename = 'data_pasien.json'
        
        self.editing_id = None 
        self.original_time = None
        
        self.setup_ui()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.load_data()
        self.refresh_queue()

    def setup_ui(self):
        left_frame = tk.Frame(self.root, padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(left_frame, text="PENDAFTARAN PASIEN", font=("Arial", 14, "bold")).pack(pady=10)    
        
        tk.Label(left_frame, text="Nama Pasien:").pack(anchor=tk.W)
        self.nama_entry = tk.Entry(left_frame, width=30)
        self.nama_entry.pack(pady=5)
        
        tk.Label(left_frame, text="Umur:").pack(anchor=tk.W)
        self.umur_entry = tk.Entry(left_frame, width=30)
        self.umur_entry.pack(pady=5)
        
        tk.Label(left_frame, text="Keluhan:").pack(anchor=tk.W)
        self.keluhan_text = tk.Text(left_frame, width=30, height=4)
        self.keluhan_text.pack(pady=5)
        
        tk.Label(left_frame, text="Prioritas:").pack(anchor=tk.W)
        self.prioritas_var = tk.StringVar(value="3")
        
        rb_frame = tk.Frame(left_frame)
        rb_frame.pack(anchor=tk.W, pady=5)
        
        options = [
            ("DARURAT (Prioritas 1)", "1", "#ffcccc"),
            ("MENDESAK (Prioritas 2)", "2", "#fff4cc"),
            ("NORMAL (Prioritas 3)", "3", "#ccffcc")
        ]
        
        for text, val, color in options:
            tk.Radiobutton(rb_frame, text=text, variable=self.prioritas_var,
                           value=val, bg=color, activebackground=color,
                           font=("Arial", 10), padx=10, pady=5).pack(anchor=tk.W, fill=tk.X, pady=2)

        self.submit_btn = tk.Button(left_frame, text="Tambah ke Antrian", command=self.process_patient, 
                                    bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), pady=10)
        self.submit_btn.pack(pady=20, fill=tk.X)

        self.cancel_edit_btn = tk.Button(left_frame, text="Batal Edit", command=self.clear_form,
                                         bg="#9E9E9E", fg="white", font=("Arial", 10))
        
        right_frame = tk.Frame(self.root, padx=20, pady=20)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="DAFTAR ANTRIAN", font=("Arial", 14, "bold")).pack(pady=10)
        
        tk.Button(right_frame, text="Panggil Pasien Selanjutnya", command=self.call_next, 
                  bg="#2196F3", fg="white", font=("Arial", 11, "bold"), pady=8).pack(pady=10, fill=tk.X)
        
        scrollbar = tk.Scrollbar(right_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.queue_listbox = tk.Listbox(right_frame, width=50, height=20, 
                                        yscrollcommand=scrollbar.set, font=("Courier", 10))
        self.queue_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.queue_listbox.yview)
        
        action_frame = tk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(action_frame, text="Edit Pasien", command=self.load_patient_to_edit, 
                  bg="#FF9800", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(action_frame, text="Hapus Pasien", command=self.delete_patient, 
                  bg="#f44336", fg="white", font=("Arial", 10)).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))

    def process_patient(self):
        """Menangani logika Tambah Baru ATAU Simpan Edit"""
        nama = self.nama_entry.get().strip()
        umur_str = self.umur_entry.get().strip()
        keluhan = self.keluhan_text.get("1.0", tk.END).strip()
        
        if not nama or not umur_str or not keluhan:
            messagebox.showwarning("ISI", "Datanya dilengkapi bos!")
            return
        
        try:
            umur = int(umur_str)
            if umur < 0: raise ValueError
        except ValueError:
            messagebox.showerror("ANGKA!", "Umur ya angka bos!")
            return
        
        if self.editing_id is not None:
            self.heap = [p for p in self.heap if p['id'] != self.editing_id]
            current_id = self.editing_id
            current_waktu = self.original_time
            msg_success = f"Data pasien {nama} berhasil diperbarui!"
        else:
            current_id = int(datetime.now().timestamp() * 100000)
            current_waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg_success = f"Pasien {nama} berhasil masuk antrian!"

        pasien = {
            'id': current_id,
            'nama': nama,
            'umur': umur,
            'keluhan': keluhan,
            'priority': int(self.prioritas_var.get()),
            'waktu': current_waktu
        }
        
        pq.enqueue(self.heap, pasien)
        
        self.save_data()
        self.refresh_queue()
        self.clear_form() 
        
        messagebox.showinfo("Sukses", msg_success)

    def load_patient_to_edit(self):
        selection = self.queue_listbox.curselection()
        if not selection:
            messagebox.showwarning("Pilih Pasien", "Pilih pasien yang ingin diedit!")
            return
        
        index = selection[0]
        all_patients = pq.get_all(self.heap)
        if index >= len(all_patients): return
        
        pasien = all_patients[index]
        
        self.editing_id = pasien['id']
        self.original_time = pasien['waktu']
        
        self.nama_entry.delete(0, tk.END)
        self.nama_entry.insert(0, pasien['nama'])
        
        self.umur_entry.delete(0, tk.END)
        self.umur_entry.insert(0, str(pasien['umur']))
        
        self.keluhan_text.delete("1.0", tk.END)
        self.keluhan_text.insert(tk.END, pasien['keluhan'])
        
        self.prioritas_var.set(str(pasien['priority']))
        
        self.submit_btn.config(text="Simpan Perubahan", bg="#FF9800")
        self.cancel_edit_btn.pack(pady=2, fill=tk.X)

    def clear_form(self):
        self.nama_entry.delete(0, tk.END)
        self.umur_entry.delete(0, tk.END)
        self.keluhan_text.delete("1.0", tk.END)
        self.prioritas_var.set("3")
        
        self.editing_id = None
        self.original_time = None
        
        self.submit_btn.config(text="Tambah ke Antrian", bg="#4CAF50")
        self.cancel_edit_btn.pack_forget()

    def on_closing(self):
        if messagebox.askokcancel("Keluar", "Apakah Anda yakin ingin keluar aplikasi?"):
            self.save_data()
            self.root.destroy()

    def call_next(self):
        if pq.is_empty(self.heap):
            messagebox.showinfo("Info", "Tidak ada pasien dalam antrian!")
            return
        
        pasien = pq.dequeue(self.heap)
        self.save_data()
        self.refresh_queue()
        
        info_text = (f"Nama: {pasien['nama']}\n"
                     f"Umur: {pasien['umur']} tahun\n"
                     f"Prioritas: {pasien['priority']}\n"
                     f"Keluhan: {pasien['keluhan']}")
        
        messagebox.showinfo("Panggil Pasien", f"Memanggil Pasien:\n\n{info_text}")

    def delete_patient(self):
        selection = self.queue_listbox.curselection()
        if not selection:
            messagebox.showwarning("Pilih Pasien", "Silakan pilih pasien dari daftar untuk dihapus.")
            return
        
        index = selection[0]
        all_patients_sorted = pq.get_all(self.heap)
        
        if index >= len(all_patients_sorted): return

        patient_to_delete = all_patients_sorted[index]
        
        if messagebox.askyesno("Konfirmasi Hapus", f"Yakin ingin menghapus pasien {patient_to_delete['nama']}?"):
            new_patients = [p for p in self.heap if p['id'] != patient_to_delete['id']]
            self.heap = []
            for p in new_patients:
                pq.enqueue(self.heap, p)
            
            self.save_data()
            self.refresh_queue()
            
            if self.editing_id == patient_to_delete['id']:
                self.clear_form()

    def refresh_queue(self):
        self.queue_listbox.delete(0, tk.END)
        all_patients = pq.get_all(self.heap)
        
        if not all_patients:
            self.queue_listbox.insert(tk.END, "[ Tidak ada pasien dalam antrian ]")
        else:
            for i, p in enumerate(all_patients, 1):
                priority_labels = {1: "DARURAT", 2: "MENDESAK", 3: "NORMAL"}
                label = priority_labels.get(p['priority'], "UNKNOWN")
                
                marker = ">>> NEXT <<<" if i == 1 else ""
                
                # Tidak ada lagi marker [EDITING] di sini sesuai permintaan
                line = f"#{i} | [{label}] {p['nama']} ({p['umur']}th) {marker}"
                self.queue_listbox.insert(tk.END, line)
                
                # Pewarnaan (Tanpa warna khusus Edit)
                bg_color, fg_color = "#ffffff", "#000000"
                
                if i == 1:
                    bg_color, fg_color = '#cce5ff', '#000099'
                elif p['priority'] == 1:
                    bg_color, fg_color = '#ffcccc', '#990000'
                elif p['priority'] == 2:
                    bg_color, fg_color = '#fff4cc', '#996600'
                else:
                    bg_color, fg_color = '#ccffcc', '#006600'
                
                self.queue_listbox.itemconfig(i-1, bg=bg_color, fg=fg_color)

    def save_data(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(pq.get_all(self.heap), f, indent=2)
        except Exception as e:
            print(f"Gagal menyimpan data: {e}")

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.heap = []
                for pasien in data:
                    pq.enqueue(self.heap, pasien)
        except FileNotFoundError:
            self.heap = []
        except json.JSONDecodeError:
            messagebox.showerror("Error Data", "File data korup. Memulai antrian baru.")
            self.heap = []

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PriorityAid: Sistem Antrian Medis")
    root.geometry("950x650")
    
    app = PriorityAidApp(root)
    
    root.mainloop()