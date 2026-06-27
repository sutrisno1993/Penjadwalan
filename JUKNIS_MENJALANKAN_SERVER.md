# 🚀 Petunjuk Teknis Jalankan Server SITAB

Dokumen ini menjelaskan langkah-langkah untuk menyalakan server aplikasi **SITAB (Automatic Timetable Generator)** secara lokal menggunakan Command Line Interface (CLI) maupun berkas otomatis (`.bat`).

---

## 📋 Persyaratan Sistem
Sebelum menjalankan server, pastikan komputer Anda sudah memiliki:
1. **Python 3.10+** (biasanya dijalankan menggunakan perintah `py` atau `python`).
2. Dependensi Python terinstal. Instalasi dapat dilakukan melalui terminal di direktori proyek:
   ```bash
   pip install -r requirements.txt
   ```
3. File `.env` di root direktori yang sudah berisi konfigurasi basis data Supabase:
   ```env
   DATABASE_URL=postgresql://username:password@host:port/database
   ```

---

## ⚡ Cara Cepat (Rekomendasi)
Di dalam folder proyek sudah disediakan berkas batch script (`run.bat`).
* Cukup **klik dua kali (double-click)** pada file `run.bat` di File Explorer Anda.
* Windows Command Prompt akan otomatis terbuka dan langsung menjalankan server backend.

---

## 💻 Cara Manual Melalui CLI (Command Line)

Buka terminal Anda (Command Prompt / PowerShell / Git Bash) di direktori proyek `d:\Jadwal` lalu jalankan perintah berikut:

### 1. Menjalankan Server Utama (Backend & Frontend)
Server backend SITAB dibangun dengan FastAPI dan telah dikonfigurasi untuk menyajikan frontend secara otomatis pada root URL (`/`).

Jalankan perintah berikut:
```bash
py -m uvicorn backend.main:app --host 127.0.0.1 --port 8002 --reload
```
* **Keterangan Perintah:**
  * `py -m uvicorn`: Menjalankan server ASGI Uvicorn menggunakan Python.
  * `backend.main:app`: Merujuk ke file `backend/main.py` dengan objek FastAPI bernama `app`.
  * `--host 127.0.0.1`: Menjalankan server pada localhost.
  * `--port 8002`: Port server backend dijalankan.
  * `--reload`: Mengaktifkan mode auto-restart saat ada perubahan kode (sangat berguna untuk pengembangan).

Setelah perintah di atas berjalan, buka browser Anda dan kunjungi alamat berikut untuk menggunakan aplikasi:
👉 **[http://localhost:8002](http://localhost:8002)**

---

### 2. Menjalankan Server Frontend Terpisah (Opsional / Development)
Jika Anda ingin mengembangkan frontend secara terpisah pada port lain (misalnya port `3000`), Anda bisa menyalakan server HTTP statis bawaan Python:

Jalankan perintah berikut di jendela terminal baru:
```bash
py -m http.server 3000 --directory frontend
```
* **Keterangan Perintah:**
  * `py -m http.server`: Mengaktifkan modul server HTTP bawaan Python.
  * `3000`: Port tempat server berjalan.
  * `--directory frontend`: Menentukan bahwa folder yang disajikan adalah folder `frontend`.

Setelah server menyala, Anda bisa mengaksesnya di:
👉 **[http://localhost:3000](http://localhost:3000)**

> [!WARNING]
> Jika Anda menggunakan port terpisah (`3000`), beberapa fungsi fetch API mungkin perlu disesuaikan karena perbedaan origin (CORS) atau ketidaktersediaan rute `/api` secara relatif pada port `3000`. Direkomendasikan tetap menggunakan port `8002`.

---

## 🛑 Cara Menghentikan Server
Untuk mematikan server yang sedang berjalan di terminal/command prompt:
1. Klik pada jendela terminal tersebut.
2. Tekan kombinasi tombol **`Ctrl + C`** pada keyboard Anda.
3. (Optional) Jika muncul pertanyaan `Terminate batch job (Y/N)?`, ketik `Y` lalu tekan **Enter**.
