"""Regression checks v5 TELKOM UNIVERSITY (container, params, sprite, warna)."""
import json
import struct
import unittest
from pathlib import Path

from PIL import Image

from gen_telu import make_digit, F_INTER
from check_round import number_box
from trexpro_wf import (validate_trexpro_container, unpack, ids_to_names,
                        decode_image, encode_image)

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / 'out/telu_trex_pro.bin'


class WatchfaceV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.params, cls.images, _ = unpack(BIN.read_bytes())
        cls.named = ids_to_names(cls.params)

    def test_deliverable_device_container(self):
        checks = validate_trexpro_container(BIN.read_bytes())
        self.assertEqual(checks['device_id'], 83)
        self.assertEqual(checks['decoded_block_bytes'], 4096)

    def test_wrong_device_is_rejected(self):
        data = bytearray(BIN.read_bytes())
        struct.pack_into('<H', data, 16, 59)
        with self.assertRaisesRegex(ValueError, 'wrong device'):
            validate_trexpro_container(data)

    def test_false_quicklz_length_is_rejected(self):
        data = bytearray(BIN.read_bytes())
        struct.pack_into('<I', data, 45, 32768)
        with self.assertRaisesRegex(ValueError, '4096'):
            validate_trexpro_container(data)

    def test_background_and_preview_resolution(self):
        bg = self.named['Background']['ImageIndex']
        preview = self.named['Background']['Preview']['ImageRange']['ImageIndex']
        self.assertEqual(decode_image(self.images[bg - 1])[:2], (360, 360))
        self.assertEqual(decode_image(self.images[preview - 1])[:2], (220, 220))
        self.assertEqual(decode_image(self.images[preview - 1])[2],
                         Image.open(ROOT / 'build/telu/preview.png')
                         .convert('RGBA').tobytes())

    def test_time_digit_sets_are_white_and_red(self):
        hms = self.named['Time']['Digital']['HoursMinutesSeconds']
        for entry, expect_red in ((hms[0], False), (hms[1], True)):
            rng = entry['Text']['Image']['ImageRange']['ImageRange']
            for i in range(10):
                blob = self.images[rng['ImageIndex'] + i - 1]
                w, h, px = decode_image(blob)
                self.assertEqual((w, h), (40, 56))
                reds = sum(1 for p in range(0, len(px), 4)
                           if px[p] > 180 and px[p + 1] < 120)
                if expect_red:
                    self.assertGreater(reds, 40, i)
                else:
                    self.assertLess(reds, 10, i)

    def test_today_month_and_weekday_ranges(self):
        ymd = {e['Type']: e for e in self.named['System']['Date']['YearMonthDay']}
        self.assertEqual(ymd[1]['Text']['Image']['ImageRange']['ImageRange']
                         ['ImagesCount'], 12)
        self.assertEqual(self.named['System']['Date']['Week']['Text']['Image']
                         ['ImageRange']['ImageRange']['ImagesCount'], 7)

    def test_weather_has_29_icon_banner_range(self):
        weather = [e for e in self.named['System']['Data']
                   if e['Type'] == 'Weather']
        linear = [e for e in weather if 'Linear' in e]
        self.assertEqual(len(linear), 1)
        self.assertEqual(linear[0]['Linear']['ImageRange']['ImagesCount'], 29)
        num = [e for e in weather if 'NumberSequence' in e]
        self.assertTrue(num)

    def test_sunrise_is_closest_event_with_icon_pair(self):
        sunrise = [e for e in self.named['System']['Data']
                   if e['Type'] == 'Sunrise']
        self.assertEqual(len(sunrise), 2)
        seq = [e for e in sunrise if 'NumberSequence' in e][0]
        self.assertNotIn('Type', seq['NumberSequence'])
        self.assertIn('DecimalPointImageIndex',
                      seq['NumberSequence']['Text']['Image'])
        pair = [e for e in sunrise if 'Linear' in e][0]
        self.assertEqual(pair['Linear']['ImageRange']['ImagesCount'], 2)

    def test_no_right_alignment_in_delivered_bin(self):
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

        walk(self.named, '')
        self.assertEqual(found, [], 'Alignment Right tidak didukung: %s' % found)

    def test_idle_is_simplified(self):
        idle = self.named['IdleScreen']
        self.assertNotEqual(idle['BackgroundImageIndex'],
                            self.named['Background']['ImageIndex'])
        data = idle['Data']
        self.assertEqual(data['Type'], 'Battery')
        self.assertNotIn('CircleScale', data)
        self.assertIn('NumberSequence', data)

    def test_all_gauges_present(self):
        types = [e['Type'] for e in self.named['System']['Data']]
        for t in ('Battery', 'Steps', 'Calories', 'HeartRate'):
            self.assertIn(t, types)
            entry = [e for e in self.named['System']['Data']
                     if e['Type'] == t][0]
            self.assertIn('CircleScale', entry)

    def test_image_round_trip_keeps_rgb_order(self):
        img = Image.new('RGBA', (2, 1))
        img.putdata([(255, 32, 41, 255), (10, 20, 30, 255)])
        blob = encode_image(img.tobytes(), 2, 1)
        w, h, px = decode_image(blob)
        self.assertEqual((w, h), (2, 1))
        self.assertEqual(px, img.tobytes())

    def test_digits_have_room_on_all_sides(self):
        for cell_w, cell_h, size, stretch in (
                (40, 56, 96, 0.71), (10, 17, 27, 0.55), (9, 12, 19, 0.78)):
            for digit in '0123456789':
                bbox = make_digit(digit, cell_w, cell_h, F_INTER, size,
                                  variation="Black", stretch=stretch).getbbox()
                self.assertIsNotNone(bbox)
                self.assertGreaterEqual(bbox[1], 0, (digit, bbox))
                self.assertLessEqual(bbox[3], cell_h, (digit, bbox))

    def test_metric_values_fit_inside_rings(self):
        folder = ROOT / 'build/telu'
        params = json.loads((folder / 'watchface.json').read_text())
        rings = {'Steps': 47, 'HeartRate': 43, 'Calories': 44, 'Battery': 43}
        for data in params['System']['Data']:
            name = data['Type']
            if name not in rings:
                continue
            txt = data['NumberSequence']['Text']
            rng = txt['Image']['ImageRange']['ImageRange']
            nd = {'Steps': 5, 'HeartRate': 3, 'Calories': 4, 'Battery': 3}[name]
            delim = txt['Image'].get('DelimiterImageIndex')
            suf = None
            if 'SuffixImage' in txt['Image']:
                suf = txt['Image']['SuffixImage']['ImageRange']['ImageIndex']
            x, y, w, h = number_box(folder, txt, nd, suf, delim)
            cx = data['CircleScale']['Angle']['X']
            self.assertLessEqual(abs(x + w / 2 - cx), rings[name], name)
            self.assertLessEqual(w / 2, rings[name], name)


if __name__ == '__main__':
    unittest.main()
