# 📘 Juknis Pengisian Data Master (Google Sheets)

Dokumen ini merupakan Petunjuk Teknis (Juknis) langkah demi langkah untuk mengisi dan menyiapkan data master penjadwalan di **Google Sheets** sebelum dilakukan sinkronisasi (*Tarik Data Master*) pada aplikasi.

## ⚠️ Aturan Fundamental Sinkronisasi
Sistem membaca data Anda secara sekuensial (berurutan) dan saling bergantung. Jika Anda salah mengetik nama di satu tab, tab berikutnya yang merujuk ke nama tersebut akan **Error**.

```mermaid
graph LR
    A[1. Guru] --> B[2. Kelas]
    B --> C[3. Mapel]
    C --> D[4. Alokasi Kurikulum]
    D --> E[5. Penugasan Guru]
```

---

## Langkah-Langkah Detail Pengisian per Tab

### 📝 Tab 1: `master_guru`
Tab ini berisi seluruh profil, ketersediaan, dan batasan mengajar guru. Selesaikan tab ini paling pertama.

| Nama Kolom di Sheets | Tipe / Isi yang Diharapkan | Penjelasan & Contoh |
| :--- | :--- | :--- |
| **`nama_guru`** | Teks Bebas | Nama lengkap guru (beserta gelar jika ada). Contoh: `Budi Santoso, S.Pd.` |
| **`kode_guru`** | Angka | Nomor unik untuk guru tersebut (untuk ditampilkan di hasil jadwal). Contoh: `101` |
| **`hari_tersedia`** | Teks (Dipisah Koma) | Hari umum guru tersebut bisa mengajar. Gunakan nama hari kapital. Contoh: `SENIN, RABU, JUMAT` |
| **`shift_pagi`** | TRUE / FALSE | Apakah guru ini diizinkan mengajar di kelas ber-shift Pagi? (Isi dengan `TRUE` atau `FALSE`). |
| **`shift_siang`** | TRUE / FALSE | Apakah guru ini diizinkan mengajar di kelas ber-shift Siang? (Isi dengan `TRUE` atau `FALSE`). |
| **`hari_tersedia_pagi`** | Teks (Dipisah Koma) | *(Opsional)* Hari spesifik jika guru hanya bisa mengajar pagi di hari tertentu. Kosongkan jika sama dengan `hari_tersedia`. |
| **`hari_tersedia_siang`** | Teks (Dipisah Koma) | *(Opsional)* Hari spesifik jika guru hanya bisa siang di hari tertentu. Kosongkan jika sama dengan `hari_tersedia`. |
| **`min_jp`** | Angka | Beban minimal JP untuk guru ini. Jika dikosongkan, default `2` JP. |
| **`max_jp`** | Angka | Beban **maksimal absolut** JP untuk guru ini. Jika melebihi ini solver akan Error. Default `60` JP. |

---

### 📝 Tab 2: `master_kelas`
Tab ini berisi pendaftaran kelas (Rombongan Belajar) yang akan dijadwalkan.

| Nama Kolom di Sheets | Tipe / Isi yang Diharapkan | Penjelasan & Contoh |
| :--- | :--- | :--- |
| **`nama_kelas`** | Teks Bebas (Unik) | Nama rombel. Contoh: `X TKJ 1` atau `XII AKL 2`. *(Pastikan ejaan konsisten!)* |
| **`shift_operasional`** | `PAGI` / `SIANG` | Shift wajib untuk kelas ini. Kelas PAGI hanya akan diplot pada jam pagi. |
| **`tingkat`** | Teks | Tingkat kelas. Contoh: `X`, `XI`, `XII`. |
| **`jurusan`** | Teks | Nama jurusan. Contoh: `TKJ`, `AKL`, `TKR`. |

---

### 📝 Tab 3: `master_mapel`
Tab ini mendaftarkan seluruh Mata Pelajaran yang ada di kurikulum sekolah.

| Nama Kolom di Sheets | Tipe / Isi yang Diharapkan | Penjelasan & Contoh |
| :--- | :--- | :--- |
| **`nama_mapel`** | Teks Bebas (Unik) | Nama mata pelajaran. Contoh: `Matematika`, `Penjasorkes`, `Basis Data`. |
| **`kategori_mapel`** | `UMUM` / `OLAHRAGA` / `PRODUKTIF` | Sangat Penting! `OLAHRAGA` akan dikunci jadi 2 JP berturut-turut tanpa istirahat. `PRODUKTIF` akan berusaha dijadikan berurutan jika panjang. |
| **`tingkat`** | Teks (Opsional) | Berlaku untuk tingkat apa (misal: `X`). |
| **`jurusan`** | Teks (Opsional) | Berlaku untuk jurusan apa (misal: `TKJ`). |

