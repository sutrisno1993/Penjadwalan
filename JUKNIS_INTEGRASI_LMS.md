# Petunjuk Integrasi & Spesifikasi Penerimaan Data SITAB pada Laravel LMS

Dokumen ini berisi spesifikasi teknis dan panduan implementasi untuk membuat **API Receiver** pada aplikasi Backend Laravel (LMS) guna menangkap data master dan jadwal pelajaran yang dikirimkan (*pushed*) dari SITAB.

Letakkan file ini di folder root proyek Laravel Anda agar asisten AI coding Laravel Anda dapat membaca, memahami, dan memprogram seluruh database migrasi, model, routing, dan controller secara otomatis.

---

## 1. STRUKTUR DATABASE (MIGRATIONS)

Buat file migrasi di Laravel secara berurutan agar hubungan foreign key terbuat tanpa error. Kita mendefinisikan 6 tabel master yang strukturnya **identik** dengan skema PostgreSQL/Supabase pada SITAB.

### A. Migrasi Tabel `teachers` (Guru)
File: `database/migrations/2026_06_21_000001_create_teachers_table.php`
```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('teachers', function (Blueprint $table) {
            $table->id('id_guru'); // Primary Key (BIGINT UNSIGNED)
            $table->string('nama_guru');
            $table->integer('kode_guru')->unique(); // Unique key untuk pencarian/sinkronisasi
            $table->json('hari_tersedia'); // Hari mengajar umum (cast ke array)
            $table->boolean('shift_pagi')->default(true);
            $table->boolean('shift_siang')->default(true);
            $table->json('hari_tersedia_pagi')->nullable();
            $table->json('hari_tersedia_siang')->nullable();
            $table->integer('min_jp')->default(2);
            $table->integer('max_jp')->default(60);
            $table->json('allowed_jp_pagi')->nullable();
            $table->json('allowed_jp_siang')->nullable();
            $table->string('no_wa')->nullable(); // Nomor WhatsApp untuk kirim jadwal
            
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('teachers');
    }
};
```

### B. Migrasi Tabel `classes` (Kelas)
File: `database/migrations/2026_06_21_000002_create_classes_table.php`
```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('classes', function (Blueprint $table) {
            $table->id('id_kelas');
            $table->string('nama_kelas')->unique(); // Unique key untuk pencarian/sinkronisasi
            $table->enum('shift_operasional', ['PAGI', 'SIANG']);
            $table->string('tingkat')->nullable();
            $table->string('jurusan')->nullable();
            
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('classes');
    }
};
```

### C. Migrasi Tabel `subjects` (Mata Pelajaran)
File: `database/migrations/2026_06_21_000003_create_subjects_table.php`
```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('subjects', function (Blueprint $table) {
            $table->id('id_mapel');
            $table->string('nama_mapel')->unique(); // Unique key untuk pencarian/sinkronisasi
            $table->string('kategori_mapel');
            $table->string('tingkat')->nullable();
            $table->string('jurusan')->nullable();
            
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('subjects');
    }
};
```

### D. Migrasi Tabel `teacher_subjects` (Kualifikasi/Penugasan Mapel Guru)
File: `database/migrations/2026_06_21_000004_create_teacher_subjects_table.php`
```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('teacher_subjects', function (Blueprint $table) {
            $table->id('id_teacher_subject');
            
            $table->unsignedBigInteger('id_guru');
            $table->foreign('id_guru')->references('id_guru')->on('teachers')->onDelete('cascade');
            
            $table->unsignedBigInteger('id_mapel');
            $table->foreign('id_mapel')->references('id_mapel')->on('subjects')->onDelete('cascade');
            
            $table->unique(['id_guru', 'id_mapel']);
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('teacher_subjects');
    }
};
```

