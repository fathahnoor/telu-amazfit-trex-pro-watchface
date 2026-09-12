# TEL-U Watchface — Layout Final (360 × 360, UIHH_GT2)

Desain "rigger modern": jam besar kanan (HH/MM susun vertikal), kolom data kiri
(KCAL/STEP/HR), strip status atas (baterai + tanggal + AM/PM), arc baterai
bawah, branding TELKOM UNIVERSITY bawah. Sumber: `tools/gen_telu.py`.

## Peta Indeks Gambar (43 total, preview = 42)

| Indeks | Isi | Ukuran |
|---|---|---|
| 0 | Background (hitam, ring marun, tick, label+ikon kolom kiri, branding) | 360×360 |
| 1 | Badge AM (merah, teks putih) | 46×28 |
| 2 | Badge PM | 46×28 |
| 3–12 | Digit besar 0–9 (putih, Arial Black) | 76×100 |
| 13–22 | Digit kecil 0–9 (putih, nilai KCAL/STEP/HR) | 26×36 |
| 23–32 | Digit medium 0–9 (putih, baterai % + tanggal) | 18×24 |
| 33 | No-data `--` | 24×14 |
| 34 | `%` (suffix baterai) | 18×13 |
| 35–41 | Weekday TUE WED THU FRI SAT SUN MON (merah) | ~45×12 |
| 42 | Preview 220×220 (katalog) | 220×220 |

## Posisi Elemen (origin kiri-atas)

| Elemen | Posisi | Catatan |
|---|---|---|
| Baterai % | (42, 26), Left | digit medium + suffix `%` |
| Tanggal: weekday | (180, 32), Left | 7 gambar TUE..MON |
| Tanggal: hari | (224, 30), Left | digit medium, zero-pad 2 |
| AM / PM | (288, 30) | badge, salah satu tampil ikut format jam |
| Jam HH | (332, 80), Right | digit besar, zero-pad 2 |
| Jam MM | (332, 186), Right | digit besar |
| KCAL | (16, 86), Left | digit kecil |
| STEP | (16, 168), Left | digit kecil, muat 5 digit |
| HR | (16, 250), Left | digit kecil |
| Arc baterai | center (180,180) r=160, 135°→225° | merah `#ED1E28`, lebar 7, ujung flat; 0° = atas searah jarum jam |
| IdleScreen | jam Center (180, 96/202), weekday Center (180, 312), arc baterai | AOD minimal, bg sama |

Label/ikon kolom kiri, separator, divider x=158, dan branding dibakar ke
background (statis). Nilai 5-digit (langkah) sudah diuji muat sebelum divider.
