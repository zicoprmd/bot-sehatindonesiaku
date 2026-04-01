# Bot Sehat Indonesia Ku - CKG

Bot otomatis untuk penginputan pelayanan **CKG (Cekan Kesehatan Gratis)** di [sehatindonesiaku.kemkes.go.id](https://sehatindonesiaku.kemkes.go.id).

## Fitur

- **Auto login** - Gunakan session Edge yang sudah ada
- **Auto skip** - Jika form skrining tidak applicable (usia), langsung skip
- **Resume** - Jika interrupted, bot akan lanjut dari pasien terakhir
- **Progress tracking** - Simpan progress ke file
- **Logging** - Semua aktivitas dicatat ke `bot_sehatindo.log`

## Struktur File

```
├── sehatindo.py       # Bot utama
├── datasehat.xlsx     # Data pasien (input)
├── progress.txt       # Progress resume (auto-generated)
├── bot_sehatindo.log  # Log aktivitas (auto-generated)
└── README.md          # Dokumentasi
```

## Format Data Excel

File `datasehat.xlsx` harus memiliki sheet bernama `data` dengan kolom:

| Kolom | Deskripsi |
|-------|-----------|
| `nama` | NIK pasien |
| `BB` | Berat Badan (kg) |
| `TB` | Tinggi Badan (cm) |
| `LP` | Lingkar Perut (cm) |
| `GDS` | Gula Darah Sewaktu (mg/dL) |
| `sistol` | Tekanan Darah Sistol (mmHg) |
| `diastol` | Tekanan Darah Diastol (mmHg) |

## Cara Pakai

### 1. Install Dependencies

```bash
pip install selenium pandas openpyxl
```

### 2. Siapkan Data Excel

- Buat/edit `datasehat.xlsx` dengan format di atas
- Pastikan Edge sudah terinstall

### 3. Jalankan Bot

```bash
python sehatindo.py
```

### 4. Jika Butuh Login Manual

Jika session habis, bot akan pause dan minta Anda login manual + isi CAPTCHA di browser Edge. Tekan ENTER jika sudah di dashboard.

## Konfigurasi

Edit bagian atas `sehatindo.py` untuk mengubah:

```python
EDGE_PROFILE = r"C:\Users\ThinkPad\AppData\Local\Microsoft\Edge\User Data"
WEBSITE_URL = "https://sehatindonesiaku.kemkes.go.id"
EXCEL_FILE = "datasehat.xlsx"
PROGRESS_FILE = "progress.txt"
```

## Skrining yang Diproses

### Demografi
- Demografi Dewasa Perempuan
- Demografi Dewasa Laki-Laki
- Demografi Lansia

### Survey (auto-skip jika tidak applicable)
- Faktor Risiko Kanker Usus
- Faktor Risiko Malaria
- Faktor Risiko TB - Dewasa & Lansia
- Gejala Cemas Remaja
- Gejala Depresi Remaja
- Kesehatan Reproduksi Putra - Anak Sekolah
- Kelayakan Tes Kebugaran
- Hati / Faktor Risiko Hepatitis
- Kanker Leher Rahim
- Kesehatan Jiwa
- Penapisan Risiko Kanker Paru
- Perilaku Merokok
- Tingkat Aktivitas Fisik

### Input Data
- BB, TB, LP (Berat, Tinggi, Lingkar Perut)
- Gula Darah
- Tekanan Darah

## Troubleshooting

### Tombol Tidak Ter klik
- Cek apakah website sudah load complete
- Cek koneksi internet
- Coba restart browser

### Salah Klik Pasien
- Cek apakah data NIK di Excel benar
- Cek apakah ada karakter khusus di nama

### Progress Tertahan
- Hapus/edit `progress.txt` untuk restart dari awal

## Stop Bot

Tekan `Ctrl+C` untuk interrupt. Bot akan berhenti dan progress tersimpan - bisa resume下次运行时.
