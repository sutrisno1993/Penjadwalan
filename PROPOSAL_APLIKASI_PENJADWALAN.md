# PROPOSAL PENGAJUAN UJI COBA & IMPLEMENTASI
## APLIKASI PENJADWALAN PELAJARAN OTOMATIS BERBASIS GOOGLE OR-TOOLS CP-SAT
**Dual-Shift (Pagi & Siang) SMK**

---

**Kepada Yth.**
**Bapak Samsul Huda, S.Pd.**
Wakil Kepala Sekolah Bidang Kurikulum (Wakakurikulum)
Di Tempat

**Perihal:** Pengajuan Uji Coba, Review Output, dan Rencana Presentasi Aplikasi Penjadwalan Pelajaran Otomatis
**Pengaju:** Sutrisno (Staf Pengajar / Tim Pengembang Sistem)

---

## 1. PENDAHULUAN & LATAR BELAKANG

Penyusunan jadwal pelajaran di sekolah kejuruan (SMK) dengan sistem dua shift (Pagi dan Siang) merupakan salah satu tugas paling kompleks di awal tahun ajaran atau semester. Pendekatan konvensional yang mem-plot alokasi guru, mata pelajaran, dan kelas secara statis/manual sering kali menghadapi jalan buntu (*infeasible*). Konflik jadwal guru, keterbatasan waktu mengajar, distribusi jam pelajaran (JP) yang tidak merata, serta aturan ketat mata pelajaran tertentu (seperti Olahraga dan Produktif) membutuhkan energi dan waktu yang besar untuk diselesaikan secara manual.

Untuk mengatasi permasalahan tersebut, saya, **Sutrisno**, telah mengembangkan sebuah **Aplikasi Penjadwalan Pelajaran Otomatis** menggunakan mesin pencari solusi matematis modern, yaitu **Google OR-Tools CP-SAT Solver**. Aplikasi ini dirancang agar dapat memproses ribuan kemungkinan kombinasi jadwal secara objektif, efisien, dan bebas konflik dalam hitungan detik.

---

## 2. FILOSOFI & PENDEKATAN PENYUSUNAN JADWAL

Dalam praktiknya, terdapat dua metode utama yang sering digunakan oleh tim kurikulum dalam menyusun jadwal:
1. **Alokasi Terlebih Dahulu:** Menentukan plot guru secara statis sejak awal (siapa mengajar di kelas apa, mapel apa, dan berapa jam), baru kemudian menyusun hari dan jamnya.
2. **Jadwal Terlebih Dahulu:** Menyusun jadwal (hari dan jam) terlebih dahulu secara dinamis, baru kemudian alokasi guru mengikuti kompetensi yang kosong.

Karena saya tidak mengetahui secara pasti alur spesifik mana yang biasa Bapak gunakan, sistem ini saya rancang menggunakan **Pendekatan Kombinasi (Hybrid Approach)** untuk menjembatani keduanya:

* **Fitur Guru Mutlak (*Fixed Teacher*):** Bapak tetap dapat menentukan guru tertentu untuk wajib mengajar di kelas dan mata pelajaran tertentu (mengunci alokasi). Fitur ini bersifat opsional, dapat digunakan untuk kelas tertentu saja atau diabaikan jika ingin sistem membagi secara otomatis.
* **Pendekatan Min JP & Max JP:** Untuk mengatasi masalah jam mengajar yang berlebih (*overload*) atau kurang (*underload*), sistem menggunakan kontrol batasan minimal jam (`min_jp`) dan maksimal jam (`max_jp`) per guru.
* **Pencegahan Jadwal Mustahil (*Infeasible*):** 
  Jika seluruh alokasi guru di semua kelas dikunci secara kaku sejak awal (guru mutlak), ditambah dengan sempitnya ketersediaan hari mengajar guru, sistem akan mendeteksi status **Infeasible** (jadwal mustahil dibuat). Hal ini disebabkan karena sistem memegang aturan mutlak (Hard Constraint) bahwa **seorang guru tidak boleh mengajar di dua kelas berbeda pada jam pelajaran yang sama**. Pendekatan kombinasi ini memberikan fleksibilitas bagi solver untuk menemukan solusi terbaik tanpa melanggar aturan bentrok tersebut.

---

## 3. DETAIL DATA UJI COBA (STATUS REAL DATA)

