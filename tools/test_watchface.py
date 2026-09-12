"""Regression checks for glyph cropping, bounds and delivered image data."""
import json
import unittest
from pathlib import Path
from PIL import Image
from gen_telu import make_digit, FONT_DISPLAY, FONT_BOLD
from check_round import number_box
from render_mockup import draw_arc
from trexpro_wf import validate_trexpro_container, unpack, ids_to_names, decode_image, encode_image
import struct

ROOT = Path(__file__).resolve().parent.parent

class WatchfaceTests(unittest.TestCase):
    def test_deliverable_device_container(self):
        checks = validate_trexpro_container((ROOT/'out/telu_trex_pro.bin').read_bytes())
        self.assertEqual(checks['device_id'],83)
        self.assertEqual(checks['decoded_block_bytes'],4096)

    def test_wrong_device_is_rejected(self):
        data=bytearray((ROOT/'out/telu_trex_pro.bin').read_bytes())
        struct.pack_into('<H',data,16,59)
        with self.assertRaisesRegex(ValueError,'wrong device'):
            validate_trexpro_container(data)

    def test_false_quicklz_length_is_rejected(self):
        data=bytearray((ROOT/'out/telu_trex_pro.bin').read_bytes())
        struct.pack_into('<I',data,45,32768)
        with self.assertRaisesRegex(ValueError,'4096'):
            validate_trexpro_container(data)

    def test_firmware_background_and_preview(self):
        params, images, _ = unpack((ROOT/'out/telu_trex_pro.bin').read_bytes())
        named = ids_to_names(params)
        bg = named['Background']['ImageIndex']
        preview = named['Background']['Preview']['ImageRange']['ImageIndex']
        self.assertGreaterEqual(bg, 1, 'Firmware image ID zero means no image')
        self.assertEqual(decode_image(images[bg - 1])[:2], (360, 360))
        self.assertEqual(decode_image(images[preview - 1])[:2], (220, 220))
        self.assertEqual(decode_image(images[preview - 1])[2],
                         Image.open(ROOT/'build/telu/preview.png').convert('RGBA').tobytes())

    def test_firmware_digit_zero_references_zero_sprite(self):
        params, images, _ = unpack((ROOT/'out/telu_trex_pro.bin').read_bytes())
        named = ids_to_names(params)
        entry = named['Time']['Digital']['HoursMinutesSeconds'][0]
        first = entry['Text']['Image']['ImageRange']['ImageRange']['ImageIndex']
        pixels = decode_image(images[first - 1])[2]
        self.assertEqual(pixels, Image.open(ROOT/'build/telu/3.png').convert('RGBA').tobytes())

    def test_digits_have_room_on_all_sides(self):
        for cell_w, cell_h, font, size in [(54, 100, FONT_DISPLAY, 91), (16, 30, FONT_BOLD, 29), (15, 22, FONT_BOLD, 23)]:
            for digit in '0123456789':
                bbox = make_digit(digit, cell_w, cell_h, font, size).getbbox()
                self.assertIsNotNone(bbox)
                self.assertGreater(bbox[1], 0, (digit, bbox))
                self.assertLess(bbox[3], cell_h, (digit, bbox))

    def test_zero_battery_draws_no_progress(self):
        canvas = Image.new('RGBA', (360, 360))
        draw_arc(canvas, {'X':180,'Y':180,'Radius':172,'StartAngle':155,'EndAngle':205}, 0, (255,0,0,255))
        self.assertIsNone(canvas.getbbox())

    def test_max_metrics_fit_their_columns(self):
        folder = ROOT / 'build/telu'
        params = json.loads((folder / 'watchface.json').read_text())
        for data in params['System']['Data']:
            name = data['Type']
            if name not in ('Calories','Steps','HeartRate'):
                continue
            txt = data['NumberSequence']['Text']
            rng = txt['Image']['ImageRange']['ImageRange']
            n, left, right = {'Calories':(4,55,130),'Steps':(5,140,236),'HeartRate':(3,245,306)}[name]
            x,y,w,h = number_box(folder, txt, rng['ImageIndex'], rng['ImagesCount'], n)
            self.assertGreaterEqual(x,left)
            self.assertLessEqual(x+w,right)

    def test_no_right_alignment_in_delivered_bin(self):
        """Firmware T-Rex Pro mengabaikan Alignment Right (teks mulai di X
        lalu memanjang ke kanan), sehingga jam masuk kapsul dan menit keluar
        layar pada uji jam 2026-09-12."""
        params, _, _ = unpack((ROOT/'out/telu_trex_pro.bin').read_bytes())
        named = ids_to_names(params)
        found = []

        def walk(node, path):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key == 'Alignment' and value == 'Right':
                        found.append(path)
                    walk(value, path + '/' + str(key))
            elif isinstance(node, list):
                for i, value in enumerate(node):
                    walk(value, path + '[%d]' % i)

        walk(named, '')
        self.assertEqual(found, [], 'Alignment Right tidak didukung: %s' % found)

    def test_idle_mirrors_main_layout(self):
        """Preview, tampilan utama, dan always-on identik dan menampilkan
        informasi yang sama."""
        folder = ROOT / 'build/telu'
        params = json.loads((folder / 'watchface.json').read_text())
        idle = params['IdleScreen']
        self.assertEqual(idle['BackgroundImageIndex'], 0)
        self.assertEqual(idle['Time']['Digital'], params['Time']['Digital'])
        self.assertEqual(idle['Date'], params['System']['Date'])
        self.assertEqual(idle['Data'], params['System']['Data'])

    def test_image_round_trip_keeps_rgb_order(self):
        """Encode->decode harus mempertahankan R,G,B persis; pada jam,
        urutan byte gambar yang salah membuat merah tampil biru."""
        img = Image.new('RGBA', (2, 1))
        img.putdata([(237, 30, 40, 255), (10, 20, 30, 255)])
        blob = encode_image(img.tobytes(), 2, 1)
        w, h, px = decode_image(blob)
        self.assertEqual((w, h), (2, 1))
        self.assertEqual(px, img.tobytes())

    def test_reference_pixels_match_delivered_bin(self):
        """Snapshot parser upstream memuat byte piksel seperti tersimpan di bin
        (format 0xFFFF = BGRX, parser menyalin apa adanya). Interpretasi RGBA
        dan kecocokan dgn desain diverifikasi oleh tools/verify_bin.py."""
        folder = ROOT / 'build/reference_current'
        if not folder.exists():
            self.skipTest('Run verify_reference.mjs with upstream source first')
        params, images, _ = unpack((ROOT/'out/telu_trex_pro.bin').read_bytes())
        for i, blob in enumerate(images):
            self.assertEqual(struct.unpack_from('<H', blob, 2)[0], 0xFFFF, i)
            w = struct.unpack_from('<I', blob, 4)[0]
            h = struct.unpack_from('<I', blob, 8)[0]
            self.assertEqual([w, h], json.loads((folder/f'{i}.json').read_text()), i)
            self.assertEqual(blob[24:], (folder/f'{i}.rgba').read_bytes(), i)

if __name__ == '__main__':
    unittest.main()
