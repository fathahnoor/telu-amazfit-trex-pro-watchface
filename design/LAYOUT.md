# TEL-U Watchface — Layout Final v2 "MIDNIGHT BLAZE" (360 × 360, UIHH_GT2)

Arah desain: tipografi memimpin (Anton condensed italic + Rajdhani),
hitam dominan + merah Tel-U tajam, monogram T angular raksasa sebagai
potongan identitas, slash diagonal, chip data, glow terkendali.
Font OFL di `assets/fonts/` (Anton, Rajdhani). Sumber: `tools/gen_telu.py`.

ROUND-SAFE: semua konten lolos validator `tools/check_round.py` (r=175).

## Peta Indeks Gambar (43 total, preview = 42)

| Indeks | Isi | Ukuran |
|---|---|---|
| 0 | Background (karbon, blaze, monogram T, ring, chip, branding) | 360×360 |
| 1 | Badge AM angular | 40×24 |
| 2 | Badge PM angular | 40×24 |
| 3–12 | Digit besar Anton italic + bayangan 0–9 | 64×100 |
| 13–22 | Digit Rajdhani Bold 0–9 (nilai) | 26×34 |
| 23–32 | Digit Rajdhani 0–9 (baterai %, tanggal) | 19×25 |
| 33 | No-data `--` | dinamis |
| 34 | `%` (suffix baterai) | dinamis |
| 35–41 | Weekday TUE WED THU FRI SAT SUN MON (putih) | dinamis |
| 42 | Preview 220×220 (katalog) | 220×220 |

## Posisi Elemen (origin kiri-atas)

| Elemen | Posisi | Catatan |
|---|---|---|
| Tanggal: weekday + hari | (162, 38) + (218, 36), Left | atas tengah |
| AM / PM | (80, 44) | badge angular kiri atas |
| Jam HH / MM | (314, 74) / (314, 180), Right | Anton italic besar |
| KCAL / STEP / HR | (58, 118/184/246), Left, dalam chip | digit Rajdhani |
| Baterai % | (283, 286), Right + suffix `%` | kanan bawah |
| Arc baterai | center (180,180) r=172, 155°→205° | merah, lebar 8, flat; 0° = atas CW |
| IdleScreen | jam Center (180, 92/198), weekday Center (180, 308), arc | AOD minimal |

Chip (40, y, 172, y+62) + bar merah, label di dalam, ikon putih —
semuanya dibakar ke background. Nilai 5-digit dan baterai 100% sudah
diuji muat + lolos validator lingkaran.
