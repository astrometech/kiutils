"""Unittests of the KiCad 10 board format additions

KiCad 10 references nets by name only, ``(net "GND")``, in pads, tracks, vias and zones, and
footprints may contain dimensions.
"""

import unittest

from kiutils.board import Board
from kiutils.footprint import Footprint
from kiutils.items.common import Net
from kiutils.utils import sexpr

BOARD_KICAD10 = '''(kicad_pcb (version 20260206) (generator "pcbnew") (generator_version "10.0")
  (general (thickness 1.6))
  (layers (0 "F.Cu" signal) (2 "B.Cu" signal))
  (footprint "R" (layer "F.Cu") (uuid "00000000-0000-0000-0000-000000000010") (at 1 2)
    (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu") (net "GND") (uuid "00000000-0000-0000-0000-000000000011"))
    (pad "2" smd rect (at 1 0) (size 1 1) (layers "F.Cu") (uuid "00000000-0000-0000-0000-000000000012"))
  )
  (segment (start 0 0) (end 1 1) (width 0.25) (layer "F.Cu") (net "GND") (uuid "00000000-0000-0000-0000-000000000013"))
  (via (at 1 1) (size 0.6) (drill 0.3) (layers "F.Cu" "B.Cu") (net "VCC") (uuid "00000000-0000-0000-0000-000000000014"))
)
'''


class Tests_KiCad10(unittest.TestCase):
    """Test cases for the KiCad 10 additions"""

    def test_netByNameOnly(self):
        """A net without a number is parsed with ``number`` set to None and written back unchanged"""
        net = Net().from_sexpr(['net', 'GND'])
        self.assertIsNone(net.number)
        self.assertEqual(net.name, 'GND')
        self.assertEqual(net.to_sexpr(), '(net "GND")')

    def test_netWithNumberIsUnchanged(self):
        net = Net().from_sexpr(['net', 3, 'GND'])
        self.assertEqual((net.number, net.name), (3, 'GND'))
        self.assertEqual(net.to_sexpr(), '(net 3 "GND")')

    def test_boardWithNetNames(self):
        board = Board.from_sexpr(sexpr.parse_sexp(BOARD_KICAD10))
        pads = board.footprints[0].pads
        self.assertEqual(pads[0].net.name, 'GND')
        self.assertIsNone(pads[0].net.number)
        self.assertIsNone(pads[1].net)
        segment, via = board.traceItems
        self.assertEqual(segment.net, 'GND')
        self.assertEqual(via.net, 'VCC')

    def test_boardWithNetNamesRoundTrip(self):
        board = Board.from_sexpr(sexpr.parse_sexp(BOARD_KICAD10))
        text = board.to_sexpr()
        self.assertIn('(net "GND")', text)
        self.assertIn('(net "VCC")', text)
        again = Board.from_sexpr(sexpr.parse_sexp(text))
        self.assertEqual(again.footprints[0].pads[0].net.name, 'GND')
        self.assertEqual([item.net for item in again.traceItems], ['GND', 'VCC'])

    def test_numberedNetsRoundTripAsBefore(self):
        text = '(kicad_pcb (version 20221018) (generator pcbnew) (net 0 "") (net 1 "GND")\n' \
               '(segment (start 0 0) (end 1 1) (width 0.25) (layer "F.Cu") (net 1) (tstamp 00000000-0000-0000-0000-000000000001)))'
        board = Board.from_sexpr(sexpr.parse_sexp(text))
        self.assertEqual(board.traceItems[0].net, 1)
        self.assertIn('(net 1)', board.to_sexpr())

    def test_footprintDimensionIsParsed(self):
        text = '''(footprint "D" (layer "F.Cu") (at 0 0)
          (dimension (type aligned) (layer "F.Fab") (uuid "00000000-0000-0000-0000-000000000020")
            (pts (xy 0 0) (xy 10 0)) (height 1)
            (gr_text "10 mm" (at 5 1 0) (layer "F.Fab") (uuid "00000000-0000-0000-0000-000000000021")
              (effects (font (size 1 1) (thickness 0.15))))
            (format (units 3) (units_format 1) (precision 4))
            (style (thickness 0.1) (arrow_length 1.27) (text_position_mode 0) (extension_height 0.58642) (extension_offset 0) keep_text_aligned)))'''
        footprint = Footprint.from_sexpr(sexpr.parse_sexp(text))
        self.assertEqual(len(footprint.dimensions), 1)
        self.assertEqual(footprint.dimensions[0].type, 'aligned')
        self.assertIn('(dimension', footprint.to_sexpr())


if __name__ == '__main__':
    unittest.main()