Untuk membuktikan efektivitas aplikasi ini, sistem telah diuji dengan **data sekolah riil (Real Data)** yang disinkronkan langsung ke database. Kondisi kesiapan data saat ini adalah sebagai berikut:
1. **Data Guru & Kompetensi (Real):** Telah diinput 37 guru riil beserta pemetaan mata pelajaran yang kompeten mereka ampu.
2. **Data Kelas & Shift (Real):** Telah dipetakan seluruh kelas riil dengan shift operasional masing-masing (Pagi/Siang).
3. **Data Alokasi Kurikulum (Real):** Beban jam pelajaran (JP) per mata pelajaran untuk setiap kelas telah disesuaikan dengan struktur kurikulum sekolah riil (maksimal 40 JP per kelas).
4. **Ketersediaan Hari Mengajar (Kecuali):** Untuk saat ini, ketersediaan hari/waktu mengajar guru masih bersifat data uji coba (*dummy*). Pembaruan ketersediaan hari mengajar yang riil akan kami lakukan setelah mendapatkan konfirmasi atau data terbaru dari bagian kurikulum.

---

## 4. ARSITEKTUR & FITUR UTAMA APLIKASI

Aplikasi ini dibangun dengan teknologi modern yang memudahkan integrasi dan penggunaan sehari-hari oleh staf kurikulum:

* **Backend Engine:** Menggunakan **FastAPI (Python)** yang cepat dan handal untuk memproses algoritma penjadwalan.
* **Database Relasional:** Menggunakan **Supabase (PostgreSQL)** untuk penyimpanan data master dan hasil penjadwalan yang aman dan rapi.
* **Ekspor Hasil Jadwal (1 File Excel dengan 4 Sheet):**
  Hasil jadwal pelajaran diekspor langsung ke dalam satu file Excel komprehensif yang terbagi menjadi empat sheet siap pakai:
  1. **Sheet `Jadwal PAGI`**: Grid jadwal lengkap kelas shift pagi per hari (Senin - Sabtu) dan per jam pelajaran (JP 1-7).
  2. **Sheet `Jadwal SIANG`**: Grid jadwal lengkap kelas shift siang per hari (Senin - Sabtu) dan per jam pelajaran (JP 1-7).
  3. **Sheet `Ringkasan Guru`**: Ringkasan jadwal per individu guru untuk memudahkan masing-masing guru melihat jadwal mengajarnya.
  4. **Sheet `Alokasi Mengajar`**: Rekap alokasi beban mengajar guru untuk memantau pemenuhan jam mengajar.  
* **Multistage Fallback Engine:** Jika jadwal utama buntu akibat parameter yang terlalu ketat, sistem otomatis menjalankan pencarian alternatif (meminjam guru dengan rumpun sejenis) agar jadwal tetap terbentuk tanpa *clash*.

---

## 5. ATURAN PENJADWALAN LENGKAP (*CONSTRAINTS*)

Sistem penjadwalan ini bekerja berdasarkan parameter matematika yang terbagi menjadi dua kategori utama:

### A. Aturan Mutlak (*Hard Constraints* - Toleransi Pelanggaran 0%)
Ini adalah batasan wajib yang tidak boleh dilanggar. Jika dilanggar, sistem akan mendeteksi status kegagalan jadwal (*Infeasible*):
1. **No Teacher Clash (Bebas Bentrok Guru):** Seorang guru tidak boleh mengajar di dua kelas berbeda pada hari dan waktu dinding (*wall-clock*) yang sama. Aturan ini juga berlaku ketat untuk guru yang mengajar lintas shift (Pagi dan Siang) agar tidak terjadi tumpang tindih waktu transisi.
2. **No Class Clash (Bebas Bentrok Kelas):** Sebuah kelas tidak boleh menerima lebih dari satu mata pelajaran pada hari dan jam pelajaran (JP) yang sama.
3. **Kesesuaian Waktu & Shift (*Teacher Availability*):** Guru hanya boleh dijadwalkan mengajar pada hari dan shift yang telah ditentukan dalam ketersediaan mereka (`hari_tersedia_pagi` / `hari_tersedia_siang`).
4. **Batas Beban Mengajar Maksimal (*Max JP*):** Jumlah JP mengajar seorang guru per minggu tidak boleh melampaui batas maksimal (`max_jp`) yang ditentukan untuk menjaga kesehatan kerja.
5. **Batas Beban Mengajar Minimal (*Min JP*):** Jika seorang guru ditugaskan, beban mengajar minimal per minggu tidak boleh kurang dari `min_jp` (misalnya untuk memenuhi sertifikasi).
6. **Aturan Khusus Olahraga (Penjasorkes):**
   * Wajib dialokasikan langsung **2 JP berturut-turut** pada hari yang sama.
   * **Dilarang keras melompati jam istirahat** (tidak boleh terpotong jeda antara JP 4 dan JP 5).
