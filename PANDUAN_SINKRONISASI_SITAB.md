# Panduan Integrasi Client SITAB ke Laravel LMS

Dokumen ini berisi spesifikasi API Receiver pada sisi LMS Laravel guna mengirimkan (*push*) data jadwal pelajaran dan master data dari aplikasi **SITAB**.

---

## 1. DETAIL ENDPOINT API

*   **HTTP Method**: `POST`
*   **Endpoint URL**: `https://www.lms11maret.xyz/api/v1/sync-all` atau `https://bekasi.lms11maret.xyz/api/v1/sync-all` (sesuaikan domain server target)
*   **Headers**:
    ```http
    Content-Type: application/json
    Authorization: Bearer token_rahasia_sitab_11maret
    User-Agent: Mozilla/5.0 ... (Untuk menghindari pemblokiran firewall/Cloudflare VPS)
    ```

> [!NOTE]
> **Toleransi URL Input**: 
> Backend SITAB dilengkapi dengan pembersih URL otomatis. Pengguna dapat memasukkan URL halaman login admin (misal `https://bekasi.lms11maret.xyz/login/admin`) atau domain utama (`https://www.lms11maret.xyz`) pada menu Pengaturan, dan SITAB secara otomatis akan memotong path belakang dan menyusun ulang ke endpoint API `/api/v1/sync-all`.


---

## 2. SPESIFIKASI FORMAT JSON (PAYLOAD)

Format request body wajib berupa JSON objek dengan kunci-kunci berikut:

```json
{
  "teachers": [
    {
      "kode_guru": 101,
      "nama_guru": "REZA PATRIOTA PUTRA, S.Kom",
      "hari_tersedia": ["SENIN", "SELASA", "RABU"],
      "shift_pagi": true,
      "shift_siang": true,
      "hari_tersedia_pagi": ["SENIN", "SELASA"],
      "hari_tersedia_siang": ["RABU"],
      "min_jp": 2,
      "max_jp": 40,
      "allowed_jp_pagi": null,
      "allowed_jp_siang": null,
      "no_wa": "08123456789"
    }
  ],
  "classes": [
    {
      "nama_kelas": "X TKJ 1",
      "shift_operasional": "PAGI",
      "tingkat": "X",
      "jurusan": "TKJ"
    }
  ],
  "subjects": [
    {
      "nama_mapel": "Matematika",
      "kategori_mapel": "UMUM",
      "tingkat": null,
      "jurusan": null
    }
  ],
  "teacher_subjects": [
    {
      "kode_guru": 101,
      "nama_mapel": "Matematika"
    }
  ],
  "class_subjects": [
    {
      "nama_kelas": "X TKJ 1",
      "nama_mapel": "Matematika",
      "durasi_jp": 4,
      "kode_guru_mutlak": null
    }
  ],
  "timetable": [
    {
      "nama_kelas": "X TKJ 1",
      "nama_mapel": "Matematika",
      "kode_guru": 101,
      "hari": "SENIN",
      "jam_ke": 1,
      "is_fallback": false,
      "original_guru_kode": null
    }
  ]
}
```

### Penjelasan Fields Penting:
*   `teachers.hari_tersedia` / `hari_tersedia_pagi` / `hari_tersedia_siang`: Berupa array string nama hari kapital (`["SENIN", "SELASA"]`).
*   `teacher_subjects`: Tabel pivot yang menghubungkan Guru ke Kualifikasi Mata Pelajaran yang diampu menggunakan `kode_guru` dan `nama_mapel`.
*   `class_subjects.kode_guru_mutlak`: Kode guru yang wajib mengampu mapel tersebut di kelas terkait (opsional/nullable).
*   `timetable`: Jadwal aktif hasil bentukan solver.
    *   `is_fallback`: Set `true` jika slot ini diisi oleh guru pengganti (substitusi).
    *   `original_guru_kode`: Kode guru asli yang seharusnya mengajar sebelum digantikan (opsional/nullable).

---

## 3. CONTOH IMPLEMENTASI SINKRONISASI

### A. Menggunakan cURL
```bash
curl -X POST http://127.0.0.1:8000/api/v1/sync-all \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token_rahasia_sitab_11maret" \
  -d @payload.json
```

### B. Menggunakan JavaScript (Axios)
```javascript
const axios = require('axios');

const payload = {
  teachers: [...],
  classes: [...],
  subjects: [...],
  teacher_subjects: [...],
  class_subjects: [...],
  timetable: [...]
};

axios.post('http://127.0.0.1:8000/api/v1/sync-all', payload, {
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token_rahasia_sitab_11maret'
  }
})
.then(response => {
  console.log('Sync Success:', response.data.message);
})
.catch(error => {
  console.error('Sync Failed:', error.response ? error.response.data : error.message);
});
```

### C. Menggunakan Python (Requests)
```python
import requests

url = "http://127.0.0.1:8000/api/v1/sync-all"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer token_rahasia_sitab_11maret"
}

payload = {
    "teachers": [],
    "classes": [],
    "subjects": [],
    "teacher_subjects": [],
    "class_subjects": [],
    "timetable": []
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Sync Success:", response.json().get("message"))
else:
    print("Sync Failed:", response.status_code, response.text)
```

---

## 4. RESPONSES API

*   **HTTP 200 OK (Success)**:
    ```json
    {
      "status": "SUCCESS",
      "message": "Seluruh data master dan jadwal berhasil disinkronisasi ke LMS Laravel!"
    }
    ```
*   **HTTP 401 Unauthorized (Invalid / Missing Token)**:
    ```json
    {
      "message": "Unauthorized Access - Invalid Token"
    }
    ```
*   **HTTP 500 Internal Server Error (Database Error / Invalid Relationship)**:
    ```json
    {
      "status": "ERROR",
      "message": "Gagal melakukan sinkronisasi database LMS: <pesan_error>"
    }
    ```
