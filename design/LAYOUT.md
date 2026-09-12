# TEL-U REDLINE

Kanvas 360 x 360, pusat (180,180), radius aman konten dinamis 175 px.

| Elemen | Posisi dan ukuran |
| --- | --- |
| Branding | y=40, simbol T dan TELKOM UNIVERSITY |
| Hari, tanggal, AM/PM | y=83 sampai 105 |
| Jam | x=62, y=114, 108 x 100 (Alignment Left, zero pad) |
| Menit | x=191, y=114, 108 x 100, kapsul merah (zero pad) |
| Kalori | x=59, y=253, hingga 4 digit |
| Langkah | x=146, y=253, hingga 5 digit |
| Denyut | x=250, y=253, hingga 3 digit |
| Baterai | x=159, y=297, Alignment Left, termasuk suffix, hingga 3 digit |
| Arc baterai | pusat 180,180, radius 172, 155 sampai 205 derajat |

Semua teks dinamis memakai Alignment Left dengan X eksplisit; firmware
T-Rex Pro mengabaikan Alignment Right (teks mulai dari X, memanjang ke kanan).
Tampilan utama dan IdleScreen memakai blok parameter yang sama, termasuk
background, sehingga preview, tampilan utama, dan always-on identik.

Indeks aset lokal (ID firmware adalah indeks lokal + 1): 0 latar; 1-2 AM/PM; 3-12 angka waktu; 13-22 metrik;
23-32 tanggal/baterai; 33 no-data; 34 persen; 35-41 weekday MON..SUN;
42 slot transparan; 43 latar idle cadangan (tidak dirujuk); 44 preview tertanam.

Parameter aktual dihasilkan oleh `tools/gen_telu.py` ke `build/telu/watchface.json`.
`design/watchface.json` adalah arsip layout lama dan tidak digunakan saat build.
