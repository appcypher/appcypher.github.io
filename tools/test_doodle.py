"""Keep directed speech-bubble tails part of the same contour as their body."""
import unittest
import xml.etree.ElementTree as ET

import doodle


class BubbleTests(unittest.TestCase):
    def test_directed_bubbles_have_one_filled_closed_outline(self):
        # Exercise top/bottom/side attachments, not just the failing home scene.
        for target in ((132, 192), (300, 260), (150, 330), (20, 250)):
            for kind in ("round", "rect"):
                for rough in (0, 1, 2.2):
                    with self.subTest(target=target, kind=kind, rough=rough):
                        svg = doodle.bubble(doodle.Pen(77, 3, rough), 60, 232, 210, 50,
                                            kind=kind, to=target)
                        root = ET.fromstring(f"<svg>{svg}</svg>")
                        self.assertEqual(len(root), 1)
                        path = root[0]
                        self.assertEqual(path.tag, "path")
                        self.assertEqual(path.get("fill"), doodle.PAPER)
                        self.assertEqual(path.get("stroke"), "currentColor")
                        self.assertTrue(path.get("d").endswith("Z"))
                        self.assertEqual(path.get("d").count("M"), 1)


if __name__ == "__main__":
    unittest.main()
