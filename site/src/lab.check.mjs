// Known-answer check, run by "npm run build" before vite: every JS port must reproduce
// the repo's own committed results, or the build fails.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { loads, same, dumps, pyInt, pyFloat, floatRepr, F } from './py.js';
import { runCase, callFunction, extractAndValidate, parseCorpus, evaluateDeep, evaluateSupplement, attemptHeal, SCHEMAS, wilson, countTests } from './lab.js';

const root = new URL('../../', import.meta.url);
const read = (p) => fs.readFileSync(new URL(p, root), 'utf8');

// Level 1: all 10 recorded cases match their stated expectation (run_cases.py prints 10 of 10).
const cases = loads(read('level-1-learn/cases.json'));
assert.equal(cases.length, 10);
const l1 = cases.map(runCase);
assert.deepEqual(l1.map((r) => r.match), cases.map(() => true), 'level 1 case expectations');
assert.equal(l1.filter((r) => r.ok).length, 4, 'four calls dispatched');
assert.equal(dumps(callFunction('get_weather', '{"city": "Dhaka", "unit": "fahrenheit"}').result), dumps(loads('{"city": "Dhaka", "unit": "fahrenheit", "temperature": 91.4}')));
assert.equal(callFunction('create_calendar_event', '{"title": "x", "date": "2026-11-20", "duration_minutes": 45.0}').errors[0].get('code'), 'type', '45.0 is a float, not an integer');

// Level 2: every document's record, errors and verdict equal results_build.json.
const docs = parseCorpus(read('level-2-build/corpus.py'));
const build = loads(read('level-2-build/results_build.json'));
assert.equal(docs.length, build.get('documents'));
build.get('per_document').forEach((want, i) => {
  const got = extractAndValidate(docs[i]);
  assert.equal(got.id, want.get('id'));
  assert.ok(same(got.record, want.get('record')), `record ${got.id}`);
  assert.ok(same(got.errors, want.get('errors')), `errors ${got.id}`);
  assert.equal(got.accepted ? 'accept' : 'reject', want.get('actual'), `verdict ${got.id}`);
});

// Level 3: final record, status, rounds and the full repair log equal results_deep.json.
const deep = loads(read('level-3-deep/results_deep.json'));
const evalDeep = loads(read('level-3-deep/evaluation_deep.json'));
const run = evaluateDeep(docs, evalDeep);
assert.ok(same(new Map(Object.entries(run.summary)), deep.get('summary')), 'deep summary');
assert.ok(same(new Map(Object.entries(run.perClass).map(([k, v]) => [k, new Map(Object.entries(v))])), deep.get('per_defect_class')), 'per defect class');
deep.get('per_document').forEach((want, i) => {
  const got = run.perDocument[i];
  assert.equal(got.id, want.get('id'));
  for (const [a, b] of [['record', 'final_record'], ['repair_log', 'repair_log'], ['errors', 'final_errors'], ['status', 'status'], ['rounds', 'rounds'], ['flagged', 'flagged'], ['silent_failure', 'silent_failure']])
    assert.ok(same(got[a], want.get(b)), `${b} ${got.id}`);
});
// The bound bites, as tests/test_deep_healing.py pins: coerce then clamp needs two rounds.
const twoStep = new Map([['invoice_id', 'INV-1'], ['vendor', 'V'], ['date', '2026-01-01'], ['total_cad', '250000'], ['items_count', 1]]);
assert.equal(attemptHeal(twoStep, { ...SCHEMAS.invoice, properties: { ...SCHEMAS.invoice.properties, invoice_id: { type: 'string' } } }, 'x', { maxRounds: 1 }).status, 'still_rejected');
// Ablation sanity: with clamp_to_range off nothing is clamped, so silent failures vanish.
const noClamp = evaluateDeep(docs, evalDeep, { rules: { drop_additional_field: true, coerce_numeric_string: true, clamp_to_range: false } }).summary;
assert.equal(noClamp.healed, 1); assert.equal(noClamp.silent_failures, 0);