### E. Migrasi Tabel `class_subjects` (Alokasi Jam Pelajaran)
File: `database/migrations/2026_06_21_000005_create_class_subjects_table.php`
```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('class_subjects', function (Blueprint $table) {
            $table->id('id_class_subject');
            
            $table->unsignedBigInteger('id_kelas');
            $table->foreign('id_kelas')->references('id_kelas')->on('classes')->onDelete('cascade');
            
            $table->unsignedBigInteger('id_mapel');
            $table->foreign('id_mapel')->references('id_mapel')->on('subjects')->onDelete('cascade');
            
            $table->integer('durasi_jp');
            
            // Guru Mutlak (nullable, jika diset)
            $table->unsignedBigInteger('id_guru_mutlak')->nullable();
            $table->foreign('id_guru_mutlak')->references('id_guru')->on('teachers')->onDelete('set null');
            
            $table->unique(['id_kelas', 'id_mapel']);
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('class_subjects');
    }
};
```

### F. Migrasi Tabel `timetable` (Jadwal Pelajaran Hasil Solver)
Kita menamakan tabel ini `timetable` (bukan jamak `timetables`) agar sinkron dengan database SITAB.
File: `database/migrations/2026_06_21_000006_create_timetable_table.php`
```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('timetable', function (Blueprint $table) {
            $table->id('id_timetable');
            
            $table->unsignedBigInteger('id_class_subject');
            $table->foreign('id_class_subject')->references('id_class_subject')->on('class_subjects')->onDelete('cascade');
            
            $table->string('hari');
            $table->integer('jam_ke');
            
            // Guru yang mengajar slot ini (bisa digantikan fallback)
            $table->unsignedBigInteger('id_guru')->nullable();
            $table->foreign('id_guru')->references('id_guru')->on('teachers')->onDelete('set null');
            
            $table->boolean('is_fallback')->default(false);
            
            $table->unsignedBigInteger('original_guru_id')->nullable();
            $table->foreign('original_guru_id')->references('id_guru')->on('teachers')->onDelete('set null');
            
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('timetable');
    }
};
```

---

## 2. MODEL ELOQUENT

Konfigurasikan model Eloquent agar memetakan kolom database dengan benar beserta relasi dan casting datanya.

### A. Model `Teacher`
File: `app/Models/Teacher.php`
```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Teacher extends Model
{
    protected $primaryKey = 'id_guru';
    protected $fillable = [
        'nama_guru', 'kode_guru', 'hari_tersedia', 
        'shift_pagi', 'shift_siang', 'hari_tersedia_pagi', 
        'hari_tersedia_siang', 'min_jp', 'max_jp', 
        'allowed_jp_pagi', 'allowed_jp_siang', 'no_wa'
    ];

    protected $casts = [
        'hari_tersedia' => 'array',
        'hari_tersedia_pagi' => 'array',
        'hari_tersedia_siang' => 'array',
        'allowed_jp_pagi' => 'array',
        'allowed_jp_siang' => 'array',
        'shift_pagi' => 'boolean',
        'shift_siang' => 'boolean',
        'min_jp' => 'integer',
        'max_jp' => 'integer',
    ];

    public function teacherSubjects()
    {
        return $this->hasMany(TeacherSubject::class, 'id_guru');
    }
}
```

### B. Model `Clas`
File: `app/Models/Clas.php`
```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Clas extends Model
{
    protected $table = 'classes';
    protected $primaryKey = 'id_kelas';
    protected $fillable = ['nama_kelas', 'shift_operasional', 'tingkat', 'jurusan'];
}
```

### C. Model `Subject`
File: `app/Models/Subject.php`
```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Subject extends Model
{
    protected $primaryKey = 'id_mapel';
    protected $fillable = ['nama_mapel', 'kategori_mapel', 'tingkat', 'jurusan'];
}
```

### D. Model `TeacherSubject`
File: `app/Models/TeacherSubject.php`
```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TeacherSubject extends Model
{
    protected $table = 'teacher_subjects';
    protected $primaryKey = 'id_teacher_subject';
    protected $fillable = ['id_guru', 'id_mapel'];

    public function teacher() {
        return $this->belongsTo(Teacher::class, 'id_guru');
    }
    public function subject() {
        return $this->belongsTo(Subject::class, 'id_mapel');
    }
}
```

