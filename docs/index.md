# structured-outputs-lab

Reliable LLM applications: strict schemas, validated extraction, and a self-healing parse loop. Built in three levels with measured results at each level, 55 tests passing, v1.0.

- Learn: a strict schema validator and function-calling dispatcher. Level grade 8700 of 10000.
- Build: a document extraction pipeline with schema validation on every output. Level grade 8200 of 10000.
- Deep (compressed): a self-healing parse loop over the 8 Build rejections. Attempted 8, healed 3, repair rate 0.375, silent failure rate 0.667. Level grade 7800 of 10000.

The fan-out set for v1.0 is graded 9560 of 10000 in PUBLICITY.md. Every number above is already published in README.md and PUBLICITY.md and is reproduced by the runners in this repo, checked in CI. The full write-ups are in the level folders: level-1-learn, level-2-build, level-3-deep. Tutorials and the blog post are in fanout/.

Releases: https://github.com/JesunAhmadUshno/structured-outputs-lab/releases
