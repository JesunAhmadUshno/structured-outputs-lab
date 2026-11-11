"""Portfolio standard checks: the required files exist and no public file carries a grade."""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = ["README.md", "PROPOSAL.md", "REPORT.md", "CHANGELOG.md", "CITATION.cff", "SECURITY.md", "LICENSE",
            "docs/decisions/0001-keep-stage-folders.md", "docs/decisions/0002-repair-rules-never-invent.md",
            "level-1-learn/cases.json", "level-2-build/results_build.json", "level-3-deep/results_deep.json",
            "level-3-deep/results_supplement.json", "level-3-deep/uncertainty.json"]
# Grades are internal (portfolio METHOD section 5). Patterns cover the forms this repo used to publish.
GRADE = re.compile(r"of 10,?000\b|/ ?10,?000\b|/10{3}\b|\bGrade:|\b[Ll]evel grades?\b|[Pp]ublicity grades?\b"
                   r"|\b\d{3,4} of 1,?000\b|hiring value \d of \d|\([A-D][+-]?( to [A-D][+-]?)?\)$", re.M)
# Made-up values in the shapes old grades took. These lines are exempt from the scan below.
FIXTURES = ["Level grade 1234 of 10000.", "graded 1111 of 10000", "| 1 |\nMean: 123 of 1000",  # grade-fixture
            "## 9. Section (C to D)", "Grade: 1,111 of 10,000", "hiring value 1 of 9"]  # grade-fixture
README_ABSTRACT = ["**Question.**", "**Headline.**", "**Field.**", "**Job family.**", "**Verdict.**",
                   "## Reproduce", "## Lifecycle", "## Layout"]


def public_text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "dist"}]
        for name in files:
            if name.endswith((".md", ".cff", ".jsx", ".html", ".py", ".json", ".yml", ".yaml", ".toml")):
                yield os.path.join(base, name)


class Layout(unittest.TestCase):
    def test_required_files_exist(self):
        missing = [p for p in REQUIRED if not os.path.exists(os.path.join(ROOT, p))]
        self.assertEqual(missing, [], "missing: " + ", ".join(missing))

    def test_readme_opens_with_the_abstract(self):
        text = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
        positions = [text.find(m) for m in README_ABSTRACT]
        self.assertNotIn(-1, positions, "README is missing part of the abstract block")
        self.assertEqual(positions, sorted(positions), "README abstract parts are out of order")

    def test_no_public_grade(self):
        hits = []
        for path in public_text_files():
            lines = open(path, encoding="utf-8").read().splitlines()
            text = "\n".join(line for line in lines if not line.endswith("# grade-fixture"))
            for m in GRADE.finditer(text):
                hits.append(f"{os.path.relpath(path, ROOT)}: {m.group(0)}")
        self.assertEqual(hits, [], "grades are internal; found: " + "; ".join(hits))

    def test_grade_pattern_catches_the_old_forms(self):
        for old in FIXTURES:
            self.assertIsNotNone(GRADE.search(old), old)


if __name__ == "__main__":
    unittest.main()