### E. Model `ClassSubject`
File: `app/Models/ClassSubject.php`
```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ClassSubject extends Model
{
    protected $table = 'class_subjects';
    protected $primaryKey = 'id_class_subject';
    protected $fillable = ['id_kelas', 'id_mapel', 'durasi_jp', 'id_guru_mutlak'];

    public function class() {
        return $this->belongsTo(Clas::class, 'id_kelas');
    }
    public function subject() {
        return $this->belongsTo(Subject::class, 'id_mapel');
    }
    public function guruMutlak() {
        return $this->belongsTo(Teacher::class, 'id_guru_mutlak');
    }
}
```

### F. Model `Timetable`
File: `app/Models/Timetable.php`
```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Timetable extends Model
{
    protected $table = 'timetable';
    protected $primaryKey = 'id_timetable';
    protected $fillable = ['id_class_subject', 'hari', 'jam_ke', 'id_guru', 'is_fallback', 'original_guru_id'];

    protected $casts = [
        'is_fallback' => 'boolean',
        'jam_ke' => 'integer',
    ];

    public function classSubject() {
        return $this->belongsTo(ClassSubject::class, 'id_class_subject');
    }
    public function teacher() {
        return $this->belongsTo(Teacher::class, 'id_guru');
    }
    public function originalTeacher() {
        return $this->belongsTo(Teacher::class, 'original_guru_id');
    }
}
```

---

## 3. KONFIGURASI & KEAMANAN API

### A. Pengaturan File `.env`
Tambahkan API Key rahasia pada file `.env` Laravel Anda:
```env
SITAB_API_KEY=token_rahasia_sitab_11maret
```

### B. Pengaturan `config/services.php`
Daftarkan token tersebut agar mudah dibaca oleh Controller:
```php
'sitab' => [
    'key' => env('SITAB_API_KEY'),
],
```

### C. File `routes/api.php`
Daftarkan route endpoint penerimaan data:
```php
use App\Http\Controllers\Api\TimetableSyncController;

Route::post('/v1/sync-all', [TimetableSyncController::class, 'syncAll']);
```

> [!NOTE]
> **Normalisasi URL Otomatis di SITAB**:
> Pada menu Pengaturan di aplikasi SITAB, Anda dapat memasukkan URL situs utama (contoh: `https://www.lms11maret.xyz` atau `https://bekasi.lms11maret.xyz`) maupun URL login admin (seperti `https://bekasi.lms11maret.xyz/login/admin`).
> Backend SITAB secara otomatis memotong path belakang URL dan menyusun ulang request ke endpoint API receiver yang valid (`/api/v1/sync-all`).


---

## 4. CONTROLLER SINKRONISASI (API RECEIVER)

File: `app/Http/Controllers/Api/TimetableSyncController.php`

Controller ini mengimplementasikan strategi **Sync & Purge** dalam satu Database Transaction. 
Data lama yang tidak ada di pengiriman terbaru akan dihapus secara aman demi menjaga database tetap sinkron dengan SITAB, tanpa merusak foreign key.

