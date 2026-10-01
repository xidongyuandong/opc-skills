import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/check-doc-links.py'
spec = importlib.util.spec_from_file_location('doc_links', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class LinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def write(self, name, text='content'):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def scan(self):
        return checker.check_links(self.root, 'xidongyuandong/opc-skills')

    def test_deleted_skill_fails_with_source_line(self):
        self.write('README.md', 'intro\n[old](skills/removed/SKILL.md)')
        errors, count = self.scan()
        self.assertEqual(count, 1)
        self.assertIn('README.md:2', errors[0])
        self.assertIn('skills/removed/SKILL.md', errors[0])

    def test_relative_images_unicode_spaces_and_balanced_parentheses(self):
        self.write('docs/目录 (new).md')
        self.write('image.png')
        self.write('docs/a.md', '[target](<目录 (new).md>)\n![pic](../image.png)\n[encoded](%E7%9B%AE%E5%BD%95%20(new).md#title)')
        self.assertEqual(self.scan(), ([], 3))

    def test_references_html_and_same_repo_urls(self):
        self.write('ok.md')
        self.write('README.md', '''[one][ref]\n[ref]: ok.md "Title"
[ref][]\n[ref]\n<a href="ok.md">ok</a>
[full](https://github.com/xidongyuandong/opc-skills/blob/main/gone.md)
[raw](https://raw.githubusercontent.com/xidongyuandong/opc-skills/main/gone.md)
''')
        errors, count = self.scan()
        self.assertEqual(count, 6)
        self.assertEqual(len(errors), 2)

    def test_examples_comments_external_and_fragments_are_not_local_links(self):
        self.write('README.md', '''```md
[example](missing.md)
```
~~~
[example](missing.md)
~~~
`[inline](missing.md)`
<!-- [comment](missing.md) -->
[external](https://example.com/none)
[title](#title)
[old revision](https://github.com/xidongyuandong/opc-skills/blob/abc123/old.md)
''')
        self.assertEqual(self.scan(), ([], 0))

    def test_directory_escape_and_case_mismatch_fail(self):
        self.write('File.md')
        self.write('README.md', '[outside](../outside.md)\n[case](file.md)')
        errors, _ = self.scan()
        self.assertEqual(len(errors), 2)

    def test_link_deletion_is_detected(self):
        target = self.write('ok.md')
        self.write('README.md', '[ok](ok.md)')
        self.assertFalse(self.scan()[0])
        target.unlink()
        self.assertTrue(self.scan()[0])

    def test_nested_list_links_and_first_reference_definition(self):
        self.write('exists.md')
        self.write('README.md', '- group\n    - [old](missing.md)\n        [more](missing2.md)\n\n[a][ref]\n[ref]: missing3.md\n[ref]: exists.md')
        errors, count = self.scan()
        self.assertEqual(count, 3)
        self.assertEqual(len(errors), 3)

    def test_indented_code_examples_are_ignored(self):
        self.write('README.md', 'Example:\n\n    [not navigation](missing.md)\n')
        self.assertEqual(self.scan(), ([], 0))

    def test_autolink_and_inventory_escape_are_reported(self):
        self.write('plugins/marketplace-zxgc/skills/new/SKILL.md')
        self.write('README.md', '<https://github.com/xidongyuandong/opc-skills/blob/main/absent.md>\n[outside](../outside.md)')
        self.write('README.en.md', '[bad](https://[invalid)')
        self.assertTrue(any('absent.md' in e for e in self.scan()[0]))
        errors = checker.check_inventory(self.root)
        self.assertTrue(any('outside' in e for e in errors))
        self.assertTrue(any('invalid' in e for e in errors))

    def test_inventory_missing_extra_and_duplicates(self):
        self.write('plugins/marketplace-zxgc/skills/new/SKILL.md')
        row = '| [new](plugins/marketplace-zxgc/skills/new/SKILL.md) | useful |\n'
        for name in ('README.md', 'README.en.md'):
            self.write(name, row)
        self.write('docs/skills-catalog.md', '## Packaged Skills\n| `new` | No | useful |\n## Historical\n| `old` | No | historical |')
        self.assertEqual(checker.check_inventory(self.root), [])
        self.write('README.en.md', row + row)
        self.write('docs/skills-catalog.md', '## Packaged Skills\n| `old` | No | absent |')
        errors = checker.check_inventory(self.root)
        self.assertTrue(any('duplicate' in e for e in errors))
        self.assertTrue(any('missing' in e and 'new' in e for e in errors))
        self.assertTrue(any('unpackaged' in e and 'old' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