7. **Batas Shift Kelas (*Shift Boundary*):** Kelas shift Pagi hanya boleh dijadwalkan pada slot pagi, dan kelas Siang hanya pada slot siang. Pada hari Sabtu, shift siang dibatasi maksimal 6 JP (tidak ada JP ke-7).
8. **Maksimal 40 JP per Kelas:** Total durasi mata pelajaran untuk satu kelas dibatasi maksimal 40 JP per minggu.
9. **Satu Guru per Alokasi:** Suatu slot alokasi mata pelajaran di kelas tertentu tidak boleh dibagi kepada dua guru berbeda. Harus diselesaikan oleh satu orang guru yang sama demi konsistensi KBM.
10. **Penguncian Guru Mutlak (*Fixed Teacher*):** Jika bagian kurikulum mengunci guru tertentu untuk kelas dan mapel tertentu, sistem wajib mematuhinya dan dilarang mencarikan pengganti jika terjadi bentrok.

### B. Aturan Fleksibel (*Soft Constraints* / Optimasi - Berdasarkan Penalti)
Aturan ini dapat disesuaikan atau dilanggar oleh sistem jika kondisi slot waktu sangat kritis, namun sistem akan selalu mengusahakan hasil terbaik dengan penalti minimal:
1. **Blok Jam Mengajar Produktif:** Mata pelajaran Produktif dengan durasi panjang ($\ge 4$ JP) diutamakan untuk diletakkan berurutan (*block time*) pada hari yang sama agar praktikum tidak terputus.
2. **Pemerataan Beban Guru:** Solver secara aktif menyeimbangkan pembagian jam mengajar di antara guru-guru yang berada dalam satu *pool* kompetensi mata pelajaran sejenis agar adil.
3. **Anti-Tumpuk Jam Harian (Penyebaran Jadwal):** Menghindari penumpukan mengajar guru lebih dari 5 JP pada satu hari yang sama jika hari ketersediaan lainnya masih kosong.
4. **Prioritas Guru Beban Tinggi:** Guru dengan target beban kerja minimal (`min_jp`) yang tinggi akan didahulukan oleh sistem dalam pencarian slot mengajar yang kosong.

---

## 6. PERMOHONAN REVIEW & PRESENTASI

Melalui proposal ini, saya memohon ketersediaan Bapak Samsul Huda, S.Pd selaku Wakakurikulum untuk:
1. **Mereview Output Hasil Jadwal:** Saya memohon kesediaan Bapak untuk memeriksa kesesuaian, estetika, dan kepraktisan jadwal hasil output aplikasi ini (1 file Excel berisi 4 sheet terlampir).
2. **Uji Coba Implementasi Internal:** Rencana utama kami adalah menerapkan aplikasi ini untuk menyusun jadwal pelajaran di **sekolah kita** secara riil pada periode mendatang.
3. **Rencana Kerjasama Eksternal:** Apabila aplikasi ini terbukti sukses dan mempermudah kerja kurikulum sekolah kita, kami merencanakan untuk menawarkan dan menyebarluaskan sistem ini ke **sekolah-sekolah lain** (baik rekan sejawat, kenalan Bapak Samsul Huda, S.Pd., maupun jaringan SMK lainnya) sebagai bentuk kolaborasi profesional dan kerja sama strategis.
4. **Permohonan Waktu Presentasi & Masukan:**
   * Jika Bapak memiliki waktu luang kapan saja, saya sangat berharap dapat **mempresentasikan cara kerja sistem dan demo langsung** di hadapan Bapak.
   * Saya sangat mengharapkan masukan, kritik, serta saran dari Bapak demi penyempurnaan fitur dan logika aplikasi ini agar benar-benar sesuai dengan dinamika kebutuhan riil di lapangan.

---

## 7. PENUTUP

Demikian proposal pengajuan ini saya sampaikan. Integrasi teknologi optimasi matematika ini diharapkan dapat merevolusi proses penyusunan jadwal sekolah kita menjadi jauh lebih cepat, akurat, dan transparan, sekaligus membuka peluang kerja sama yang lebih luas dengan sekolah-sekolah mitra.

Atas perhatian, waktu, dan arahan yang Bapak/Ibu Wakakurikulum berikan, saya ucapkan terima kasih yang sebesar-besarnya.

**Hormat Saya,**



**Sutrisno**
*Staf Pengajar / Pengembang Sistem Penjadwalan*