```php
<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Models\Teacher;
use App\Models\Clas;
use App\Models\Subject;
use App\Models\TeacherSubject;
use App\Models\ClassSubject;
use App\Models\Timetable;

class TimetableSyncController extends Controller
{
    public function syncAll(Request $request)
    {
        // 1. Validasi Token Bearer
        $token = $request->bearerToken();
        if ($token !== config('services.sitab.key')) {
            return response()->json(['message' => 'Unauthorized Access - Invalid Token'], 401);
        }

        $data = $request->all();

        try {
            DB::transaction(function () use ($data) {
                
                // --- A. SYNC GURU ---
                $activeTeacherIds = [];
                if (isset($data['teachers'])) {
                    foreach ($data['teachers'] as $t) {
                        $teacher = Teacher::updateOrCreate(
                            ['kode_guru' => $t['kode_guru']],
                            [
                                'nama_guru'           => $t['nama_guru'],
                                'hari_tersedia'       => $t['hari_tersedia'],
                                'shift_pagi'          => $t['shift_pagi'],
                                'shift_siang'         => $t['shift_siang'],
                                'hari_tersedia_pagi'  => $t['hari_tersedia_pagi'] ?? null,
                                'hari_tersedia_siang' => $t['hari_tersedia_siang'] ?? null,
                                'min_jp'              => $t['min_jp'] ?? 2,
                                'max_jp'              => $t['max_jp'] ?? 60,
                                'allowed_jp_pagi'     => $t['allowed_jp_pagi'] ?? null,
                                'allowed_jp_siang'    => $t['allowed_jp_siang'] ?? null,
                                'no_wa'               => $t['no_wa'] ?? null
                            ]
                        );
                        $activeTeacherIds[] = $teacher->id_guru;
                    }
                }

                // --- B. SYNC KELAS ---
                $activeClassIds = [];
                if (isset($data['classes'])) {
                    foreach ($data['classes'] as $c) {
                        $class = Clas::updateOrCreate(
                            ['nama_kelas' => $c['nama_kelas']],
                            [
                                'shift_operasional' => $c['shift_operasional'],
                                'tingkat'           => $c['tingkat'] ?? null,
                                'jurusan'           => $c['jurusan'] ?? null
                            ]
                        );
                        $activeClassIds[] = $class->id_kelas;
                    }
                }

                // --- C. SYNC MAPEL ---
                $activeSubjectIds = [];
                if (isset($data['subjects'])) {
                    foreach ($data['subjects'] as $s) {
                        $subject = Subject::updateOrCreate(
                            ['nama_mapel' => $s['nama_mapel']],
                            [
                                'kategori_mapel' => $s['kategori_mapel'],
                                'tingkat'        => $s['tingkat'] ?? null,
                                'jurusan'        => $s['jurusan'] ?? null
                            ]
                        );
                        $activeSubjectIds[] = $subject->id_mapel;
                    }
                }

                // --- D. SYNC PENUGASAN GURU (TEACHER SUBJECTS) ---
                // Karena relasi pivot, kita kumpulkan id yang aktif
                $activeTeacherSubjectIds = [];
                if (isset($data['teacher_subjects'])) {
                    foreach ($data['teacher_subjects'] as $ts) {
                        // Cari guru & mapel berdasarkan unique key (kode_guru & nama_mapel)
                        $tModel = Teacher::where('kode_guru', $ts['kode_guru'])->first();
                        $sModel = Subject::where('nama_mapel', $ts['nama_mapel'])->first();

                        if ($tModel && $sModel) {
                            $pivot = TeacherSubject::updateOrCreate(
                                [
                                    'id_guru'  => $tModel->id_guru,
                                    'id_mapel' => $sModel->id_mapel
                                ]
                            );
                            $activeTeacherSubjectIds[] = $pivot->id_teacher_subject;
                        }
                    }
                }

                // --- E. SYNC ALOKASI KURIKULUM (CLASS SUBJECTS) ---
                $activeClassSubjectIds = [];
                if (isset($data['class_subjects'])) {
                    foreach ($data['class_subjects'] as $cs) {
                        $cModel = Clas::where('nama_kelas', $cs['nama_kelas'])->first();
                        $sModel = Subject::where('nama_mapel', $cs['nama_mapel'])->first();

                        if ($cModel && $sModel) {
                            // Cari guru mutlak jika didefinisikan
                            $gMutlakModel = null;
                            if (isset($cs['kode_guru_mutlak']) && $cs['kode_guru_mutlak']) {
                                $gMutlakModel = Teacher::where('kode_guru', $cs['kode_guru_mutlak'])->first();
                            }

                            $allocation = ClassSubject::updateOrCreate(
                                [
                                    'id_kelas' => $cModel->id_kelas,
                                    'id_mapel' => $sModel->id_mapel
                                ],
                                [
                                    'durasi_jp'       => $cs['durasi_jp'],
                                    'id_guru_mutlak'  => $gMutlakModel ? $gMutlakModel->id_guru : null
                                ]
                            );
                            $activeClassSubjectIds[] = $allocation->id_class_subject;
                        }
                    }
                }

                // --- F. PURGE JADWAL LAMA (TIMETABLE) & PIVOT LAIN ---
                // Truncate timetable karena jadwal akan ditulis ulang sepenuhnya
                Timetable::truncate();

                // Hapus alokasi kurikulum yang sudah tidak ada di pengiriman terbaru
                ClassSubject::whereNotIn('id_class_subject', $activeClassSubjectIds)->delete();

                // Hapus penugasan guru yang sudah tidak ada
                TeacherSubject::whereNotIn('id_teacher_subject', $activeTeacherSubjectIds)->delete();

                // Hapus mapel, kelas, dan guru lama yang sudah tidak aktif di SITAB
                Subject::whereNotIn('id_mapel', $activeSubjectIds)->delete();
                Clas::whereNotIn('id_kelas', $activeClassIds)->delete();
                Teacher::whereNotIn('id_guru', $activeTeacherIds)->delete();

                // --- G. SYNC JADWAL BARU (TIMETABLE) ---
                if (isset($data['timetable'])) {
                    foreach ($data['timetable'] as $slot) {
                        // Cari alokasi pelajaran terkait (kelas + mapel)
                        $cModel = Clas::where('nama_kelas', $slot['nama_kelas'])->first();
                        $sModel = Subject::where('nama_mapel', $slot['nama_mapel'])->first();

                        if ($cModel && $sModel) {
                            $csModel = ClassSubject::where([
                                'id_kelas' => $cModel->id_kelas,
                                'id_mapel' => $sModel->id_mapel
                            ])->first();

                            if ($csModel) {
                                // Cari guru pengampu aktif di slot ini
                                $gModel = null;
                                if (isset($slot['kode_guru']) && $slot['kode_guru']) {
                                    $gModel = Teacher::where('kode_guru', $slot['kode_guru'])->first();
                                }

                                // Cari guru asli jika terjadi substitusi/fallback
                                $gOrigModel = null;
                                if (isset($slot['original_guru_kode']) && $slot['original_guru_kode']) {
                                    $gOrigModel = Teacher::where('kode_guru', $slot['original_guru_kode'])->first();
                                }

                                Timetable::create([
                                    'id_class_subject' => $csModel->id_class_subject,
                                    'hari'             => $slot['hari'],
                                    'jam_ke'           => $slot['jam_ke'],
                                    'id_guru'          => $gModel ? $gModel->id_guru : null,
                                    'is_fallback'      => $slot['is_fallback'] ?? false,
                                    'original_guru_id' => $gOrigModel ? $gOrigModel->id_guru : null,
                                ]);
                            }
                        }
                    }
                }
            });

            return response()->json([
                'status'  => 'SUCCESS',
                'message' => 'Seluruh data master dan jadwal berhasil disinkronisasi ke LMS Laravel!'
            ], 200);

        } catch (\Exception $e) {
            return response()->json([
                'status'  => 'ERROR',
                'message' => 'Gagal melakukan sinkronisasi database LMS: ' . $e->getMessage()
            ], 500);
        }
    }
}
```

