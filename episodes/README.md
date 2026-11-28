# DARK ATLAS — Episode input

Simpan naskah episode sebagai `episodes/current.txt`.

- Satu paragraf = satu adegan. Pecah paragraf panjang agar visual lebih dinamis.
- Tulis hanya narasi yang akan dibacakan. Jangan masukkan catatan kamera atau timecode.
- Gunakan bahasa Indonesia.
- Jangan masukkan API key atau data rahasia ke file ini.

Setelah menyimpan naskah, buka tab **Actions** → **DARK ATLAS - Render Video** → **Run workflow**. Hasil MP4 akan tersedia sebagai artifact untuk diunduh.

Workflow memakai edge-tts (tanpa API key), FFmpeg, dan pencarian video bebas dari Wikimedia Commons/Internet Archive. Jika stok tidak ditemukan, engine memakai visual fallback FFmpeg. Tidak ada API berbayar yang dikonfigurasi.