> [!TIP]
> Khusus untuk mata pelajaran Olahraga, kategori **WAJIB** diatur sebagai `OLAHRAGA`. Sistem juga otomatis mendeteksi kata kunci seperti "Penjasorkes" atau "Jasmani" pada nama mapel.

---

### 📝 Tab 4: `alokasi_kurikulum`
Tab ini **menghubungkan Kelas dan Mapel** beserta jumlah jam per minggu.
*(Tab ini murni alokasi mata pelajaran terhadap kelas, belum melibatkan siapa gurunya).*

| Nama Kolom di Sheets | Tipe / Isi yang Diharapkan | Penjelasan & Contoh |
| :--- | :--- | :--- |
| **`nama_kelas`** | Teks | **Wajib sama persis (termasuk spasi)** dengan nama di `master_kelas`. |
| **`nama_mapel`** | Teks | **Wajib sama persis** dengan nama di `master_mapel`. |
| **`durasi_jp`** | Angka | Total Jam Pelajaran (JP) dalam seminggu untuk mapel tersebut di kelas itu. Contoh: `4`. |

> [!CAUTION]
> 1. Total `durasi_jp` untuk satu kelas dari seluruh barisnya **TIDAK BOLEH** lebih dari 40 JP. Jika lebih, proses sinkronisasi akan langsung gagal/Error.
> 2. Untuk mapel berkategori `OLAHRAGA`, `durasi_jp` wajib diset **2**. Jika diset 3 atau 1, sistem akan Error.

---

### 📝 Tab 5: `penugasan_guru`
Tab ini adalah "Kolam Kualifikasi" (Pool). Anda mendata **siapa saja guru yang boleh/mampu mengajar** mata pelajaran tertentu. 

| Nama Kolom di Sheets | Tipe / Isi yang Diharapkan | Penjelasan & Contoh |
| :--- | :--- | :--- |
| **`nama_guru`** | Teks | **Wajib sama persis** dengan di `master_guru`. |
| **`nama_mapel`** | Teks | **Wajib sama persis** dengan di `master_mapel`. |

> [!IMPORTANT]
> **Mengapa ada Tab 5? Bukankah 1 guru mengajar 1 mapel spesifik?**
> Sistem solver aplikasi ini *tidak* meminta Anda mencocokkan "Mapel X di Kelas Y diajarkan oleh Guru Z". Sistem hanya butuh tahu "Guru A dan Guru B sama-sama bisa mengajar Matematika". 
> Nanti, sistem yang akan secara otomatis **mencarikan** (mengundi) antara Guru A atau Guru B mana yang paling pas untuk mengisi jadwal Kelas Y agar tidak bentrok.

---

## 🛠️ Troubleshooting Error Sinkronisasi

Ketika Anda menekan tombol **"Tarik Data Master"**, aplikasi akan menimpa ulang (menghapus) data lama di database. Apabila muncul notifikasi gagal sebagian (*Partial*), baca tab notifikasi dengan saksama:

1. **Error: "Kelas [Nama] tidak ditemukan"** 
   - Anda salah ketik di Tab 4 (`alokasi_kurikulum`). Misal di Tab 2 namanya `X TKJ 1`, tapi di Tab 4 Anda ketik `X-TKJ-1`. Sistem tidak akan mengenalinya. Samakan ketikannya.
2. **Error: "Guru [Nama] tidak ditemukan di master_guru"**
   - Kasus serupa di Tab 5. Pastikan huruf besar-kecil dan gelar diketik identik dengan Tab 1.
3. **Peringatan: "Coverage — Shift PAGI, SENIN... Kekurangan 2 Guru"**
   - Artinya, di hari Senin shift Pagi, jumlah kelas Anda lebih banyak daripada jumlah guru yang dikonfigurasi masuk pada Senin Pagi. 
   - Cek kembali Tab 1, pastikan `shift_pagi` di-set `TRUE` dan `hari_tersedia` menyertakan `SENIN` untuk guru yang bersangkutan.
