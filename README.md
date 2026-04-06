# toko-ai-agent 

Sistem manajemen toko berbasis AI yang berjalan secara lokal (offline) untuk membantu pembukuan, audit stok, dan analisis bisnis secara otomatis.

Project ini dirancang untuk toko kecil hingga menengah yang membutuhkan sistem sederhana, stabil, dan bisa berjalan tanpa internet.

Fitur Utama 1. Audit Stok Harian Mencatat stok masuk dan keluar Monitoring stok bahan Deteksi selisih stok Riwayat audit harian Satuan: kg, liter, pcs 2. Pembukuan Sederhana Pendapatan harian (1 angka per hari) Pencatatan biaya Rekap laporan otomatis Ringkasan bulanan 3. AI Agent (Offline) Tanya jawab data toko Analisis stok Prediksi kebutuhan bahan Membantu pengambilan keputusan Berjalan tanpa internet 4. Backup Otomatis Backup data harian Backup database Restore data jika terjadi error Contoh Penggunaan 

User dapat bertanya ke AI:

"Berapa stok salom hari ini?" "Berapa total pendapatan minggu ini?" "Apakah stok bumbu kacang cukup untuk 3 hari?" "Hitung keuntungan bulan ini" 

AI akan membaca data dan memberikan jawaban secara otomatis.

Struktur Folder 

toko-ai-agent/ │ ├── data/ │ ├── stok.csv │ ├── transaksi.csv │ ├── biaya.csv │ ├── backup/ │ ├── auto/ │ └── manual/ │ ├── ai/ │ ├── model/ │ ├── agent.py │ └── prompt.txt │ ├── core/ │ ├── audit.py │ ├── pembukuan.py │ └── stok.py │ ├── database/ │ └── db.sqlite │ ├── logs/ │ ├── config.py ├── main.py └── README.md

Teknologi yang Digunakan Python SQLite CSV AI Model Lokal (GGUF) LLM Offline Raspberry Pi / Linux / Windows 

Contoh model yang didukung:

qwen2.5-3b-instruct llama3 mistral gemma Cara Menjalankan 1. Clone Repository 

git clone https://github.com/username/toko-ai-agent.git

cd toko-ai-agent

2. Install Dependency 

pip install -r requirements.txt

3. Jalankan Program 

python main.py

Mode Sistem 

Sistem dapat berjalan dalam beberapa mode:

Mode Manual 

User memasukkan data secara manual.

Contoh:

Tambah stok
Tambah transaksi
Tambah biaya

Mode AI 

User bisa bertanya langsung ke AI.

Contoh:

Berapa stok hari ini
Hitung pendapatan hari ini
Apakah stok cukup

Data yang Dicatat Stok 

Nama Barang
Satuan
Jumlah
Tanggal

Contoh:

Bahan Salom
kg
12
2026-04-06

Transaksi 

Tanggal
Pendapatan

Contoh:

2026-04-06
450000

Biaya 

Tanggal
Nama Biaya
Jumlah

Contoh:

2026-04-06
Gas
50000

Backup Otomatis 

Backup akan dilakukan:

Setiap hari Saat program ditutup Saat data diubah 

Lokasi backup:

backup/auto/

Target Sistem 

Dirancang untuk:

Warung makan Toko kecil UMKM Usaha rumahan Sistem offline Roadmap Pengembangan 

Versi 1

Audit stok Pembukuan sederhana Backup otomatis 

Versi 2

AI agent offline Prediksi stok Notifikasi stok habis 

Versi 3

Dashboard Multi user Laporan grafik 

Versi 4

Sinkronisasi cloud (opsional) Mobile app Lisensi 

MIT License

Author 

toko-ai-agent

Sistem AI Lokal untuk Manajemen Toko


