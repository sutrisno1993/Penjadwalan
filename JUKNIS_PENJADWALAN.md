# 📘 Juknis Penjadwalan Otomatis: Filosofi, Constraint, dan Troubleshooting

Dokumen ini merupakan Petunjuk Teknis (Juknis) hasil analisis terhadap mesin penjadwal (Solver) dan logika sistem. Sistem ini dikendalikan oleh **Google OR-Tools CP-SAT Solver** menggunakan **Hard Constraints** (Aturan Mutlak) dan **Soft Constraints** (Aturan Fleksibel).

---

## 1. Filosofi Desain Penjadwalan (Pendekatan Sutrisno)

Di masa lalu, bagian kurikulum terbiasa memplot alokasi jadwal secara statis sejak awal: **Guru Siapa, mengajar Mapel Apa, di Kelas Mana, dan Berapa Jam**. 
Praktik *micromanagement* ini seringkali membuat jadwal **sangat sulit untuk di-generate**. Terlalu banyak data yang bersinggungan dan jadwal guru menjadi bentrok karena ketersediaan hari/waktu mereka terbatas.

Untuk memecahkan masalah ini, **Sutrisno (Pengembang Sistem)** mengambil pendekatan desain baru:
1. **Penentuan Guru Spesifik Adalah Opsional (Pool-Based)**
   Sistem disarankan bekerja menggunakan sistem *pool* kualifikasi (Tab 5). Anda cukup mendata "Guru A dan B mampu mengajar Matematika". Mesin otomatis akan membagi-bagikan kelas mana yang diajar Guru A dan Kelas mana yang diajar Guru B untuk secara cerdas **menghindari konflik/bentrok waktu**.
   
   Namun, jika Anda tetap ingin memplot guru tertentu secara mutlak ke kelas dan mapel tertentu, Anda dapat mengelolanya melalui **Tab 6: Guru Mutlak** di halaman Data Master. Tab ini didesain khusus agar penginputan aman dan teratur melalui **Input Berurutan (Terfilter)**:
   - Pertama, pilih **Guru** (Dropdown Mapel & Kelas dalam kondisi terkunci).
   - Kedua, dropdown **Mata Pelajaran** akan aktif dan otomatis terfilter hanya menampilkan mapel yang diampu oleh guru tersebut (berdasarkan data Tab 5).
   - Ketiga, dropdown **Kelas** akan aktif dan otomatis terfilter hanya menampilkan kelas yang memiliki alokasi kurikulum untuk mapel tersebut (berdasarkan data Tab 4).
   
   Fitur mengunci guru (`id_guru_mutlak`) ini adalah **Hard Constraint**. Jika terlalu banyak diterapkan, sistem pasti akan menemukan kebuntuan (Infeasible). Anda dapat mengelola (CRUD) daftar penguncian aktif langsung dari tabel di sisi kanan Tab 6.
2. **Kontrol Pemerataan via `min_jp` dan `max_jp`**
   Karena guru didistribusikan secara otomatis oleh sistem, muncul risiko bahwa seorang guru tidak mendapatkan jam sama sekali, atau sebaliknya, dieksploitasi dengan jam terlalu banyak. Untuk membatasi dan mencegah hal ini, Sutrisno mengambil opsi untuk menerapkan batasan **Minimal JP (`min_jp`)** dan **Maksimal JP (`max_jp`)** per guru.

---

## 2. Sistem Peringatan (Warning System)

Peringatan (Warning) **tidak akan membatalkan** proses penyusunan jadwal. Jadwal tetap ter-generate, namun dengan catatan:

- **Peringatan Cakupan Guru (Coverage)**: Di awal proses, sistem membandingkan jumlah guru yang tersedia dengan jumlah kelas. Jika guru lebih sedikit dari kelas, akan muncul peringatan potensi slot kosong.
- **Beban Mengajar Kurang (`min_jp`)**: Sistem mendeteksi jika ada guru yang mendapat alokasi JP lebih rendah dari batas `min_jp` yang ditetapkan (misalnya hanya dapat 2 JP padahal minimal harusnya 10 JP).
- **Guru Tidak Mendapat Jam (0 JP)**: Sistem secara otomatis mendeteksi jika ada guru aktif yang tidak mendapatkan slot jam mengajar sama sekali (0 JP) setelah proses generate selesai. Peringatan ini akan muncul secara spesifik di **Konsol Log** sebagai `[Tidak Mendapat Jam]`, di bagian bawah halaman **Grid Jadwal**, dan di tab **Ringkasan Alokasi** dengan badge status merah **"Tidak Mendapat Jam"**.
- **JP Kelas Kurang dari 40**: Jika alokasi kelas di Tab 4 kurang dari 40 JP, sistem otomatis mengisi sisa slot tersebut dengan teks **"KOSONG"**.
- **Peringatan Substitusi / Fallback (Tahap 2 & 3)**:
  Apabila sistem tidak bisa menemukan guru utama (Stage 1) yang tidak bentrok, ia akan "meminjam" guru lain:
  - **Substitusi Tahap 2**: Diganti dengan guru dari Kategori Mapel yang sama.
  - **Substitusi Tahap 3**: Diganti dengan guru bebas mana saja asalkan shift/harinya cocok.

