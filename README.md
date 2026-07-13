# Layanan Pengaduan Jaringan 🌐

Sistem Informasi Layanan Pengaduan Jaringan (Helpdesk Jaringan) berbasis web yang dikembangkan menggunakan framework Django (Python). Aplikasi ini bertujuan untuk memudahkan pelaporan, penanganan, dan pemantauan kendala jaringan yang terjadi di berbagai bidang/departemen.

## 🚀 Fitur Utama

- **Manajemen Pengaduan (Tiket):** Pelaporan kendala jaringan dengan kategori, deskripsi detail, lampiran, dan prioritas.
- **Role-Based Access Control (RBAC):** Hak akses yang dibedakan untuk 3 peran utama (Admin, Teknisi, dan Pelapor).
- **Tracking Status Laporan:** Memantau status laporan (Menunggu, Diproses, Selesai).
- **Service Level Agreement (SLA):** Peringatan otomatis jika laporan belum ditangani dalam waktu 24 jam.
- **Sistem Rating & Ulasan:** Pelapor dapat memberikan penilaian dan ulasan terhadap kinerja teknisi setelah laporan selesai.
- **Manajemen Pengguna:** Admin dapat mengelola akun pengguna, mengatur bidang/departemen, dan menambahkan akun teknisi.
- **Dashboard Informatif:** Dashboard yang disesuaikan untuk masing-masing peran pengguna.

## 👥 Peran Pengguna (Roles)

1. **Pelapor (User/Pegawai)**
   - Membuat laporan pengaduan jaringan baru.
   - Melampirkan bukti kendala (foto/dokumen).
   - Melihat status laporan yang telah dibuat.
   - Memberikan rating dan ulasan pada laporan yang telah diselesaikan.

2. **Teknisi**
   - Menerima dan menangani laporan pengaduan yang ditugaskan.
   - Memperbarui status laporan (Menunggu -> Diproses -> Selesai).
   - Mengunggah bukti penyelesaian dan memberikan solusi yang dilakukan.

3. **Admin**
   - Memantau seluruh laporan pengaduan yang masuk.
   - Mengelola akun teknisi dan pelapor.
   - Mengelola data Bidang / Departemen.
   - Melihat ringkasan dan detail setiap laporan di sistem.

## 🛠️ Teknologi yang Digunakan

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript (Template Engine Django)
- **Database:** SQLite (Bawaan Django, dapat disesuaikan ke PostgreSQL/MySQL)

## 📸 Screenshot Antarmuka (UI)

### 👨‍💼 Halaman Pelapor
<details>
<summary>Lihat Screenshot Pelapor</summary>

- **Login Pelapor**  
  *Halaman awal bagi pegawai (pelapor) untuk masuk ke dalam sistem menggunakan kredensial email/username.*
<br> <img src="screenshot/pelapor/login.jpg" width="800">

- **Dashboard Pelapor**  
  *Menampilkan ringkasan status tiket secara keseluruhan (menunggu, diproses, selesai) agar pelapor dapat memantau dengan cepat.*
<br> <img src="screenshot/pelapor/dasboard.jpg" width="800">

- **Buat Laporan**  
  *Formulir pengajuan pengaduan di mana pelapor dapat mengisi judul, memilih kategori kendala, mendeskripsikan detail, dan melampirkan foto.*
<br> <img src="screenshot/pelapor/buat_laporan_.jpg" width="800">

- **Daftar Laporan**  
  *Tabel riwayat seluruh laporan yang pernah diajukan oleh pelapor, lengkap dengan label status warna-warni untuk identifikasi mudah.*
<br> <img src="screenshot/pelapor/daftar_laporan.jpg" width="800">

- **Detail Laporan**  
  *Tampilan rincian spesifik satu laporan yang mencakup solusi dari teknisi serta form untuk memberikan rating & ulasan kepuasan pengguna.*
<br> <img src="screenshot/pelapor/detail_laporan.jpg" width="800">

- **Profil Pelapor**  
  *Halaman pengelolaan akun untuk melengkapi data diri, nomor telepon, dan asal bidang/departemen.*
