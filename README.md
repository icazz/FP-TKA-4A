# Final Project Teknologi Komputasi Awan - 4A

## Anggota Kelompok

| NRP | Nama |
|------------|--------------------------|
| 5027241008 | Paundra Pujo |
| 5027241022 | Ardhi Putra Pradana |
| 5027241048 | Afrizan Rasya |
| 5027241058 | Ica Zika Hamizah |
| 5027241064 | Hanif Mawla Faizi |
| 5027241093 | M. Atha Tajuddin |

---

## Struktur Repository

```
FP-TKA-4A/
├── README.md                   ← Laporan utama project
├── SOAL.md                     ← Dokumen soal final project
├── Resources/
│   ├── BE/                     ← Backend (Order Processing Service)
│   │   ├── app.py              ← Aplikasi Flask REST API utama
│   │   ├── requirements.txt    ← Daftar dependensi Python
│   │   └── Dockerfile          ← Docker image untuk backend
│   ├── FE/                     ← Frontend (Web UI)
│   │   ├── index.html          ← Halaman antarmuka pengguna
│   │   ├── styles.css          ← Stylesheet tampilan web
│   │   ├── Dockerfile          ← Docker image untuk frontend
│   │   └── entrypoint.sh       ← Script entrypoint container FE
│   ├── DB/                     ← Konfigurasi & seed data database
│   │   ├── generate_dump.py    ← Script untuk generate data awal MongoDB
│   │   ├── dump/               ← Folder dump data MongoDB
│   │   └── README.md           ← Panduan setup database
│   └── Test/
│       └── locustfile.py       ← Script load testing dengan Locust
├── Result/                     ← Hasil pengujian & screenshot
│   └── README.md               ← Dokumentasi hasil pengujian
└── infra/                      ← Konfigurasi infrastruktur cloud
    ├── apps/                   ← Konfigurasi deployment aplikasi
    ├── db/                     ← Konfigurasi deployment database
    └── setup.sh                ← Script otomasi setup server
```

---
