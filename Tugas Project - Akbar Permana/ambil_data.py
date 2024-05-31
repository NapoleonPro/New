import sqlite3
import json
import urllib.request
from datetime import datetime
import time
from threading import Thread, Event
import numpy as np
import matplotlib.dates as mdates


# Membuat database 
def database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS database (
        id_tree INTEGER PRIMARY KEY,
        latitude REAL,
        longitude REAL,
        added_timestamp TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_data (
        id_tree INTEGER,
        sensor_type INTEGER,
        nilai REAL,
        timestamp TEXT,
        PRIMARY KEY (id_tree, sensor_type, timestamp)
    )
    ''')
    conn.commit()
    conn.close()


# Fungsi untuk membuat format timestamp waktu
def format_timestamp(timestamp):
    """Format timestamp untuk waktu."""
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S') 
    return dt.strftime('%a, %d %b %Y %H:%M:%S')

# Buat variable global untuk menghentikan pengambilan data sensor
stop_sensor = Event()

# Buat variable global untuk set menyimpan ID tanaman yang telah dihapus
hapus_tanaman_set = set()

# Deklarasi npm dan api yang digunakan
NPM = '2304111010057'
API = 'https://belajar-python-unsyiah.an.r.appspot.com/sensor/read'

# Fungsi untuk ambil data sensor dari API
def ambil_data_sensor(id_tree, sensor_type):
    try:
        url = f"{API}?npm={NPM}&id_tree={id_tree}&sensor_type={sensor_type}"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode("utf-8"))
            nilai = data['value']
            timestamp = data.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')  
            timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Data diambil untuk ID tanaman = {id_tree}, tipe_sensor = {sensor_type}, nilai = {nilai}, waktu = {timestamp}")
            return nilai, timestamp
    except Exception as e:
        print(f"Gagal mengambil data untuk id_tanaman={id_tree}, tipe_sensor={sensor_type}: {e}")
        return None, None


# Fungsi untuk menyimpan data sensor ke dalam database 
def simpan_data_sensor(id_tree, sensor_type, nilai, timestamp):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO sensor_data (id_tree, sensor_type, nilai, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (id_tree, sensor_type, nilai, timestamp))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError as e:
        print(f"Gagal menyimpan data untuk id_tanaman={id_tree}, tipe_sensor={sensor_type}, waktu={timestamp}: {e}")



# Fungsi untuk mulai ambil data sensor secara berkala 
def mulai_ambil_data_sensor():
    def ambil_data_secara_berkala():
        while not stop_sensor.is_set():
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute ('SELECT id_tree FROM database')
            database =  cursor.fetchall()
            conn.close()

            for data in database:
                id_tree = data[0]
                if id_tree in hapus_tanaman_set:
                    continue

                for sensor_type in range(10):
                    nilai, timestamp = ambil_data_sensor(id_tree, sensor_type)
                    if nilai is not None and timestamp is not None:
                        simpan_data_sensor(id_tree, sensor_type, nilai, timestamp)

            time.sleep(60) # Mengambil data sensor setiap 1 menit

    # Membuat thread baru dengan target fungsi 'ambil_data_secara_berkala'
    thread = Thread(target=ambil_data_secara_berkala)
    thread.daemon = True 
    thread.start()

# Fungsi ambil data sensor untuk grafik 
def ambil_data_sensor_untuk_grafik(id_tree, sensor_type, waktu_mulai, waktu_akhir):
    print(f"Mengambil data dari {waktu_mulai} hingga {waktu_akhir}")

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT nilai, timestamp
    FROM sensor_data
    WHERE id_tree = ? AND sensor_type = ? AND timestamp BETWEEN ? AND ?
    ORDER BY timestamp
    ''', (id_tree, sensor_type, waktu_mulai, waktu_akhir))
    data = cursor.fetchall()
    conn.close()
    print(f"Data yang ditemukan: {data}")
    return data

# Fungsi untuk ambil rata-rata semua sensor dari semua tanaman
def ambil_rata_rata_sensor(waktu_mulai, waktu_akhir):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    data_rata_rata = {i: None for i in range(10)}  # Inisialisasi dictionary dengan 10 sensor

    cursor.execute('''
    SELECT sensor_type, AVG(nilai)
    FROM sensor_data
    WHERE timestamp BETWEEN ? AND ?
    GROUP BY sensor_type
    ''', (waktu_mulai, waktu_akhir))

    baris_baris = cursor.fetchall()
    for baris in baris_baris:
        sensor_type, avg_nilai = baris
        data_rata_rata[sensor_type] = avg_nilai

    conn.close()
    return data_rata_rata


# Fungsi interpolasi data hilang untuk mengatasi nilai grafik yang hilang dari rentang waktu yang diminta
def interpolasi_data_hilang(timestamps, nilai, waktu_mulai, waktu_akhir):
    """Interpolasi data untuk mengisi nilai yang hilang di titik awal dan akhir."""
    timestamps = np.array([mdates.date2num(ts) for ts in timestamps])
    nilai = np.array(nilai)

    # Mengonversi string waktu ke objek datetime
    mulai_waktu = mdates.date2num(datetime.strptime(waktu_mulai, '%Y-%m-%d %H:%M:%S'))
    akhir_waktu = mdates.date2num(datetime.strptime(waktu_akhir, '%Y-%m-%d %H:%M:%S'))

    # Jika timestamps tidak memiliki mulai_waktu atau akhir_waktu tambahkan mereka dengan interpolasi
    if mulai_waktu not in timestamps:
        nilai_awal = np.interp(mulai_waktu, timestamps, nilai)
        timestamps = np.insert(timestamps, 0, mulai_waktu)
        nilai = np.insert(nilai, 0, nilai_awal)

    if akhir_waktu not in timestamps:
        nilai_akhir = np.interp(akhir_waktu, timestamps, nilai)
        timestamps = np.append(timestamps, akhir_waktu)
        nilai = np.append(nilai, nilai_akhir)

    # konversi kembali timestamps ke datetime tanpa zona waktu
    timestamps = [mdates.num2date(ts) for ts in timestamps]

    return timestamps, nilai