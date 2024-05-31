import sqlite3
from datetime import datetime
import random
import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox,ttk
from tkcalendar import Calendar
from ambil_data import *



# Fungsi untuk tambah tanaman
def tambah_tanaman(id_tree, input_window):
    if not id_tree.isdigit():
        messagebox.showerror("Error", "ID Tanaman harus berupa angka.")
        return

    id_tree = int(id_tree)
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    added_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO database (id_tree, latitude, longitude, added_timestamp) VALUES (?,?,?,?)',
                       (id_tree, latitude, longitude, added_timestamp))
        conn.commit()
        messagebox.showinfo("Tambah Tanaman", f"Tanaman dengan ID = {id_tree} berhasil ditambahkan")
        input_window.destroy()  # Tutup jendela input ID setelah berhasil menambahkan tanaman
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "ID Tanaman sudah ada.")
    finally:
        conn.close()

# Fungsi untuk menampilkan halaman input ID tanaman
def halaman_tambah_tanaman():
    # Buat window baru
    input_window = tk.Toplevel(root)
    input_window.title("Masukkan ID Tanaman")
    input_window.geometry("400x200")

    # Membaca gambar latar belakang
    background_image = tk.PhotoImage(file="background/bgneongr.png")

    # Menampilkan gambar latar belakang
    background_label = tk.Label(input_window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Anchor diatur ke "nw" (northwest)

    tk.Label(input_window, text="Masukkan ID Tanaman:", font=("Helvetica", 12)).pack(pady=10)

    entry_id_tree = tk.Entry(input_window, font=("Helvetica", 12))
    entry_id_tree.pack(pady=10)

    def lanjutkan():
        id_tree = entry_id_tree.get()
        tambah_tanaman(id_tree, input_window)

    tk.Button(input_window, text="Tambah", command=lanjutkan, font=("Helvetica", 12), bg="green", fg="white").pack(pady=10)

    # Memastikan gambar latar belakang tetap ada dengan menyimpannya dalam atribut window
    input_window.background = background_image
# Fungsi untuk menghapus tanaman
def hapus_tanaman(id_tree, input_window):
    if not id_tree.isdigit():
        messagebox.showerror("Error", "ID Tanaman harus berupa angka.")
        return

    id_tree = int(id_tree)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Cek apakah ID tanaman ada dalam database
    cursor.execute('SELECT COUNT(*) FROM database WHERE id_tree = ?', (id_tree,))
    result = cursor.fetchone()

    if result[0] == 0:
        messagebox.showerror("Error", "ID Tanaman tidak ditemukan.")
        conn.close()
        return

    cursor.execute('DELETE FROM sensor_data WHERE id_tree = ?', (id_tree,))
    cursor.execute('DELETE FROM database WHERE id_tree = ?', (id_tree,))
    conn.commit()
    conn.close()

    messagebox.showinfo("Hapus Tanaman", f"Tanaman dengan ID = {id_tree} dan semua data sensornya berhasil dihapus")
    input_window.destroy()  # Tutup jendela input ID setelah berhasil menghapus tanaman

# Fungsi untuk menampilkan halaman input ID tanaman yang akan dihapus
def halaman_hapus_tanaman():
    # Buat window baru
    input_window = tk.Toplevel(root)
    input_window.title("Hapus Tanaman")
    input_window.geometry("400x200")

    # Membaca gambar latar belakang
    background_image = tk.PhotoImage(file="background/bgneonpink.png")

    # Menampilkan gambar latar belakang
    background_label = tk.Label(input_window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Anchor diatur ke "nw" (northwest)

    tk.Label(input_window, text="Masukkan ID Tanaman yang akan dihapus:", font=("Helvetica", 12)).pack(pady=10)

    entry_id_tree = tk.Entry(input_window, font=("Helvetica", 12))
    entry_id_tree.pack(pady=10)

    def lanjutkan_hapus():
        id_tree = entry_id_tree.get()
        hapus_tanaman(id_tree, input_window)

    tk.Button(input_window, text="Hapus", command=lanjutkan_hapus, font=("Helvetica", 12), bg="red", fg="white").pack(pady=10)
    tk.Button(input_window, text="Kembali", command=input_window.destroy, font=("Helvetica", 12), bg="grey", fg="white").pack(pady=10)

    # Memastikan gambar latar belakang tetap ada dengan menyimpannya dalam atribut window
    input_window.background = background_image

# Fungsi tampilkan data sensor tanaman
def tampilkan_data(id_tree, label_data):
    if not id_tree.isdigit():
        messagebox.showerror("Error", "ID Tanaman harus berupa angka.")
        return

    id_tree = int(id_tree)

    label_sensor = {
        0: "Suhu udara (°C)",
        1: "Kelembaban udara (%)",
        2: "Curah hujan (mm)",
        3: "Tingkat sinar UV",
        4: "Suhu tanah (°C)",
        5: "Kelembaban tanah (%)",
        6: "pH tanah",
        7: "Kadar N dalam tanah (mg/kg)",
        8: "Kadar P dalam tanah (mg/kg)",
        9: "Kadar K dalam tanah (mg/kg)"
    }

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT sensor_type, nilai, MAX(timestamp)
    FROM sensor_data 
    WHERE id_tree = ?
    GROUP BY sensor_type
    ''', (id_tree,))

    data = cursor.fetchall()

    cursor.execute('SELECT latitude, longitude, added_timestamp FROM database WHERE id_tree = ?', (id_tree,))
    database_info = cursor.fetchone()
    conn.close()

    if not data:
        messagebox.showerror("Error", f"Tidak ada data sensor untuk tanaman dengan ID = {id_tree}")
        return

    latitude, longitude, added_timestamp = database_info if database_info else (None, None, None)

    # Mengumpulkan data untuk tabel
    table_data = [
        ["ID Tanaman", f"{id_tree}"],
        ["Lat,Lon", f"{latitude}, {longitude}"],
        ["Tanggal ID ditambahkan", format_timestamp(added_timestamp) if added_timestamp else "Tidak Tersedia"]
    ]

    # Menambahkan judul kolom untuk tabel
    table_data.append(["Sensor", "Nilai", "Waktu"])

    # Menambahkan data sensor ke dalam tabel
    for sensor_type, nilai, timestamp in data:
        table_data.append([label_sensor.get(sensor_type, f'Sensor {sensor_type}'), f"{nilai:.2f}", format_timestamp(timestamp)])

    # Hapus data lama jika ada
    for child in label_data.winfo_children():
        child.destroy()

    # Membuat tabel menggunakan ttk.Treeview
    table = ttk.Treeview(label_data, columns=("Sensor", "Nilai", "Waktu"), show="headings", height=len(table_data)) # Set height agar tabel tidak perlu di-scroll
    for col in table["columns"]:
        table.heading(col, text=col)

    # Menambahkan data ke dalam tabel
    for row in table_data:
        table.insert("", "end", values=row)

    table.pack(expand=True, fill="both", padx=10, pady=10)
    label_data.master.geometry("640x400")

# Fungsi untuk menampilkan halaman input ID tanaman
def halaman_input_id():
    # Buat window baru
    input_window = tk.Toplevel(root)
    input_window.title("Masukkan ID Tanaman")
    input_window.geometry("400x200")

    # Membaca gambar latar belakang
    background_image = tk.PhotoImage(file="background/bgneonppl.png")

    # Menampilkan gambar latar belakang
    background_label = tk.Label(input_window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Anchor diatur ke "nw" (northwest)

    tk.Label(input_window, text="Masukkan ID Tanaman:", font=("Helvetica", 12)).pack(pady=10)

    entry_id_tree = tk.Entry(input_window, font=("Helvetica", 12))
    entry_id_tree.pack(pady=10)

    def lanjutkan():
        id_tree = entry_id_tree.get()
        tampilkan_halaman_data(id_tree)
        input_window.destroy()

    tk.Button(input_window, text="Lanjutkan", command=lanjutkan, font=("Helvetica", 10), bg="#2ECC71", fg="white").pack(pady=10)

    # Memastikan gambar latar belakang tetap ada dengan menyimpannya dalam atribut window
    input_window.background = background_image

# Fungsi untuk menampilkan halaman data
def tampilkan_halaman_data(id_tree):
    # Buat window baru
    data_window = tk.Toplevel(root)
    data_window.title("Data Tanaman")
    data_window.geometry("610x400")

    label_data = tk.Label(data_window, text="", wraplength=400, justify="center", font=("Helvetica", 10))
    label_data.pack(pady=10)

    # Panggil fungsi untuk menampilkan data
    tampilkan_data(id_tree, label_data)

    tk.Button(data_window, text="Kembali ke Menu", command=data_window.destroy, font=("Helvetica", 10), bg="#A52A2A", fg="white").pack(pady=10)

# Fungsi untuk tampilkan semua data 
def tampilkan_semua_data():
    label_sensor = {
        0: "Suhu udara (°C)",
        1: "Kelembaban udara (%)",
        2: "Curah hujan (mm)",
        3: "Tingkat sinar UV",
        4: "Suhu tanah (°C)",
        5: "Kelembaban tanah (%)",
        6: "pH tanah",
        7: "Kadar N dalam tanah (mg/kg)",
        8: "Kadar P dalam tanah (mg/kg)",
        9: "Kadar K dalam tanah (mg/kg)"
    }

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id_tree, latitude, longitude, added_timestamp FROM database')
    data = cursor.fetchall()

    if not data:
        messagebox.showinfo("Tidak Ada Tanaman", "Tidak ada tanaman yang ditemukan di database.")
        return

    # Buat window baru untuk menampilkan data tanaman
    tampil_window = tk.Toplevel(root)
    tampil_window.title("Daftar Tanaman")
    tampil_window.geometry("800x600")

    # Buat Treeview
    tree = ttk.Treeview(tampil_window)
    tree["columns"] = ("latitude", "longitude", "added_timestamp")

    # Atur nama kolom
    tree.heading("#0", text="ID Tanaman")
    tree.heading("latitude", text="Latitude")
    tree.heading("longitude", text="Longitude")
    tree.heading("added_timestamp", text="Tanggal Ditambahkan")

    # Menambahkan data ke Treeview
    for tanaman in data:
        id_tree, latitude, longitude, added_timestamp = tanaman
        tree.insert("", tk.END, text=id_tree, values=(latitude, longitude, added_timestamp))

        # Ambil data sensor
        cursor.execute('''
        SELECT sensor_type, nilai, MAX(timestamp)
        FROM sensor_data
        WHERE id_tree = ?
        GROUP BY sensor_type
        ''', (id_tree,))
        sensor_data = cursor.fetchall()

        # Menambahkan data sensor ke dalam kolom terkait
        for sensor_type, nilai, timestamp in sensor_data:
            sensor_info = f"{label_sensor.get(sensor_type, f'Sensor {sensor_type}')}: {nilai:.2f}"
            tree.insert("", tk.END, text="", values=("", "", sensor_info))

    tree.pack(expand=True, fill=tk.BOTH)

    conn.close()

# Fungsi membuat grafik sensor
def grafik_sensor(id_tree, sensor_type, nama_sensor, waktu_mulai, waktu_akhir):
    data = ambil_data_sensor_untuk_grafik(id_tree, sensor_type, waktu_mulai, waktu_akhir)

    if not data:
        messagebox.showerror("Error", f"Tidak ada data untuk grafik ID tanaman = {id_tree}")
        return

    nilai, timestamps = zip(*data)
    timestamps = [datetime.strptime(ts, '%Y-%m-%d %H:%M:%S') for ts in timestamps]

    timestamps, nilai = interpolasi_data_hilang(timestamps, nilai, waktu_mulai, waktu_akhir)

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown']

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, nilai, marker='o', linestyle='-', label=nama_sensor, color=colors[sensor_type % len(colors)])
    plt.title(f'Grafik {nama_sensor} untuk ID Tanaman {id_tree}')
    plt.xlabel('Waktu')
    plt.ylabel(nama_sensor)

    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))

    plt.gcf().autofmt_xdate()
    plt.grid(True)

    plt.legend()
    plt.show()


# Fungsi opsi grafik yang ditampilkan
def tampilkan_opsi_grafik(id_tree):
    # Label untuk setiap jenis sensor
    label_sensor = {
        0: "Suhu udara (°C)",
        1: "Kelembaban udara (%)",
        2: "Curah hujan (mm)",
        3: "Tingkat sinar UV",
        4: "Suhu tanah (°C)",
        5: "Kelembaban tanah (%)",
        6: "pH tanah",
        7: "Kadar N dalam tanah (mg/kg)",
        8: "Kadar P dalam tanah (mg/kg)",
        9: "Kadar K dalam tanah (mg/kg)"
    }

    # Fungsi untuk memilih sensor dan menampilkan jendela memilih waktu
    def pilih_sensor(sensor_type):
        def submit():
            # Mendapatkan waktu mulai
            waktu_mulai_date = cal_waktu_mulai.get_date()
            waktu_mulai_time = f"{spin_hour.get().zfill(2)}:{spin_minute.get().zfill(2)}:{spin_second.get().zfill(2)}"
            waktu_mulai = f"{waktu_mulai_date} {waktu_mulai_time}"

            # Mendapatkan waktu selesai
            waktu_akhir_date = cal_waktu_akhir.get_date()
            waktu_akhir_time = f"{spin_hour_end.get().zfill(2)}:{spin_minute_end.get().zfill(2)}:{spin_second_end.get().zfill(2)}"
            waktu_akhir = f"{waktu_akhir_date} {waktu_akhir_time}"

            try:
                # Memeriksa apakah waktu telah diisi
                if waktu_mulai_date and waktu_mulai_time and waktu_akhir_date and waktu_akhir_time:
                    # Parsing waktu_mulai dan waktu_akhir
                    waktu_mulai = datetime.strptime(waktu_mulai, '%Y-%m-%d %H:%M:%S')
                    waktu_akhir = datetime.strptime(waktu_akhir, '%Y-%m-%d %H:%M:%S')

                    # Format waktu tanpa konversi zona waktu
                    waktu_mulai = waktu_mulai.strftime('%Y-%m-%d %H:%M:%S')
                    waktu_akhir = waktu_akhir.strftime('%Y-%m-%d %H:%M:%S')

                    # Memanggil fungsi untuk menampilkan grafik dengan parameter yang sesuai
                    grafik_sensor(id_tree, sensor_type, label_sensor[sensor_type], waktu_mulai, waktu_akhir)
                    window.destroy()  # Menutup jendela setelah grafik ditampilkan
                else:
                    messagebox.showerror("Error", "Waktu mulai dan waktu selesai harus diisi.")
            except ValueError as e:
                messagebox.showerror("Error", f"Format waktu salah: {e}")

        # Membuat jendela untuk memilih waktu
        window = tk.Toplevel(root)
        window.title(f"Pilih Waktu untuk {label_sensor[sensor_type]}")

        # Widget untuk memilih waktu mulai
        tk.Label(window, text="Waktu Mulai:").pack()
        cal_waktu_mulai = Calendar(window, date_pattern='yyyy-mm-dd')
        cal_waktu_mulai.pack()

        # Widget untuk memilih jam, menit, dan detik untuk waktu mulai
        waktu_mulai_time_frame = tk.Frame(window)
        waktu_mulai_time_frame.pack()
        spin_hour = tk.Spinbox(waktu_mulai_time_frame, from_=0, to=23, width=2, format="%02.0f")
        spin_hour.grid(row=0, column=0)
        tk.Label(waktu_mulai_time_frame, text=":").grid(row=0, column=1)
        spin_minute = tk.Spinbox(waktu_mulai_time_frame, from_=0, to=59, width=2, format="%02.0f")
        spin_minute.grid(row=0, column=2)
        tk.Label(waktu_mulai_time_frame, text=":").grid(row=0, column=3)
        spin_second = tk.Spinbox(waktu_mulai_time_frame, from_=0, to=59, width=2, format="%02.0f")
        spin_second.grid(row=0, column=4)

        # Widget untuk memilih waktu selesai
        tk.Label(window, text="Waktu Selesai:").pack()
        cal_waktu_akhir = Calendar(window, date_pattern='yyyy-mm-dd')
        cal_waktu_akhir.pack()

        # Widget untuk memilih jam, menit, dan detik untuk waktu selesai
        waktu_akhir_time_frame = tk.Frame(window)
        waktu_akhir_time_frame.pack()
        spin_hour_end = tk.Spinbox(waktu_akhir_time_frame, from_=0, to=23, width=2, format="%02.0f")
        spin_hour_end.grid(row=0, column=0)
        tk.Label(waktu_akhir_time_frame, text=":").grid(row=0, column=1)
        spin_minute_end = tk.Spinbox(waktu_akhir_time_frame, from_=0, to=59, width=2, format="%02.0f")
        spin_minute_end.grid(row=0, column=2)
        tk.Label(waktu_akhir_time_frame, text=":").grid(row=0, column=3)
        spin_second_end = tk.Spinbox(waktu_akhir_time_frame, from_=0, to=59, width=2, format="%02.0f")
        spin_second_end.grid(row=0, column=4)

        # Tombol submit untuk menampilkan grafik
        submit_button = tk.Button(window, text="Submit", command=submit)
        submit_button.pack()

    # Membuat jendela utama untuk memilih sensor
    window = tk.Toplevel(root)
    window.title("Pilih Sensor untuk Menampilkan Grafik")

    # Menampilkan tombol untuk setiap sensor dengan tata letak yang menarik
    above_frame = tk.Frame(window)
    above_frame.pack()
    below_frame = tk.Frame(window)
    below_frame.pack()
    
    above_sensor_types = list(label_sensor.keys())[:4]
    below_sensor_types = list(label_sensor.keys())[4:]

    for sensor_type in above_sensor_types:
        sensor_button = tk.Button(above_frame, text=label_sensor[sensor_type], command=lambda st=sensor_type: pilih_sensor(st))
        sensor_button.pack(pady=5, padx=10)

    for sensor_type in below_sensor_types:
        sensor_button = tk.Button(below_frame, text=label_sensor[sensor_type], command=lambda st=sensor_type: pilih_sensor(st))
        sensor_button.pack(pady=5, padx=10)

def tampilkan_grafik():
    def submit_id():
        id_tree = id_tree_entry.get()
        if id_tree.strip():
            tampilkan_opsi_grafik(int(id_tree))
            window.destroy()

    window = tk.Toplevel(root)
    window.title("Input ID Tanaman")

    # Perbesar jendela
    window.geometry("400x200")

    # Atur latar belakang
    background_image = tk.PhotoImage(file="background/bgneonred.png")  # Ubah nama file sesuai dengan nama file PNG Anda
    background_label = tk.Label(window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    id_tree_label = tk.Label(window, text="Masukkan ID Tanaman:", bg="lightgray")
    id_tree_label.pack(pady=(30, 5))

    id_tree_entry = tk.Entry(window)
    id_tree_entry.pack(pady=5)

    submit_button = tk.Button(window, text="Submit", command=submit_id)
    submit_button.pack(pady=5)

    # Posisikan jendela ke tengah layar
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    window.mainloop()



# Fungsi untuk menampilkan rata-rata data sensor
def tampilkan_rata_rata_sensor():
    waktu_mulai = None
    waktu_akhir = None

    def submit():
        nonlocal waktu_mulai
        nonlocal waktu_akhir

        waktu_mulai_date = cal_waktu_mulai.get_date()
        waktu_mulai_time = f"{spin_hour.get().zfill(2)}:{spin_minute.get().zfill(2)}:{spin_second.get().zfill(2)}"
        waktu_mulai = f"{waktu_mulai_date} {waktu_mulai_time}"

        waktu_akhir_date = cal_waktu_akhir.get_date()
        waktu_akhir_time = f"{spin_hour_end.get().zfill(2)}:{spin_minute_end.get().zfill(2)}:{spin_second_end.get().zfill(2)}"
        waktu_akhir = f"{waktu_akhir_date} {waktu_akhir_time}"

        window.destroy()

        try:
            if waktu_mulai and waktu_akhir:
                waktu_mulai_dt = datetime.strptime(waktu_mulai, '%Y-%m-%d %H:%M:%S')
                waktu_akhir_dt = datetime.strptime(waktu_akhir, '%Y-%m-%d %H:%M:%S')

                waktu_mulai = waktu_mulai_dt.strftime('%Y-%m-%d %H:%M:%S')
                waktu_akhir = waktu_akhir_dt.strftime('%Y-%m-%d %H:%M:%S')

                rata_rata = ambil_rata_rata_sensor(waktu_mulai, waktu_akhir)
                if rata_rata:
                    grafik_rata_rata_sensor(rata_rata, waktu_mulai, waktu_akhir)
                else:
                    messagebox.showinfo("Tidak Ada Data", "Tidak ada data rata-rata sensor yang ditemukan.")
            else:
                messagebox.showerror("Error", "Waktu mulai dan waktu selesai harus diisi.")
        except ValueError as e:
            messagebox.showerror("Error", f"Format waktu salah: {e}")

        return

    def kembali_ke_menu_utama():
        window.destroy()
        return

    window = tk.Toplevel(root)
    window.title("Input Waktu Rata-Rata Sensor")

    label_waktu_mulai = tk.Label(window, text="Waktu Mulai:")
    label_waktu_mulai.pack()

    cal_waktu_mulai = Calendar(window, date_pattern='yyyy-mm-dd')
    cal_waktu_mulai.pack()

    waktu_mulai_time_frame = tk.Frame(window)
    waktu_mulai_time_frame.pack()

    spin_hour = tk.Spinbox(waktu_mulai_time_frame, from_=0, to=23, width=2, format="%02.0f")
    spin_hour.grid(row=0, column=0)
    tk.Label(waktu_mulai_time_frame, text=":").grid(row=0, column=1)
    spin_minute = tk.Spinbox(waktu_mulai_time_frame, from_=0, to=59, width=2, format="%02.0f")
    spin_minute.grid(row=0, column=2)
    tk.Label(waktu_mulai_time_frame, text=":").grid(row=0, column=3)
    spin_second = tk.Spinbox(waktu_mulai_time_frame, from_=0, to=59, width=2, format="%02.0f")
    spin_second.grid(row=0, column=4)

    label_waktu_akhir = tk.Label(window, text="Waktu Selesai:")
    label_waktu_akhir.pack()

    cal_waktu_akhir = Calendar(window, date_pattern='yyyy-mm-dd')
    cal_waktu_akhir.pack()

    waktu_akhir_time_frame = tk.Frame(window)
    waktu_akhir_time_frame.pack()

    spin_hour_end = tk.Spinbox(waktu_akhir_time_frame, from_=0, to=23, width=2, format="%02.0f")
    spin_hour_end.grid(row=0, column=0)
    tk.Label(waktu_akhir_time_frame, text=":").grid(row=0, column=1)
    spin_minute_end = tk.Spinbox(waktu_akhir_time_frame, from_=0, to=59, width=2, format="%02.0f")
    spin_minute_end.grid(row=0, column=2)
    tk.Label(waktu_akhir_time_frame, text=":").grid(row=0, column=3)
    spin_second_end = tk.Spinbox(waktu_akhir_time_frame, from_=0, to=59, width=2, format="%02.0f")
    spin_second_end.grid(row=0, column=4)

    submit_button = tk.Button(window, text="Submit", command=submit)
    submit_button.pack()

    kembali_button = tk.Button(window, text="Kembali", command=kembali_ke_menu_utama)
    kembali_button.pack()

    window.wait_window()


# Fungsi untuk menampilkan grafik rata-rata sensor
def grafik_rata_rata_sensor(rata_rata, waktu_mulai, waktu_akhir):
    label_sensor = {
        0: "Suhu udara (°C)",
        1: "Kelembaban udara (%)",
        2: "Curah hujan (mm)",
        3: "Tingkat sinar UV",
        4: "Suhu tanah (°C)",
        5: "Kelembaban tanah (%)",
        6: "pH tanah",
        7: "Kadar N dalam tanah (mg/kg)",
        8: "Kadar P dalam tanah (mg/kg)",
        9: "Kadar K dalam tanah (mg/kg)"
    }

    jumlah_sensor = len(label_sensor)
    fig, ax = plt.subplots(figsize=(12, 8))

    # Menyiapkan array untuk posisi bar
    bar_positions = np.arange(jumlah_sensor)

    # Menyiapkan array untuk lebar bar
    bar_width = 0.35

    # Menyiapkan array untuk label bar
    bar_labels = [label_sensor[i] for i in range(jumlah_sensor)]

    # Menyiapkan warna untuk setiap bar
    colors = ['skyblue', 'salmon', 'lightgreen', 'gold', 'lightcoral', 
              'lightskyblue', 'orange', 'mediumseagreen', 'lightpink', 'lightgrey']

    # Plot garis untuk rata-rata pembacaan sensor, satu garis untuk setiap sensor
    jitter = np.linspace(-0.2, 0.2, jumlah_sensor)  # Menambahkan jitter untuk nilai x
    for i in range(jumlah_sensor):
        x_values = bar_positions + jitter[i]  # Menambahkan jitter pada posisi x
        y_values = [rata_rata[j] for j in range(jumlah_sensor)]
        ax.plot(x_values, y_values, marker='o', linestyle='-', color=colors[i], linewidth=2, label=label_sensor[i])

    # Tambahkan label pada sumbu-x
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(bar_labels, rotation=45, ha='right')

    # Tambahkan label pada sumbu-y
    ax.set_ylabel('Rata-rata Nilai Sensor')

    # Tambahkan judul dengan keterangan rentang waktu
    ax.set_title(f'Rata-rata Sensor untuk Setiap Tipe Sensor Semua Tanaman\nRentang Waktu: {waktu_mulai} - {waktu_akhir}')

    # Tambahkan grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Tambahkan legend
    ax.legend()

    plt.tight_layout()
    plt.show()

    # Plot bar untuk rata-rata pembacaan sensor dengan warna yang berbeda
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(bar_positions, [rata_rata[i] if rata_rata[i] is not None else 0 for i in range(jumlah_sensor)], 
                  bar_width, color=colors, label='Rata-rata Nilai Sensor')

    # Tambahkan label pada sumbu-x
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(bar_labels, rotation=45, ha='right')

    # Tambahkan label pada sumbu-y
    ax.set_ylabel('Rata-rata Nilai Sensor')

    # Tambahkan judul dengan keterangan rentang waktu
    ax.set_title(f'Rata-rata Sensor untuk Setiap Tipe Sensor Semua Tanaman\nRentang Waktu: {waktu_mulai} - {waktu_akhir}')

    # Tambahkan grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Tambahkan legend
    ax.legend()

    # Tambahkan nilai rata-rata di atas bar
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, round(yval, 2), va='bottom', ha='center')

    plt.tight_layout()
    plt.show()

def tampilkan_selamat_datang(nama=None):
    if nama:
        return f"Selamat datang, {nama}!"
    else:
        return "Selamat datang!"

# Fungsi untuk keluar dari aplikasi
def keluar():
    root.destroy()

# Fungsi untuk menampilkan tombol-tombol di menu utama
def tampilkan_tombol():
    def saat_masuk(e):
        e.widget.config(bg="grey")

    def saat_keluar(e):
        e.widget.config(bg=e.widget.warna_default)

    pesan_selamat_datang = tampilkan_selamat_datang(nama_pengguna)
    label_selamat_datang = tk.Label(root, text=pesan_selamat_datang, font=("Helvetica", 16), fg="white", bg="black")
    label_selamat_datang.place(relx=0.5, rely=0.1, anchor="center")

    btn_tampilkan_rata_rata = tk.Button(root, text="Tampilkan Rata-rata Sensor", command=tampilkan_rata_rata_sensor, bg="#3498db", fg="white", font=("Arial", 12, "bold"))
    btn_tampilkan_rata_rata.place(x=300, y=275, width=270, height=40)
    btn_tampilkan_rata_rata.bind("<Enter>", saat_masuk)
    btn_tampilkan_rata_rata.bind("<Leave>", saat_keluar)
    btn_tampilkan_rata_rata.warna_default = "#3498db"

    btn_hapus_tanaman = tk.Button(root, text="Hapus Tanaman", command=halaman_hapus_tanaman, bg="#3498db", fg="white", font=("Arial", 12, "bold"))
    btn_hapus_tanaman.place(x=300, y=160, width=270, height=40)
    btn_hapus_tanaman.bind("<Enter>", saat_masuk)
    btn_hapus_tanaman.bind("<Leave>", saat_keluar)
    btn_hapus_tanaman.warna_default = "#3498db"

    btn_tampilkan_data = tk.Button(root, text="Data Tanaman", command=halaman_input_id, bg="#3498db", fg="white", font=("Arial", 12, "bold"))
    btn_tampilkan_data.place(x=300, y=215, width=270, height=40)
    btn_tampilkan_data.bind("<Enter>", saat_masuk)
    btn_tampilkan_data.bind("<Leave>", saat_keluar)
    btn_tampilkan_data.warna_default = "#3498db"

    btn_tampilkan_semua_tanaman = tk.Button(root, text="Daftar Tanaman", command=tampilkan_semua_data, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
    btn_tampilkan_semua_tanaman.place(x=20, y=215, width=270, height=40)
    btn_tampilkan_semua_tanaman.bind("<Enter>", saat_masuk)
    btn_tampilkan_semua_tanaman.bind("<Leave>", saat_keluar)
    btn_tampilkan_semua_tanaman.warna_default = "#2ecc71"

    btn_tampilkan_grafik = tk.Button(root, text="Grafik Sensor Tanaman", command=tampilkan_grafik, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
    btn_tampilkan_grafik.place(x=20, y=275, width=270, height=40)
    btn_tampilkan_grafik.bind("<Enter>", saat_masuk)
    btn_tampilkan_grafik.bind("<Leave>", saat_keluar)
    btn_tampilkan_grafik.warna_default = "#2ecc71"

    btn_tambah_tanaman = tk.Button(root, text="Tambah Tanaman", command=halaman_tambah_tanaman, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
    btn_tambah_tanaman.place(x=20, y=160, width=270, height=40)
    btn_tambah_tanaman.bind("<Enter>", saat_masuk)
    btn_tambah_tanaman.bind("<Leave>", saat_keluar)
    btn_tambah_tanaman.warna_default = "#2ecc71"

    btn_keluar = tk.Button(root, text="Keluar", command=keluar, bg="#FF0000", fg="white", font=("Arial", 12, "bold"))
    btn_keluar.place(x=20, y=330, width=550, height=40)
    btn_keluar.bind("<Enter>", saat_masuk)
    btn_keluar.bind("<Leave>", saat_keluar)
    btn_keluar.warna_default = "#FF0000"

# Fungsi untuk meminta nama pengguna
def ambil_nama_pengguna():
    input_window = tk.Toplevel(root)
    input_window.title("Halooo")
    input_window.geometry("590x400")
    
    # Membaca gambar latar belakang
    background_image = tk.PhotoImage(file="background/bgmain.png")
    background_label = tk.Label(input_window, image=background_image)
    background_label.image = background_image  # Keep a reference to avoid garbage collection
    background_label.place(x=0, y=0, relwidth=1, relheight=1, anchor="nw")
    
    # Mengatur posisi jendela di tengah layar
    window_width = 590
    window_height = 400
    screen_width = input_window.winfo_screenwidth()
    screen_height = input_window.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    input_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    def on_submit():
        global nama_pengguna
        nama = entry_nama.get()
        if nama == "":
            messagebox.showwarning("Peringatan", "Jika Anda tidak ingin memasukkan nama, mohon tekan 'Lewati'.")
            return
        nama_pengguna = nama
        input_window.destroy()
        tampilkan_tombol()
        root.deiconify()
        # Inisialisasi database dan mulai pengambilan data sensor setelah nama pengguna diinput
        database()
        mulai_ambil_data_sensor()

    def lewati():
        global nama_pengguna
        nama_pengguna = None
        input_window.destroy()
        tampilkan_tombol()
        root.deiconify()
        # Inisialisasi database dan mulai pengambilan data sensor setelah nama pengguna diinput
        database()
        mulai_ambil_data_sensor()

    def saat_masuk(e):
        e.widget.config(bg="grey")

    def saat_keluar(e):
        e.widget.config(bg=e.widget.warna_default)

    label_prompt = tk.Label(input_window, text="Masukkan nama Anda:", font=("Helvetica", 16), fg="white", bg="black")
    label_prompt.place(relx=0.5, rely=0.4, anchor="center")

    entry_nama = tk.Entry(input_window, font=("Helvetica", 14))
    entry_nama.place(relx=0.5, rely=0.5, anchor="center")

    btn_submit = tk.Button(input_window, text="Masuk", command=on_submit, bg="#1E90FF", fg="white", font=("Arial", 12, "bold"))
    btn_submit.place(x=235, y=250, width=100, height=40, anchor="center")
    btn_submit.warna_default = "#1E90FF"
    btn_submit.bind("<Enter>", saat_masuk)
    btn_submit.bind("<Leave>", saat_keluar)

    btn_lewati = tk.Button(input_window, text="Lewati", command=lewati, bg="#2ecc71", fg="white", font=("Arial", 12, "bold"))
    btn_lewati.place(x=360, y=250, width=100, height=40, anchor="center")
    btn_lewati.warna_default = "#2ecc71"
    btn_lewati.bind("<Enter>", saat_masuk)
    btn_lewati.bind("<Leave>", saat_keluar)

    btn_keluar = tk.Button(input_window, text="Keluar", command=root.destroy, bg="#FF0000", fg="white", font=("Arial", 12, "bold"))
    btn_keluar.place(x=185, y=280, width=225, height=40)
    btn_keluar.warna_default = "#FF0000"
    btn_keluar.bind("<Enter>", saat_masuk)
    btn_keluar.bind("<Leave>", saat_keluar)

# Membuat root window
root = tk.Tk()
root.title("Monitoring Tanaman Nilam")
root.geometry("590x400")  # Ukuran geometri tampilan utama

# Membaca gambar latar belakang
background_image = tk.PhotoImage(file="background/bgmain.png")

# Menampilkan gambar latar belakang
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1, anchor="nw")  # Anchor diatur ke "nw" (northwest)

# Mengatur posisi jendela root di tengah layar
window_width = 590
window_height = 400
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
# Menyembunyikan jendela utama saat pertama kali diluncurkan
root.withdraw()

# Meminta nama dari pengguna
ambil_nama_pengguna()

# Menjalankan event loop

def gui():
    root.mainloop()
    return gui