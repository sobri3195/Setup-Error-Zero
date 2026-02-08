# Setup-Error Zero

Prototype aplikasi **React + Python** untuk:

> **AI Deteksi dan Rekomendasi Koreksi Setup Real-time dari Portal Imaging/CBCT**

**Author:** dr. Muhammad Sobri Maulana

## Latar Belakang (PICO)

- **P (Population):** Pasien radioterapi dengan IGRT (portal imaging dan/atau CBCT).
- **I (Intervention):** AI untuk identifikasi translasi/rotasi dan rekomendasi koreksi setup secara real-time.
- **C (Comparison):** Review manual oleh RTT/terapis radiasi dan/atau dokter.
- **O (Outcome):** Residual setup error setelah koreksi, kebutuhan repeat imaging, waktu di mesin, dan insiden near-miss terkait setup.

## Fitur Prototype

- Input error translasi (Tx, Ty, Tz) dalam mm.
- Input error rotasi (Rx, Ry, Rz) dalam derajat.
- API Python menghitung **risk score** sederhana dan memberikan rekomendasi:
  - Koreksi wajib + repeat imaging.
  - Koreksi direkomendasikan + validasi manual.
  - Monitoring tanpa repeat imaging.
- Frontend React menampilkan hasil rekomendasi secara real-time.

## Struktur Proyek

- `app.py` → Backend Python (standard library HTTP server) + endpoint API rekomendasi.
- `templates/index.html` → Frontend React (CDN) untuk input dan visualisasi rekomendasi.
- `requirements.txt` → Dependensi Python.

## Cara Menjalankan

```bash
python -m venv .venv
source .venv/bin/activate
python app.py
```

Buka browser: `http://127.0.0.1:5000`

## Catatan Klinis

- Output ini adalah **decision support**, bukan pengganti keputusan klinis.
- Semua rekomendasi AI wajib melalui verifikasi RTT/terapis radiasi dan/atau dokter sebelum tindakan.
- Model scoring saat ini adalah baseline rule-based untuk demonstrasi, dan dapat dikembangkan menjadi model ML/DL berbasis data klinis aktual.