---

## 5. STRUKTUR PAYLOAD JSON DARI SITAB

Berikut adalah format JSON lengkap yang dikirimkan oleh SITAB saat menekan tombol **"Kirim Semua Data ke LMS"**:

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

---

## 6. KEUNTUNGAN DECOUPLING INI (MENGAPA MEMAKAI POLA INI?)
1. **Bebas Error Dialek Database**: SITAB memakai PostgreSQL/Supabase sedangkan Laravel LMS biasanya memakai MySQL. Dengan integrasi REST API JSON, dialek SQL tidak saling bentrok.
2. **Keamanan Port Database**: Server Supabase atau MySQL Laravel tidak perlu diekspos ke publik. Cukup buka port HTTP standar (80/443).
3. **Penyimpanan Riwayat Nilai & Tugas di LMS Aman**: Tabel relasi penugasan khusus LMS seperti `students` (Siswa), `grades` (Nilai), atau `assignments` (Tugas) dapat Anda buat di Laravel secara terpisah dengan relasi mengacu pada `id_kelas` di tabel `classes` atau `id_timetable` di tabel `timetable`. Ketika SITAB melakukan *purge*, data master hanya di-*update*, dan tidak menghapus relasi jika didefinisikan dengan `onDelete('restrict')` atau `onDelete('no action')`.
