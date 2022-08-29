"""Unittests of schematic related classes

Authors:
    (C) Marvin Mager - @mvnmgrx - 2022

License identifier:
    GPL-3.0
"""

import unittest
from os import path

from tests.testfunctions import to_file_and_compare, prepare_test, cleanup_after_test, TEST_BASE
from kiutils.schematic import Schematic

SCHEMATIC_BASE = path.join(TEST_BASE, 'schematic')

class Tests_Schematic(unittest.TestCase):
    """Test cases for Schematics"""

    def setUp(self) -> None:
        prepare_test(self)
        return super().setUp()

    def test_createEmptySchematic(self):
        """Tests that an empty schematic generates S-Expression as expected from KiCad

        Note: This test currently disregards an empty `(symbol_instances)` token as it seems that this
        only exists when empty KiCad schematics are created. This is what should be expected for
        empty schematics:

        <pre><code>
        (kicad_sch (version 20211123) (generator kicad-python-tools)
            (paper "A4")
            (lib_symbols)
            (symbol_instances)
        )
        </code</pre>"""
        schematic = Schematic()
        self.testData.pathToTestFile = path.join(SCHEMATIC_BASE, 'test_createEmptySchematic')
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_schematicWithAllPrimitives(self):
        """Tests the parsing of a schematic with all primitives (lines, traces, busses, connections,
        images, etc)"""
        self.testData.pathToTestFile = path.join(SCHEMATIC_BASE, 'test_schematicWithAllPrimitives')
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def test_hierarchicalSchematicWithAllPrimitives(self):
        """Tests the parsing of a hierarchical schematic with all primitives (lines, traces, busses,
        connections, images, etc)"""
        self.testData.pathToTestFile = path.join(SCHEMATIC_BASE, 'test_hierarchicalSchematicWithAllPrimitives')
        schematic = Schematic().from_file(self.testData.pathToTestFile)
        self.assertTrue(to_file_and_compare(schematic, self.testData))

    def tearDown(self) -> None:
        cleanup_after_test(self.testData)
        return super().tearDown()
