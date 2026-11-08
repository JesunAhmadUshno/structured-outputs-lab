# PUBLICITY: structured-outputs-lab (P14)

Publicity log under the documentation and publishing standard,
Section 7. Every finished level produces its written fan-out set.
Drafts are prepared by the loop. Actual social posting follows
the standing platform rules and gates. The loop itself never posts
to social.

Fan-out set date: 2026-11-04. Project state: v1.0, Learn, Build, and
compressed Deep done 2026-11-04, 55 tests passing.

## Fan-out files (moved from README.md, 2026-11-08)

Written fan-out for v1.0 is in fanout/ (2026-11-04). The drafts are
dated and name files by their names at the time; README.md maps the
old names to PROPOSAL.md and REPORT.md.

- fanout/blog-post.md: the full story, with the main results claim.
- fanout/tutorial.md: course module P14-structured-outputs-lab;
  every command in it was run and verified.
- fanout/website-page.md: project page copy only, not published.
- fanout/linkedin-post.md: draft, not posted, link in the first
  comment line only.
- fanout/paper-candidate.md: the self-healing parse reliability
  note brief; submission is Jesun's tap, nothing submitted.
- fanout/release-notes.md: draft notes for the existing releases
  v0.1, v0.5, and v1.0 only.

## Channel log (2026-11-04)

| Channel | Outcome on 2026-11-04 |
| --- | --- |
| GitHub releases | Live: v0.1 https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v0.1 , v0.5 https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v0.5 , v1.0 https://github.com/JesunAhmadUshno/structured-outputs-lab/releases/tag/v1.0 (verified with gh release list, 2026-11-04). Draft release notes for all three are in fanout/release-notes.md. No new release was created for the fan-out. |
| Portfolio index | Held: fan-out links are ready, the index update is a coordinator step outside this cycle. Named reason: held for index refresh. |
| Website page | Draft in fanout/website-page.md. Held: not published to jesunahmadushno.com. |
| Blog | Draft in fanout/blog-post.md. Held: not posted. |
| Tutorial | In repo: fanout/tutorial.md. Every command in it was run and verified on 2026-11-04 (three runners, three per-level test discoveries, full suite at 55 tests). |
| LinkedIn post | Draft in fanout/linkedin-post.md, marked DRAFT NOT POSTED, link carried as the first-comment line per the LinkedIn rule. Held: not posted, loop never posts. |
| X | Draft held: no X copy is shipped in this set beyond the LinkedIn draft source text. Held under the standing social rules; posting is outside the loop. |
| Facebook | Draft held: no Facebook copy posted. Standing rule applies (no link in body or comments, keyword call to action fulfilled by DM). Held: not posted, loop never posts. |
| Instagram | Draft held: no Instagram copy posted. Standing rule applies (no clickable link in caption, link in bio). Held: not posted, loop never posts. |
| Threads | Draft held: no Threads copy posted. Threads waits for Jesun's tap per post, hash-locked on exact text and media. Held: awaiting Jesun's tap. |
| Video | Held: engine queue, January production for lab projects per the December Compression Protocol. No video was produced in this cycle. |
| Book chapter | Draft angle in fanout/blog-post.md and SPEC.md ("Answers In Shape"). Held: chapter draft follows the finished project set; not a published chapter. |
| Paper candidate | Draft brief in fanout/paper-candidate.md (self-healing parse loop, repair rate and silent failure rate). Submission is Jesun's tap. Nothing submitted, no venue contacted. Tracker row stands at CANDIDATE for P14. |

## Actions polish pack (2026-11-04)

Applied through a pull request on 2026-11-04, following the GitHub
Actions polish standard for ROADMAP-V3-BATCH. The pack adds: CI on a
Python 3.11 and 3.12 matrix with a ruff lint step (scope in
ruff.toml: E, F, I, line length 120), CodeQL scanning, Dependabot
for pip and GitHub Actions, a release workflow attaching a
structured-outputs-lab source tarball to v* tag releases, Labeler,
Greetings, Stale in comment-only mode (days-before-close: -1, it
never closes), and a docs summary page under docs/ for GitHub
Pages. All existing CI steps are preserved inside the matrix:
smoke, Learn tests and case run, Build tests and run, Deep tests
and healing run. The Greetings workflow uses the snake_case inputs
that actions/first-interaction@v3 requires (issue_message,
pr_message, repo_token).

| Channel | Outcome on 2026-11-04 |
| --- | --- |
| GitHub Actions polish pack | Applied by pull request in this repo; CI, CodeQL, Dependabot, Release, Labeler, Greetings, and Stale workflows added, plus ruff.toml, requirements.txt, and docs/index.md. |
| GitHub Pages | Docs page under docs/ prepared for Pages (source main, /docs). Live status is verified with gh after the merge and recorded in the batch ledger, not claimed here ahead of that check. |
| PyPI publishing | Held: needs a new credential (PyPI token). Jesun's tap only. No credential was created. |
| Social posting | Held: no social post was made for this pack. Standing platform rules and gates apply; Threads waits for Jesun's tap per post. The loop itself never posts to social. |
