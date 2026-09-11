# Theme Telkom University — TEL-U Watchface

Palet & aturan visual untuk seluruh asset. Angka hex **tanpa alpha**; alpha dicantumkan terpisah.

## Palet

```json
{
  "telu_red":    "#ED1E28",
  "telu_maroon": "#B6252A",
  "gray_dark":   "#55565B",
  "gray_light":  "#959597",
  "white":       "#FFFFFF",
  "black":       "#000000"
}
```

## Aturan

1. Background **harus** hitam murni (AMOLED off-pixel).
2. Maksimal 3 warna non-abu per layar: merah Tel-U, marun, putih.
3. Label menggunakan abu (`#959597`), nilai penting putih, aksen merah.
4. Ornamen marun alpha ≤ 40% agar tidak mengganggu keterbacaan.
5. Semua elemen wajib muat dalam lingkaran diameter 360 (hindari pojok).
6. Branding TEL-U hanya teks sederhana (non-komersial).

## Ornamen Khas TEL-U

1. **Ring ganda**: lingkaran marun tipis (r=170, lw=1, alpha 35%) + lingkaran merah tipis (r=163, alpha 25%) — mengingatkan lingkaran logo TEL-U.
2. **Tick marker merah** di posisi jam 12 / 3 / 6 / 9 pada ring luar.
3. **Teks branding** "TELKOM UNIVERSITY" huruf kapital kecil di bawah, tracking lebar.
4. **Segitiga AM/PM** merah Tel-U (tiruan panah rigger asli, warna diganti).