// Supplementary set: every record, log and the summary equal results_supplement.json.
const supp = loads(read('level-3-deep/results_supplement.json'));
const srun = evaluateSupplement(loads(read('level-3-deep/supplement.json')));
assert.ok(same(new Map(Object.entries(srun.summary)), supp.get('summary')), 'supplement summary');
supp.get('per_record').forEach((want, i) => {
  const got = srun.perRecord[i];
  assert.equal(got.id, want.get('id'));
  for (const [a, b] of [['record', 'final_record'], ['repair_log', 'repair_log'], ['errors', 'final_errors'], ['status', 'status'], ['rounds', 'rounds'], ['silent_failure', 'silent_failure'], ['match', 'match']])
    assert.ok(same(got[a], want.get(b)), `supplement ${b} ${got.id}`);
});

// Wilson intervals equal level-3-deep/uncertainty.json.
const unc = JSON.parse(read('level-3-deep/uncertainty.json'));
for (const k of ['extraction_accuracy', 'validation_catch_rate', 'repair_rate', 'silent_failure_rate', 'supplement_repair_rate', 'supplement_silent_failure_rate']) {
  const { successes, trials, wilson95 } = unc[k];
  wilson(successes, trials).forEach((v, j) => assert.ok(Math.abs(v - wilson95[j]) < 5e-5, `${k} wilson ${v}`));
}

// Test counts: the README states 16 + 18 + 21 = 55 for the three level suites.
const n = (f) => countTests(read(`tests/${f}`));
assert.deepEqual([n('test_learn_structured.py'), n('test_build_pipeline.py'), n('test_deep_healing.py')], [16, 18, 21]);
assert.match(read('README.md'), /Deep unit tests \(55 total\)/);

// Python parsing edge cases, as printed by CPython 3.12.3.
assert.deepEqual(['1_000', '0_1', '+3', '-0', ' 5 '].map(pyInt), [1000, 1, 3, 0, 5]);
assert.deepEqual(['1__0', '_1', '1_', '4.5', '1e3'].map(pyInt), [null, null, null, null, null]);
assert.deepEqual(['1_000.000_1', '1e1_0', '1.e5', '.5', '5.', 'iNf', '-Infinity', '1e400'].map((t) => floatRepr(pyFloat(t).v)), ['1000.0001', '10000000000.0', '100000.0', '0.5', '5.0', 'inf', '-inf', 'inf']);
assert.deepEqual(['.e5', '1_.5', '1._5', 'e5', '1e', '0x10'].map(pyFloat), [null, null, null, null, null, null]);
assert.deepEqual([1e16, 1e15, 1.5e-5, 0.0001, -0, 123456789012345678, 0.1 + 0.2].map(floatRepr), ['1e+16', '1000000000000000.0', '1.5e-05', '0.0001', '-0.0', '1.2345678901234568e+17', '0.30000000000000004']);
const msg = (t) => { try { loads(t); return null; } catch (e) { return e.message; } };
assert.deepEqual(['{city: Toronto}', '', '[1,]', '{"a":1,}', '{"a" 1}', '[1 2]', '"abc', '01', '-', '{"a":1} x', '"a\tb"', '"\\q"', 'tru'].map(msg), [
  'Expecting property name enclosed in double quotes', 'Expecting value', 'Expecting value', 'Expecting property name enclosed in double quotes',
  "Expecting ':' delimiter", "Expecting ',' delimiter", 'Unterminated string starting at', 'Extra data', 'Expecting value', 'Extra data',
  'Invalid control character at', 'Invalid \\escape', 'Expecting value']);
assert.equal(dumps(loads('{"a": [1, 2.0, {"b": NaN}], "c": [], "d": {}}')), '{\n  "a": [\n    1,\n    2.0,\n    {\n      "b": NaN\n    }\n  ],\n  "c": [],\n  "d": {}\n}');
assert.ok(same(F(2), loads('2.0')) && !same(2, loads('2.0')));

console.log('lab ok', { level1: `${l1.filter((r) => r.match).length}/10`, level2: `${docs.length} documents`, level3: run.summary, supplement: srun.summary });
