"""
models.py — Pydantic request/response models
Schema sesuai database: class_subjects tanpa id_guru,
timetable via id_class_subject.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


# ─────────────────────────────────────────────
# Teachers
# ─────────────────────────────────────────────

class TeacherBase(BaseModel):
    nama_guru:           str
    kode_guru:           int
    hari_tersedia:       List[str]
    shift_pagi:          bool               = True
    shift_siang:         bool               = True
    hari_tersedia_pagi:  Optional[List[str]] = None
    hari_tersedia_siang: Optional[List[str]] = None
    min_jp:              Optional[int]      = None
    max_jp:              Optional[int]      = None
    allowed_jp_pagi:     Optional[dict[str, List[int]]] = None
    allowed_jp_siang:    Optional[dict[str, List[int]]] = None

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id_guru: int
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Classes
# ─────────────────────────────────────────────

class ClassBase(BaseModel):
    nama_kelas:        str
    shift_operasional: str = Field(..., pattern="^(PAGI|SIANG)$")
    tingkat:           Optional[str] = None
    jurusan:           Optional[str] = None

class ClassCreate(ClassBase):
    pass

class Class(ClassBase):
    id_kelas: int
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Subjects
# ─────────────────────────────────────────────

class SubjectBase(BaseModel):
    nama_mapel:    str
    kategori_mapel: str
    tingkat:       Optional[str] = None
    jurusan:       Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id_mapel: int
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Class Subjects (Alokasi Kelas-Mapel)
# TIDAK menyimpan id_guru — normalized ke teacher_subjects
# ─────────────────────────────────────────────

class ClassSubjectBase(BaseModel):
    id_kelas:  int
    id_mapel:  int
    durasi_jp: int
    id_guru_mutlak: Optional[int] = None

class ClassSubjectCreate(ClassSubjectBase):
    pass

class ClassSubject(ClassSubjectBase):
    id_class_subject: int
    nama_kelas:       Optional[str] = None
    nama_mapel:       Optional[str] = None
    nama_guru_mutlak: Optional[str] = None
    class Config:
        from_attributes = True


class AllocationUpdate(BaseModel):
    durasi_jp: int
    id_guru_mutlak: Optional[int] = None


class AllocationCopy(BaseModel):
    id_kelas_asal: int
    id_kelas_tujuan: int


# ─────────────────────────────────────────────
# Teacher Subjects (Penugasan / Kualifikasi Guru)
# ─────────────────────────────────────────────

class TeacherSubjectBase(BaseModel):
    id_guru:  int
    id_mapel: int

class TeacherSubjectCreate(TeacherSubjectBase):
    pass

class TeacherSubject(TeacherSubjectBase):
    id_teacher_subject: int
    nama_guru:          Optional[str] = None
    kode_guru:          Optional[int] = None
    nama_mapel:         Optional[str] = None
    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────

class SettingsUpdate(BaseModel):
    spreadsheet_id:   str
    credentials_json: str
