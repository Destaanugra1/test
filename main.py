import tkinter as tk
from tkinter import ttk, messagebox
import json, os

DATA_FILE = "data.json"

class Buku:      # Model sederhana, langsung pakai __init__ default
    def __init__(self, judul, pengarang, id_buku, dipinjam=False):
        self.id, self.judul, self.pengarang, self.dipinjam = id_buku, judul, pengarang, dipinjam

class Anggota:
    def __init__(self, id_anggota, nama):
        self.id, self.nama = id_anggota, nama

class Transaksi:
    def __init__(self, anggota, buku):
        self.anggota, self.buku = anggota, buku

class PerpustakaanApp:
    def __init__(self, root):
        self.root = root; self.root.title("Manajemen Perpustakaan Mini")
        self.buku_list, self.anggota_list, self.transaksi_list = [], [], []
        self.setup_ui(); self.load_data()

    def setup_ui(self):
        frame_input = tk.Frame(self.root); frame_input.pack(padx=10, pady=10, fill='x')
        # Input Buku
        self.entry_idbuku, self.entry_judul, self.entry_pengarang = (tk.Entry(), tk.Entry(), tk.Entry())
        self.buat_input(frame_input, "Tambah Buku", [("ID Buku", self.entry_idbuku), ("Judul", self.entry_judul), ("Pengarang", self.entry_pengarang)], self.tambah_buku, 0)
        # Input Anggota
        self.entry_idanggota, self.entry_namaanggota = tk.Entry(), tk.Entry()
        self.buat_input(frame_input, "Tambah Anggota", [("ID", self.entry_idanggota), ("Nama", self.entry_namaanggota)], self.tambah_anggota, 1)
        # Transaksi
        self.entry_idanggota_trans, self.entry_idbuku_trans = tk.Entry(), tk.Entry()
        self.buat_transaksi(frame_input, 2)
        # Output
        frame_output = tk.Frame(self.root); frame_output.pack(padx=10, pady=10, fill='both', expand=True)
        self.tree_buku = self.buat_treeview(frame_output, "Daftar Buku", ["ID", "Judul", "Pengarang", "Status"])
        self.tree_anggota = self.buat_treeview(frame_output, "Daftar Anggota", ["ID", "Nama"])
        self.tree_trans = self.buat_treeview(frame_output, "Daftar Transaksi", ["ID Anggota", "Nama", "Judul Buku"])

    def buat_input(self, parent, judul, fields, cmd, col):
        frame = tk.LabelFrame(parent, text=judul); frame.grid(row=0, column=col, padx=5)
        for i, (lbl, ent) in enumerate(fields):
            tk.Label(frame, text=lbl).grid(row=i, column=0); ent.grid(row=i, column=1)
        tk.Button(frame, text="Tambah", command=cmd).grid(row=len(fields), columnspan=2, pady=5)

    def buat_transaksi(self, parent, col):
        frame = tk.LabelFrame(parent, text="Transaksi"); frame.grid(row=0, column=col, padx=5)
        for i, (lbl, ent) in enumerate([("ID Anggota", self.entry_idanggota_trans), ("ID Buku", self.entry_idbuku_trans)]):
            tk.Label(frame, text=lbl).grid(row=i, column=0); ent.grid(row=i, column=1)
        tk.Button(frame, text="Pinjam", command=self.pinjam_buku).grid(row=2, column=0, pady=5)
        tk.Button(frame, text="Kembalikan", command=self.kembalikan_buku).grid(row=2, column=1, pady=5)

    def buat_treeview(self, parent, title, kolom):
        tk.Label(parent, text=title, font=('Arial', 10, 'bold')).pack()
        frame = tk.Frame(parent); frame.pack(fill='x', pady=5)
        scrollbar = ttk.Scrollbar(frame, orient="vertical")
        tree = ttk.Treeview(frame, columns=kolom, show="headings", height=5, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview); scrollbar.pack(side="right", fill="y")
        for k in kolom:
            tree.heading(k, text=k); tree.column(k, anchor='center')
        tree.pack(side="left", fill='x', expand=True); return tree

    def tambah_buku(self):
        id_buku, judul, pengarang = self.entry_idbuku.get().strip(), self.entry_judul.get().strip(), self.entry_pengarang.get().strip()
        if not id_buku or not judul or not pengarang:
            messagebox.showwarning("Input Error", "Lengkapi data buku!"); return
        if any(b.id == id_buku for b in self.buku_list):
            messagebox.showwarning("Error", "ID buku sudah ada."); return
        self.buku_list.append(Buku(judul, pengarang, id_buku))
        self.refresh_tree_buku_status()
        [e.delete(0, tk.END) for e in [self.entry_idbuku, self.entry_judul, self.entry_pengarang]]
        self.simpan_data()

    def tambah_anggota(self):
        id_, nama = self.entry_idanggota.get().strip(), self.entry_namaanggota.get().strip()
        if not id_ or not nama:
            messagebox.showwarning("Input Error", "Lengkapi data anggota!"); return
        if any(a.id == id_ for a in self.anggota_list):
            messagebox.showwarning("Error", "ID anggota sudah ada."); return
        anggota = Anggota(id_, nama); self.anggota_list.append(anggota)
        self.tree_anggota.insert("", "end", values=(anggota.id, anggota.nama))
        [e.delete(0, tk.END) for e in [self.entry_idanggota, self.entry_namaanggota]]
        self.simpan_data()

    def pinjam_buku(self):
        id_anggota, id_buku = self.entry_idanggota_trans.get().strip(), self.entry_idbuku_trans.get().strip()
        anggota = next((a for a in self.anggota_list if a.id == id_anggota), None)
        buku = next((b for b in self.buku_list if b.id == id_buku), None)
        if not anggota or not buku:
            messagebox.showerror("Error", "Anggota atau buku tidak ditemukan."); return
        if buku.dipinjam:
            messagebox.showerror("Error", "Buku sedang dipinjam."); return
        transaksi = Transaksi(anggota, buku)
        self.transaksi_list.append(transaksi); buku.dipinjam = True
        self.tree_trans.insert("", "end", values=(anggota.id, anggota.nama, buku.judul))
        self.refresh_tree_buku_status()
        [e.delete(0, tk.END) for e in [self.entry_idanggota_trans, self.entry_idbuku_trans]]
        self.simpan_data()

    def kembalikan_buku(self):
        id_anggota, id_buku = self.entry_idanggota_trans.get().strip(), self.entry_idbuku_trans.get().strip()
        transaksi = next((t for t in self.transaksi_list if t.anggota.id == id_anggota and t.buku.id == id_buku), None)
        if not transaksi:
            messagebox.showerror("Error", "Transaksi tidak ditemukan."); return
        transaksi.buku.dipinjam = False; self.transaksi_list.remove(transaksi)
        for item in self.tree_trans.get_children():
            vals = self.tree_trans.item(item)['values']
            if vals[0] == id_anggota and vals[2] == transaksi.buku.judul:
                self.tree_trans.delete(item); break
        self.refresh_tree_buku_status()
        [e.delete(0, tk.END) for e in [self.entry_idanggota_trans, self.entry_idbuku_trans]]
        self.simpan_data()

    def refresh_tree_buku_status(self):
        self.tree_buku.delete(*self.tree_buku.get_children())
        for buku in self.buku_list:
            status = "Dipinjam" if buku.dipinjam else "Tersedia"
            self.tree_buku.insert("", "end", values=(buku.id, buku.judul, buku.pengarang, status))

    def simpan_data(self):
        data = {
            "buku": [{"id": b.id, "judul": b.judul, "pengarang": b.pengarang, "dipinjam": b.dipinjam} for b in self.buku_list],
            "anggota": [{"id": a.id, "nama": a.nama} for a in self.anggota_list],
            "transaksi": [{"id_anggota": t.anggota.id, "id_buku": t.buku.id} for t in self.transaksi_list]
        }
        with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

    def load_data(self):
        if not os.path.exists(DATA_FILE): return
        with open(DATA_FILE) as f: data = json.load(f)
        for b in data.get("buku", []):
            self.buku_list.append(Buku(b["judul"], b["pengarang"], b["id"], b["dipinjam"]))
        for a in data.get("anggota", []):
            self.anggota_list.append(Anggota(a["id"], a["nama"]))
        for t in data.get("transaksi", []):
            anggota = next((a for a in self.anggota_list if a.id == t["id_anggota"]), None)
            buku = next((b for b in self.buku_list if b.id == t["id_buku"]), None)
            if anggota and buku:
                self.transaksi_list.append(Transaksi(anggota, buku)); buku.dipinjam = True
        self.refresh_tree_buku_status()
        for a in self.anggota_list:
            self.tree_anggota.insert("", "end", values=(a.id, a.nama))
        for t in self.transaksi_list:
            self.tree_trans.insert("", "end", values=(t.anggota.id, t.anggota.nama, t.buku.judul))

if __name__ == "__main__":
    root = tk.Tk()
    PerpustakaanApp(root)
    root.mainloop()