<br> <img src="screenshot/pelapor/profil.jpg" width="800">
</details>

### 🔧 Halaman Teknisi
<details>
<summary>Lihat Screenshot Teknisi</summary>

- **Login Teknisi**  
  *Portal akses yang digunakan oleh staf IT/teknisi jaringan.*
<br> <img src="screenshot/teknisi/login.jpg" width="800">

- **Dashboard Teknisi**  
  *Menyajikan statistik performa teknisi berupa jumlah tiket yang masuk dan harus segera dikerjakan (Task Assignment).*
<br> <img src="screenshot/teknisi/dasboard.jpg" width="800">

- **Daftar Laporan Tugas**  
  *Antrean tiket pengaduan yang ditugaskan khusus kepada teknisi yang sedang login.*
<br> <img src="screenshot/teknisi/daftar_laporan.jpg" width="800">

- **Detail & Penanganan Laporan**  
  *Ruang kerja teknisi untuk memproses laporan. Di sini teknisi mengubah status laporan, memasukkan catatan solusi perbaikan, dan mengunggah foto bukti jaringan kembali normal.*
<br> <img src="screenshot/teknisi/detail_laporan.jpg" width="800">

- **Profil Teknisi**  
  *Halaman informasi pribadi milik teknisi jaringan.*
<br> <img src="screenshot/teknisi/profil.jpg" width="800">
</details>

### 👑 Halaman Admin
<details>
<summary>Lihat Screenshot Admin</summary>

- **Login Admin**  
  *Pintu masuk utama untuk level manajerial / administrator.*
<br> <img src="screenshot/admin/login_admin.jpg" width="800">

- **Dashboard Admin**  
  *Pusat kendali utama (Control Center) yang merangkum keseluruhan data operasional, rasio penyelesaian masalah, serta daftar tiket yang melampaui batas waktu SLA (Service Level Agreement).*
<br> <img src="screenshot/admin/dasboard.png" width="800">

- **Daftar Seluruh Laporan**  
  *Tabel komprehensif seluruh tiket lintas bidang dan lintas teknisi untuk kebutuhan pemantauan dan audit.*
<br> <img src="screenshot/admin/daftar_laporan.jpg" width="800">

- **Detail Laporan (Pantauan Admin)**  
  *Pandangan utuh dari suatu tiket yang memungkinkan admin melakukan evaluasi jika penyelesaian dirasa kurang tepat.*
<br> <img src="screenshot/admin/laporan_detail.png" width="800">

- **Buat Akun Teknisi**  
  *Fitur administrasi khusus bagi Admin untuk mendaftarkan akun staf IT baru dengan privilese (hak akses) teknisi.*
<br> <img src="screenshot/admin/buat_akun_teknisi_.jpg" width="800">

- **Profil Admin**  
  *Halaman pengelolaan data diri administrator.*
<br> <img src="screenshot/admin/profil.jpg" width="800">
</details>

## ⚙️ Panduan Instalasi (Menjalankan secara Lokal)

1. **Clone Repository**
   ```bash
   git clone https://github.com/Ferly02/layananpengaduanjaringan.git
   cd layananpengaduanjaringan
   ```

2. **Buat dan Aktifkan Virtual Environment (Opsional namun disarankan)**
   ```bash
   python -m venv venv
   # Di Windows
   venv\Scripts\activate
   # Di Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**
   (Pastikan terdapat `requirements.txt`, jika tidak, install Django)
   ```bash
   pip install django
   ```

4. **Jalankan Migrasi Database**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Buat Superuser (Admin) / Seed Data**
   ```bash
   python create_admin.py  # Jika Anda memiliki script ini
   # Atau
   python manage.py createsuperuser
   ```

6. **Jalankan Development Server**
   ```bash
   python manage.py runserver
   ```
   Aplikasi dapat diakses melalui browser di `http://127.0.0.1:8000/`.

---
**Repository:** [https://github.com/Ferly02/layananpengaduanjaringan.git](https://github.com/Ferly02/layananpengaduanjaringan.git)
