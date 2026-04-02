# Setup-Error Zero

> Prototype aplikasi decision-support radioterapi untuk analisis setup error translasi & rotasi, dilengkapi rekomendasi koreksi berbasis skor risiko.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![HTTPServer](https://img.shields.io/badge/Backend-Standard%20Library-green)
![React](https://img.shields.io/badge/Frontend-React%2018-61DAFB)
![Status](https://img.shields.io/badge/Status-Prototype-orange)

---

## Daftar Isi
- [Ringkasan Proyek](#ringkasan-proyek)
- [Analisa Kodebase (Detail & Mendalam)](#analisa-kodebase-detail--mendalam)
- [Fitur Utama](#fitur-utama)
- [Fungsi Sistem](#fungsi-sistem)
- [Arsitektur Aplikasi](#arsitektur-aplikasi)
- [Alur Proses Data](#alur-proses-data)
- [Spesifikasi API](#spesifikasi-api)
- [Logika Perhitungan Risk Score](#logika-perhitungan-risk-score)
- [Validasi & Batasan](#validasi--batasan)
- [Struktur Proyek](#struktur-proyek)
- [Cara Menjalankan](#cara-menjalankan)
- [Contoh Uji Endpoint](#contoh-uji-endpoint)
- [Roadmap Pengembangan](#roadmap-pengembangan)
- [Kontributor & Kontak](#kontributor--kontak)
- [Dukungan / Donasi](#dukungan--donasi)
- [Disclaimer Klinis](#disclaimer-klinis)

---

## Ringkasan Proyek
**Setup-Error Zero** adalah prototipe aplikasi web ringan yang memproses parameter setup error radioterapi (Tx, Ty, Tz, Rx, Ry, Rz), menghitung skor risiko gabungan, lalu menghasilkan rekomendasi tindakan koreksi setup.

Aplikasi dirancang sebagai **decision support tool** agar tim klinis dapat memperoleh estimasi awal tindakan sebelum beam-on, dengan tetap mengutamakan validasi profesional oleh RTT/terapis radiasi/dokter.

---

## Analisa Kodebase (Detail & Mendalam)

### 1) Backend (`app.py`)
Backend menggunakan `http.server` bawaan Python, sehingga deployment sederhana tanpa framework tambahan.

#### Komponen kunci:
- **Konfigurasi server**
  - Host: `0.0.0.0`
  - Port: `5000`
- **Handler utama:** `SetupErrorZeroHandler(BaseHTTPRequestHandler)`
  - `do_GET()`
    - Menyajikan `templates/index.html` pada `/` atau `/index.html`.
    - Route lain mengembalikan `404 JSON`.
  - `do_POST()`
    - Endpoint aktif: `/api/recommend`.
    - Parsing payload JSON berisi 6 parameter setup error.
    - Menghitung:
      - `translation_error = |tx| + |ty| + |tz|`
      - `rotation_error = |rx| + |ry| + |rz|`
      - `risk_score = 0.7 * translation_error + 0.3 * rotation_error`
    - Menentukan rekomendasi tindakan berdasarkan threshold skor.
    - Mengembalikan output JSON lengkap: skor, rekomendasi aksi, dan arah koreksi.
- **Fungsi `run_server()`**
  - Menjalankan server sinkron (`serve_forever`).

#### Temuan teknis:
- Implementasi sangat ringan dan cepat dijalankan.
- Endpoint bersifat deterministik/rule-based (mudah diaudit).
- Belum ada validasi numerik mendalam (contoh: tipe tak valid non-castable bisa memunculkan exception).
- Belum ada logging terstruktur, auth, atau CORS policy untuk integrasi skala lanjut.

### 2) Frontend (`templates/index.html`)
Frontend disusun sebagai satu file HTML dengan React 18 via CDN + Babel standalone.

#### Komponen kunci:
- **State utama**
  - `form` menyimpan 6 input numerik.
  - `result` menyimpan respons endpoint.
  - `activeTab` untuk navigasi mobile (`input`, `hasil`, `info`).
- **Aksi submit**
  - `fetch('/api/recommend', { method: 'POST', ... })`
  - Menampilkan hasil rekomendasi secara langsung.
- **UI/UX**
  - Layout card responsif.
  - Grid input 3 kolom desktop / 2 kolom mobile.
  - Bottom mobile navigation untuk akses cepat tab.

#### Temuan teknis:
- Arsitektur single-page sederhana, minim dependensi build.
- Cocok untuk PoC cepat.
- Belum ada handling error jaringan/API yang robust (misal timeout, retry, fallback state).

### 3) Dependensi (`requirements.txt`)
- Tidak ada dependensi eksternal Python.
- Menurunkan kompleksitas setup lingkungan.

---

## Fitur Utama
- Input setup error translasi: **Tx, Ty, Tz (mm)**.
- Input setup error rotasi: **Rx, Ry, Rz (°)**.
- Perhitungan **risk score** gabungan translasi-rotasi.
- Rekomendasi tindakan koreksi berbasis threshold risiko.
- Rekomendasi arah koreksi otomatis (nilai invers dari input error).
- Tampilan hasil cepat pada tab **Hasil**.
- Info ringkas penggunaan pada tab **Info**.

---

## Fungsi Sistem
1. **Akuisisi parameter error** dari operator.
2. **Normalisasi sederhana** melalui cast ke `float`.
3. **Kalkulasi risiko** via bobot translasi dan rotasi.
4. **Klasifikasi level tindakan** (`high`, `medium`, `low` risk by threshold).
5. **Generasi output koreksi** untuk axis translasi/rotasi.
6. **Display hasil real-time** pada antarmuka web.

---

## Arsitektur Aplikasi
```text
[User/RTT]
    |
    v
[React UI - index.html]
    |  POST /api/recommend (JSON)
    v
[Python HTTPServer - app.py]
    |
    v
[Rule-based Risk Engine]
    |
    v
[JSON Recommendation Response]
```

---

## Alur Proses Data
1. User mengisi nilai `tx_mm, ty_mm, tz_mm, rx_deg, ry_deg, rz_deg`.
2. Frontend mengirim payload JSON ke endpoint `/api/recommend`.
3. Backend menghitung error absolut total translasi & rotasi.
4. Backend menghitung `risk_score` berbobot.
5. Backend memilih aksi klinis berbasis threshold:
   - `risk_score >= 8` → koreksi wajib + repeat imaging.
   - `4 <= risk_score < 8` → koreksi direkomendasikan + validasi.
   - `< 4` → monitoring tanpa repeat imaging.
6. Frontend menampilkan skor, aksi, dan nilai koreksi.

---

## Spesifikasi API
### `POST /api/recommend`

#### Request (JSON)
```json
{
  "tx_mm": 1.5,
  "ty_mm": -0.8,
  "tz_mm": 2.1,
  "rx_deg": 0.4,
  "ry_deg": -0.2,
  "rz_deg": 0.7
}
```

#### Response (JSON)
```json
{
  "risk_score": 3.61,
  "translation_error_mm": 4.4,
  "rotation_error_deg": 1.3,
  "action": "Lanjutkan dengan monitoring, tanpa repeat imaging",
  "recommendation": {
    "shift_mm": {
      "x": -1.5,
      "y": 0.8,
      "z": -2.1
    },
    "rotation_deg": {
      "pitch": -0.4,
      "roll": 0.2,
      "yaw": -0.7
    }
  },
  "note": "Output AI wajib ditinjau oleh RTT/terapis radiasi dan/atau dokter."
}
```

---

## Logika Perhitungan Risk Score
Formula saat ini:

\[
\text{risk\_score} = 0.7 \times (|Tx|+|Ty|+|Tz|) + 0.3 \times (|Rx|+|Ry|+|Rz|)
\]

### Alasan pendekatan
- Translasi diberi bobot lebih besar (0.7) untuk menegaskan dampak displacement linear.
- Rotasi tetap dipertimbangkan (0.3) untuk menjaga sensitivitas terhadap perubahan angular.

> Catatan: ini adalah baseline rule-based untuk prototipe; kalibrasi klinis lanjutan tetap diperlukan.

---

## Validasi & Batasan
### Kelebihan
- Cepat dipahami, mudah audit, tanpa black-box ML.
- Ringan dijalankan di perangkat umum.

### Batasan saat ini
- Belum memakai data historis pasien/mesin.
- Belum ada confidence interval atau uncertainty estimate.
- Belum ada autentikasi, audit trail, serta penyimpanan rekam keputusan.
- Belum ada mekanisme fail-safe saat input ekstrem/noise.

### Rekomendasi peningkatan
- Tambah validasi input & sanitasi exception.
- Integrasi logging klinis terstruktur.
- Tambah mode simulasi dataset & evaluasi metrik.
- Integrasi model ML/DL berbasis data lokal tervalidasi etik.

---

## Struktur Proyek
```text
Setup-Error-Zero/
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
└── README.md
```

---

## Cara Menjalankan
```bash
python -m venv .venv
source .venv/bin/activate
python app.py
```

Akses aplikasi di browser:
- `http://127.0.0.1:5000`
- `http://localhost:5000`

---

## Contoh Uji Endpoint
```bash
curl -X POST http://127.0.0.1:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"tx_mm":2,"ty_mm":1,"tz_mm":-1,"rx_deg":0.5,"ry_deg":0.2,"rz_deg":0.3}'
```

---

## Roadmap Pengembangan
- [ ] Validasi input & exception handling komprehensif.
- [ ] Logging + audit trail tindakan operator.
- [ ] Export hasil ke format laporan klinis.
- [ ] Modul analytics tren setup error per fraksi.
- [ ] Integrasi model prediktif berbasis dataset institusi.
- [ ] Dashboard QA untuk evaluasi near-miss.

---

## Kontributor & Kontak
- **GitHub:** [github.com/sobri3195](https://github.com/sobri3195)
- **Author:** **Lettu Kes dr. Muhammad Sobri Maulana, S.Kom, CEH, OSCP, OSCE**
- **Email:** [muhammadsobrimaulana31@gmail.com](mailto:muhammadsobrimaulana31@gmail.com)
- **Website:** [muhammadsobrimaulana.netlify.app](https://muhammadsobrimaulana.netlify.app)
- **Sevalla Page:** [muhammad-sobri-maulana-kvr6a.sevalla.page](https://muhammad-sobri-maulana-kvr6a.sevalla.page/)
- **YouTube:** [@muhammadsobrimaulana6013](https://www.youtube.com/@muhammadsobrimaulana6013)
- **Telegram:** [@winlin_exploit](https://t.me/winlin_exploit)
- **TikTok:** [@dr.sobri](https://www.tiktok.com/@dr.sobri)
- **Grup WhatsApp:** [Bergabung di Grup](https://chat.whatsapp.com/B8nwRZOBMo64GjTwdXV8Bl)
- **Toko Online Sobri:** [pegasus-shop.netlify.app](https://pegasus-shop.netlify.app)
- **Gumroad:** [maulanasobri.gumroad.com](https://maulanasobri.gumroad.com/)

---

## Dukungan / Donasi
Jika proyek ini bermanfaat, dukungan Anda sangat berarti:

- [Lynk.id](https://lynk.id/muhsobrimaulana)
- [Trakteer](https://trakteer.id/g9mkave5gauns962u07t)
- [KaryaKarsa](https://karyakarsa.com/muhammadsobrimaulana)
- [Nyawer](https://nyawer.co/MuhammadSobriMaulana)

---

## Disclaimer Klinis
Aplikasi ini adalah **prototype decision support** untuk edukasi, riset, dan pengembangan sistem. Output sistem **tidak menggantikan** keputusan profesional medis. Semua rekomendasi wajib diverifikasi oleh tenaga klinis berwenang sebelum tindakan terapi.