> [!WARNING]
> Terlalu banyak pesan "Substitusi" berarti ketersediaan hari guru utama terlalu sempit. Solusi: perlebar (kosongkan) batas hari kerja guru di Tab 1.

---

## 3. Aturan Mutlak (Hard Constraints)

Ini adalah batasan yang membuat solver **PASTI GAGAL (Infeasible / Error)** jika tidak dapat dipenuhi:

1. **Beban Guru Maksimal (`max_jp`)**: Seorang guru **TIDAK BOLEH** mengajar melampaui `max_jp`. Sistem mengunci ini sebagai aturan mutlak.
2. **Kesesuaian Waktu & Shift (Availability)**: Guru dilarang diplot di hari/shift yang tidak sesuai dengan izin profil mereka (`shift_pagi` / `shift_siang`).
3. **No Teacher Clash (Bentrok Guru)**: Guru tidak boleh mengajar di dua kelas berbeda pada menit riil yang sama (*wall-clock time*).
4. **No Class Clash**: Sebuah kelas maksimal diajar 1 mata pelajaran per slot jam.
5. **Olahraga (Penjasorkes) Wajib Blok Tanpa Istirahat**: Mapel Olahraga **mutlak** harus 2 JP berturut-turut pada hari yang sama, dan dilarang keras melompati jam istirahat (potongan JP 4 ke JP 5). 
6. **Maksimal 40 JP per Kelas**: Pre-Flight Error akan membatalkan proses jika alokasi JP kelas lewat dari 40.
7. **Satu Guru Per Alokasi**: 1 baris alokasi di suatu kelas tidak boleh dibagi kepada 2 guru. Wajib diselesaikan oleh **1 orang guru**.
8. **Penguncian Guru Mutlak (Fixed Teacher)**: Jika fitur ini dipakai, sistem **wajib** menggunakan guru tersebut. Jika guru mutlak tersebut bentrok, solver dilarang mencari pengganti dan langsung Gagal (Infeasible).

---

## 4. Aturan Fleksibel (Soft Constraints / Optimasi)

Solver boleh "melanggar" aturan ini dengan konsekuensi penalti nilai internal sistem, namun jadwal tetap jadi:

1. **Mapel Produktif (≥ 4 JP) Berurutan**: Sangat diusahakan menjadi blok jam pada hari yang sama. Boleh dipecah beda hari hanya jika slot sangat kritis.
2. **Pemerataan Beban Mengajar**: Sistem berusaha meratakan beban antar guru berkompetensi sama (mengacu pada trik Sutrisno di poin 1).
3. **Anti-Tumpuk Hari**: Sistem berusaha memecah jam guru ke beberapa hari. Sangat dihindari 1 guru dijejali > 5 JP pada satu hari yang sama jika hari lain masih kosong.
4. **Prioritas Guru (`min_jp` Tinggi)**: Guru yang punya `min_jp` tinggi diprioritaskan oleh sistem untuk dicarikan jam kosong.

---

## 5. Penyebab Utama "Gagal Generate" & Troubleshoot

Apabila proses menampilkan pesan **FAILED / Infeasible / Error**:

### A. Error "Tidak Ada Guru yang Kualifikasi..." (Pre-Flight)
- **Gejala**: Proses mandek sebelum mencoba menyusun jadwal.
- **Analisis**: Mapel X di Shift Pagi, tapi tidak ada satu pun guru di Tab 5 yang bisa mengajar Mapel X dan punya izin `shift_pagi = TRUE`.
- **Solusi**: Daftarkan guru untuk mapel tersebut di Tab 5, dan pastikan status shift paginya `TRUE`.

### B. Infeasible akibat `max_jp` Terlampaui
- **Gejala**: Gagal di seluruh Stage (1-3).
- **Analisis**: Total beban kurikulum untuk Mapel X ternyata butuh 60 JP. Namun Anda hanya punya 1 Guru dengan `max_jp = 40`. Sistem mentok karena `max_jp` bersifat mutlak.
- **Solusi**: Tambah/rekrut guru kedua untuk Mapel X di Tab 5, atau naikkan plafon `max_jp` guru pertama.

### C. Infeasible karena Jepitan Guru Mutlak
- **Gejala**: Error guru mutlak bentrok.
- **Analisis**: Anda menggunakan metode lama (mem-plot `id_guru_mutlak` ke Kelas X dan Kelas Y di saat bersamaan). Karena hari guru tersebut sangat sempit, jadinya ia bentrok dengan dirinya sendiri.
- **Solusi**: Ikuti saran Sutrisno. Lepas `id_guru_mutlak`, masukkan guru ke dalam Pool (Tab 5), dan biarkan sistem meratakan secara otomatis agar tidak konflik.

### D. Infeasible karena "Jepitan" Olahraga
- **Analisis**: Olahraga menuntut 2 blok utuh tanpa potong istirahat. Jika ketersediaan hari Guru Olahraga terlalu sempit, ia tidak akan kebagian tempat.
- **Solusi**: Perlebar hari ketersediaan guru Olahraga.
