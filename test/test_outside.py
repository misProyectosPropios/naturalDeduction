import unittest
from pathlib import Path


class TestOutsideInterface(unittest.TestCase):
    def setUp(self):
        self.html_text = Path('index.html').read_text(encoding='utf-8')

    def test_html_contains_wasm_loader(self):
        self.assertIn('WebAssembly.instantiate', self.html_text)
        self.assertIn('formula.wasm', self.html_text)
        self.assertIn('wasmInstance.exports.add', self.html_text)

    def test_html_contains_cli_preview_structure(self):
        self.assertIn('renderCliPreview', self.html_text)
        self.assertIn('normalizeFormula', self.html_text)
        self.assertIn('viewArea', self.html_text)

    def test_html_has_input_controls(self):
        self.assertIn('id="formulaInput"', self.html_text)
        self.assertIn('id="addBtn"', self.html_text)
        self.assertIn('id="setGoalBtn"', self.html_text)
        self.assertIn('id="clearBtn"', self.html_text)
        self.assertIn('id="formulaList"', self.html_text)
        self.assertIn('id="viewArea"', self.html_text)

if __name__ == '__main__':
    unittest.main()
