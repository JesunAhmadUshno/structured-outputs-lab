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
GRADE = re.compile(r"of 10,?000\b|/ ?10,?000\b|/1000\b|\bGrade:|\b[Ll]evel grades?\b|[Pp]ublicity grades?\b"
                   r"|\b\d{3,4} of 1,?000\b|hiring value \d of \d|\([A-D][+-]?( to [A-D][+-]?)?\)$", re.M)
README_ABSTRACT = ["**Question.**", "**Headline.**", "**Field.**", "**Job family.**", "**Verdict.**",
                   "## Reproduce", "## Lifecycle", "## Layout"]


def public_text_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "dist"}]
        for name in files:
            if name.endswith((".md", ".cff", ".jsx", ".html")):
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
            for m in GRADE.finditer(open(path, encoding="utf-8").read()):
                hits.append(f"{os.path.relpath(path, ROOT)}: {m.group(0)}")
        self.assertEqual(hits, [], "grades are internal; found: " + "; ".join(hits))

    def test_grade_pattern_catches_the_old_forms(self):
        for old in ["Level grade 8700 of 10000.", "graded 9560 of 10000", "| 965 |\nMean: 956 of 1000",
                    "## 6. Reproducibility (A- to A)", "Grade: 3,400 of 10,000", "hiring value 3 of 5"]:
            self.assertIsNotNone(GRADE.search(old), old)


if __name__ == "__main__":
    unittest.main()
