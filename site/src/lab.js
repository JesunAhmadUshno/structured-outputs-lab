// JS ports of the repo's Python code, kept line-for-line close so they can be checked:
//   validate()                      level-1-learn/schema_validate.py
//   REGISTRY, callFunction()        level-1-learn/function_calling.py
//   SCHEMAS, extractAndValidate()   level-2-build/pipeline.py
//   attemptHeal(), evaluateDeep()   level-3-deep/heal.py, level-3-deep/run_deep.py
//   wilson()                        level-3-deep/uncertainty.py
// src/lab.check.mjs runs every port against the committed results during "npm run build".
import { F, PyFloat, WS, strip, pyInt, pyFloat, pyRepr, pyEq, deepCopy, loads, JSONDecodeError } from './py.js';

// ---------------------------------------------------------------- Level 1: validator
const err = (path, code, message) => new Map([['path', path], ['code', code], ['message', message]]);

export function typeName(v) {
  if (typeof v === 'boolean') return 'boolean';
  if (typeof v === 'string') return 'string';
  if (typeof v === 'number') return 'integer';
  if (v instanceof PyFloat) return 'number';
  if (v instanceof Map) return 'object';
  if (Array.isArray(v)) return 'array';
  if (v === null) return 'null';
  return typeof v;
}
const typeMatches = (v, expected) => (expected === 'number' ? ['number', 'integer'].includes(typeName(v)) : typeName(v) === expected);
const s = pyRepr; // str() of an int or float equals its repr

// Python's "$" (no MULTILINE) also matches just before a trailing newline.
const patternCache = new Map();
const pyPattern = (p) => {
  if (!patternCache.has(p)) patternCache.set(p, new RegExp(p.replace(/\$$/, '(?=\\n?$)'), 'u'));
  return patternCache.get(p);
};

export function validate(value, schema, path = '$') {
  const errors = [];
  if ('enum' in schema && !schema.enum.some((e) => pyEq(value, e))) {
    errors.push(err(path, 'enum', `${path}: ${pyRepr(value)} is not one of ${pyRepr(schema.enum)}`));
    return errors;
  }
  const expected = schema.type;
  if (expected !== undefined && !typeMatches(value, expected)) {
    errors.push(err(path, 'type', `${path}: expected ${expected}, got ${typeName(value)}`));
    return errors;
  }
  if (typeof value === 'string') errors.push(...validateString(value, schema, path));
  else if (typeof value === 'number' || value instanceof PyFloat) errors.push(...validateNumber(value, schema, path));
  else if (value instanceof Map) errors.push(...validateObject(value, schema, path));
  else if (Array.isArray(value)) errors.push(...validateArray(value, schema, path));
  return errors;
}

function validateString(value, schema, path) {
  const errors = [], len = [...value].length; // code points, like len() on a Python str
  if ('minLength' in schema && len < schema.minLength) errors.push(err(path, 'min_length', `${path}: length ${len} is below minLength ${schema.minLength}`));
  if ('maxLength' in schema && len > schema.maxLength) errors.push(err(path, 'max_length', `${path}: length ${len} is above maxLength ${schema.maxLength}`));
  if ('pattern' in schema && !pyPattern(schema.pattern).test(value)) errors.push(err(path, 'pattern', `${path}: ${pyRepr(value)} does not match pattern ${pyRepr(schema.pattern)}`));
  return errors;
}

function validateNumber(value, schema, path) {
  const errors = [], v = +value;
  if ('minimum' in schema && v < schema.minimum) errors.push(err(path, 'minimum', `${path}: ${s(value)} is below minimum ${s(schema.minimum)}`));
  if ('maximum' in schema && v > schema.maximum) errors.push(err(path, 'maximum', `${path}: ${s(value)} is above maximum ${s(schema.maximum)}`));
  if ('exclusiveMinimum' in schema && v <= schema.exclusiveMinimum) errors.push(err(path, 'exclusive_minimum', `${path}: ${s(value)} is not above exclusiveMinimum ${s(schema.exclusiveMinimum)}`));
  if ('exclusiveMaximum' in schema && v >= schema.exclusiveMaximum) errors.push(err(path, 'exclusive_maximum', `${path}: ${s(value)} is not below exclusiveMaximum ${s(schema.exclusiveMaximum)}`));
  return errors;
}

function validateObject(value, schema, path) {
  const errors = [], props = schema.properties || {};
  for (const f of schema.required || []) if (!value.has(f)) errors.push(err(`${path}.${f}`, 'required', `${path}.${f}: required field is missing`));
  if (schema.additionalProperties === false)
    for (const f of value.keys()) if (!Object.hasOwn(props, f)) errors.push(err(`${path}.${f}`, 'additional', `${path}.${f}: additional field is not allowed in strict mode`));
  for (const [f, sub] of Object.entries(props)) if (value.has(f)) errors.push(...validate(value.get(f), sub, `${path}.${f}`));
  return errors;
}

function validateArray(value, schema, path) {
  const errors = [];
  if ('minItems' in schema && value.length < schema.minItems) errors.push(err(path, 'min_items', `${path}: ${value.length} items is below minItems ${schema.minItems}`));
  if ('maxItems' in schema && value.length > schema.maxItems) errors.push(err(path, 'max_items', `${path}: ${value.length} items is above maxItems ${schema.maxItems}`));
  if (schema.items) value.forEach((item, i) => errors.push(...validate(item, schema.items, `${path}[${i}]`)));
  return errors;
}

// ---------------------------------------------------------------- Level 1: dispatcher
const DATE = '^[0-9]{4}-[0-9]{2}-[0-9]{2}$';
export const FUNCTIONS = {
  get_weather: {
    schema: { type: 'object', properties: { city: { type: 'string', minLength: 1, maxLength: 60 }, unit: { type: 'string', enum: ['celsius', 'fahrenheit'] } }, required: ['city'], additionalProperties: false },
    run: (a) => {
      const city = a.get('city'), unit = a.has('unit') ? a.get('unit') : 'celsius';
      const c = { toronto: 21, dhaka: 33, london: 17 }[city.toLowerCase()] ?? 20;
      const t = unit === 'fahrenheit' ? F(Math.round((c * 9 / 5 + 32) * 10) / 10) : c;
      return new Map([['city', city], ['unit', unit], ['temperature', t]]);
    },
  },
  create_calendar_event: {
    schema: { type: 'object', properties: { title: { type: 'string', minLength: 1, maxLength: 120 }, date: { type: 'string', pattern: DATE }, duration_minutes: { type: 'integer', minimum: 15, maximum: 480 } }, required: ['title', 'date'], additionalProperties: false },
    run: (a) => new Map([['title', a.get('title')], ['date', a.get('date')], ['duration_minutes', a.has('duration_minutes') ? a.get('duration_minutes') : 60], ['status', 'created']]),
  },
  score_keywords: {
    schema: { type: 'object', properties: { text: { type: 'string', minLength: 1 }, keywords: { type: 'array', items: { type: 'string', minLength: 1 }, minItems: 1, maxItems: 10 } }, required: ['text', 'keywords'], additionalProperties: false },
    run: (a) => {
      const lowered = a.get('text').toLowerCase(), kws = a.get('keywords');
      const found = kws.filter((k) => lowered.includes(k.toLowerCase()));
      return new Map([['found', found], ['count', found.length], ['total', kws.length]]);
    },
  },
};

// FunctionRegistry.call: unknown name, then JSON parse, then validate; only valid arguments dispatch.
export function callFunction(name, args) {
  const fn = Object.hasOwn(FUNCTIONS, name) ? FUNCTIONS[name] : null;
  if (!fn) return { ok: false, errors: [err('$', 'unknown_function', `$: unknown function ${pyRepr(name)}`)] };
  if (typeof args === 'string') {
    try { args = loads(args); } catch (e) {
      if (!(e instanceof JSONDecodeError)) throw e;
      return { ok: false, errors: [err('$', 'invalid_json', `$: arguments are not valid JSON (${e.message})`)] };
    }
  }
  const errors = validate(args, fn.schema);
  if (errors.length) return { ok: false, errors };
  return { ok: true, result: fn.run(args) };
}

// run_cases.py: a case matches when accept/reject is as expected and, for rejects, the first error path too.
export function runCase(c) {
  const out = callFunction(c.get('function'), c.get('arguments'));
  const firstPath = !out.ok && out.errors.length ? out.errors[0].get('path') : null;
  let match = out.ok === c.get('expect_ok');
  if (match && !c.get('expect_ok') && c.has('expect_first_path')) match = firstPath === c.get('expect_first_path');
  return { ...out, firstPath, match };
}

// ---------------------------------------------------------------- Level 2: extraction pipeline
export const SCHEMAS = {
  invoice: { type: 'object', properties: { invoice_id: { type: 'string', pattern: '^INV-[0-9]{4}$' }, vendor: { type: 'string', minLength: 1, maxLength: 80 }, date: { type: 'string', pattern: DATE }, total_cad: { type: 'number', minimum: F(0.01), maximum: 100000 }, items_count: { type: 'integer', minimum: 1, maximum: 100 } }, required: ['invoice_id', 'vendor', 'date', 'total_cad', 'items_count'], additionalProperties: false },
  meeting_note: { type: 'object', properties: { meeting_id: { type: 'string', pattern: '^MTG-[0-9]{4}$' }, title: { type: 'string', minLength: 1, maxLength: 120 }, date: { type: 'string', pattern: DATE }, attendees: { type: 'array', items: { type: 'string', minLength: 1 }, minItems: 1, maxItems: 20 }, duration_minutes: { type: 'integer', minimum: 15, maximum: 480 } }, required: ['meeting_id', 'title', 'date', 'attendees', 'duration_minutes'], additionalProperties: false },
  product_listing: { type: 'object', properties: { sku: { type: 'string', pattern: '^SKU-[0-9]{4}$' }, name: { type: 'string', minLength: 1, maxLength: 80 }, price_cad: { type: 'number', minimum: F(0.01), maximum: 50000 }, stock: { type: 'integer', minimum: 0, maximum: 10000 }, category: { type: 'string', enum: ['tools', 'kitchen', 'office', 'outdoor'] } }, required: ['sku', 'name', 'price_cad', 'stock', 'category'], additionalProperties: false },
};

const asNumber = (t) => pyFloat(t) ?? t; // a token that does not parse stays a string, on purpose
const asInteger = (t) => pyInt(t) ?? t;
// re.MULTILINE "^", "$", ".", "\s", "\S" spelled out with Python's line and whitespace rules.
const BOL = '(?:^|(?<=\\n))', EOL = '(?=\\n|$)';
const line = (text, label) => {
  const m = new RegExp(`${BOL}${label}:[${WS}]*([^\\n]+)${EOL}`).exec(text);
  return m ? strip(m[1]) : null;
};
const head = (text, word) => new RegExp(`${BOL}${word}[${WS}]+([^${WS}]+)${EOL}`).exec(text)?.[1];

function extract(text, idWord, idField, fields) {
  const record = new Map();
  const id = head(text, idWord);
  if (id !== undefined) record.set(idField, id);
  for (const [label, field, conv] of fields) {
    const v = line(text, label);
    if (v !== null) record.set(field, conv ? conv(v) : v);
  }
  return record;
}
const attendees = (v) => v.split(',').map(strip);
export const EXTRACTORS = {
  invoice: (t) => extract(t, 'Invoice', 'invoice_id', [['Vendor', 'vendor'], ['Date', 'date'], ['Total', 'total_cad', asNumber], ['Items', 'items_count', asInteger], ['Discount', 'discount', asNumber]]),
  meeting_note: (t) => extract(t, 'Meeting', 'meeting_id', [['Title', 'title'], ['Date', 'date'], ['Attendees', 'attendees', attendees], ['Duration', 'duration_minutes', asInteger]]),
  product_listing: (t) => extract(t, 'Product', 'sku', [['Name', 'name'], ['Price', 'price_cad', asNumber], ['Stock', 'stock', asInteger], ['Category', 'category'], ['Warranty', 'warranty_years', asInteger]]),
};

export function extractAndValidate(doc) {
  const ex = EXTRACTORS[doc.doc_type];
  if (!ex) return { id: doc.id, doc_type: doc.doc_type, record: null, errors: [err('$', 'unknown_type', `$: unknown document type ${pyRepr(doc.doc_type)}`)], accepted: false };
  const record = ex(doc.text);
  const errors = validate(record, SCHEMAS[doc.doc_type]);
  return { id: doc.id, doc_type: doc.doc_type, record, errors, accepted: !errors.length };
}

// Reads the DOCUMENTS list straight out of level-2-build/corpus.py, so there is no copy to drift.
export function parseCorpus(src) {
  const docs = [];
  const re = /"id":\s*"([^"]+)",\s*"doc_type":\s*"([^"]+)",\s*"text":\s*\(([\s\S]*?)\),/g;
  for (const m of src.matchAll(re)) {
    const text = [...m[3].matchAll(/"((?:[^"\\]|\\.)*)"/g)].map((p) => JSON.parse(`"${p[1]}"`)).join('');
    docs.push({ id: m[1], doc_type: m[2], text });
  }
  return docs;
}

// ---------------------------------------------------------------- Level 3: self-healing loop
export const MAX_ROUNDS = 3;
export const RULES = ['drop_additional_field', 'coerce_numeric_string', 'clamp_to_range'];
const ALL_ON = { drop_additional_field: true, coerce_numeric_string: true, clamp_to_range: true };

const fieldFromPath = (p) => (p.startsWith('$.') ? p.slice(2).split('.')[0].split('[')[0] : null);
const subschema = (schema, f) => (f === null ? schema : (schema.properties || {})[f] || {});
const logEntry = (docId, round, e, rule, before, after, valueChanging, outcome) => new Map([
  ['doc_id', docId], ['round', round], ['path', e.get('path')], ['code', e.get('code')], ['rule', rule],
  ['before', before], ['after', after], ['value_changing', valueChanging], ['outcome', outcome]]);

function tryParseNumeric(text, target) {
  if (typeof text !== 'string' || !strip(text)) return [false, null];
  const v = target === 'integer' ? pyInt(text) : target === 'number' ? pyFloat(text) : null;
  return v === null ? [false, null] : [true, v];
}

function clampValue(value, sub, code) {
  if (code === 'maximum') return sub.maximum;
  if (code === 'minimum') return sub.minimum;
  if (code === 'exclusive_maximum') return sub.type === 'integer' ? sub.exclusiveMaximum - 1 : F(+sub.exclusiveMaximum - 0.01);
  if (code === 'exclusive_minimum') return sub.type === 'integer' ? sub.exclusiveMinimum + 1 : F(+sub.exclusiveMinimum + 0.01);
  return value;
}

// One repair attempt for one error. A rule switched off falls through to unrepairable,
// which is exactly what heal.py does for an error no rule names.
function attemptError(record, schema, docId, round, e, rules) {
  const code = e.get('code'), field = fieldFromPath(e.get('path')), sub = subschema(schema, field);
  const has = field !== null && record.has(field);
  const before = has ? deepCopy(record.get(field)) : null;
  const none = () => logEntry(docId, round, e, 'none_unrepairable', before, before, false, 'unrepairable');
  if (code === 'additional' && has && rules.drop_additional_field) {
    const dropped = record.get(field);
    record.delete(field);
    return logEntry(docId, round, e, 'drop_additional_field', dropped, null, false, 'applied');
  }
  if (code === 'type' && has) {
    if (rules.coerce_numeric_string && ['number', 'integer'].includes(sub.type)) {
      const [ok, parsed] = tryParseNumeric(record.get(field), sub.type);
      if (ok) { record.set(field, parsed); return logEntry(docId, round, e, 'coerce_numeric_string', before, parsed, false, 'applied'); }
    }
    return none();
  }
  if (['minimum', 'maximum', 'exclusive_minimum', 'exclusive_maximum'].includes(code) && has && rules.clamp_to_range) {
    const clamped = clampValue(record.get(field), sub, code);
    record.set(field, clamped);
    return logEntry(docId, round, e, 'clamp_to_range', before, clamped, true, 'applied_value_changing');
  }
  return none();
}

export function attemptHeal(record, schema, docId = 'unknown', { maxRounds = MAX_ROUNDS, rules = ALL_ON } = {}) {
  const working = deepCopy(record);
  let errors = validate(working, schema);
  if (!errors.length) return { id: docId, record: working, healed: false, flagged: false, status: 'already_valid', rounds: 0, repair_log: [], errors: [] };
  const log = [];
  let flagged = false, rounds = 0;
  for (let round = 1; round <= maxRounds; round++) {
    rounds = round;
    errors = validate(working, schema);
    if (!errors.length) break;
    let applied = false;
    for (const e of errors) {
      const entry = attemptError(working, schema, docId, round, e, rules);
      log.push(entry);
      if (entry.get('outcome').startsWith('applied')) applied = true;
      if (entry.get('value_changing')) flagged = true;
    }
    if (!applied) break;
  }
  const finalErrors = validate(working, schema);
  const healed = !finalErrors.length;
  return { id: docId, record: working, healed, flagged, status: healed ? (flagged ? 'healed_flagged' : 'healed_clean') : 'still_rejected', rounds, repair_log: log, errors: finalErrors };
}

export const DEFECT_CLASSES = ['missing', 'wrong_type', 'extra_field', 'out_of_range', 'bad_enum'];
const round3 = (x) => Math.round(x * 1000) / 1000;

// run_deep.evaluate(): the Build rejections through the loop, scored against evaluation_deep.json.
export function evaluateDeep(docs, evaluation, opts) {
  const outcomes = docs.map(extractAndValidate);
  const accepted = outcomes.filter((o) => o.accepted), rejected = outcomes.filter((o) => !o.accepted);
  const byId = new Map(evaluation.map((e) => [e.get('id'), e]));
  let validAltered = 0;
  for (const o of accepted) {
    const h = attemptHeal(o.record, SCHEMAS[o.doc_type], o.id, opts);
    if (h.status !== 'already_valid' || !pyEq(h.record, o.record)) validAltered++;
  }
  const perClass = Object.fromEntries(DEFECT_CLASSES.map((c) => [c, { attempted: 0, healed: 0, healed_flagged: 0, silent_failures: 0 }]));
  const perDocument = [];
  let healedTotal = 0, clean = 0, flaggedN = 0, silentN = 0, matched = 0;
  for (const o of rejected) {
    const exp = byId.get(o.id), cls = exp.get('defect_class'), truthful = exp.get('truthful_healed_record');
    const r = attemptHeal(o.record, SCHEMAS[o.doc_type], o.id, opts);
    let silent = false;
    if (r.healed) {
      healedTotal++; r.flagged ? flaggedN++ : clean++;
      silent = !(truthful !== null && pyEq(r.record, truthful));
      if (silent) silentN++;
    }
    const pc = perClass[cls];
    pc.attempted++;
    if (r.healed) { pc.healed++; if (r.flagged) pc.healed_flagged++; if (silent) pc.silent_failures++; }
    let ok = r.healed === exp.get('expect_healed');
    if (r.healed && r.flagged !== exp.get('expect_flagged')) ok = false;
    if (r.healed && truthful !== null && !pyEq(r.record, truthful)) ok = false;
    if (r.healed && pyEq(r.record, o.record)) ok = false;
    if (ok) matched++;
    perDocument.push({ ...r, doc_type: o.doc_type, defect_class: cls, original_record: o.record, truthful, true_record: exp.get('true_record'), silent_failure: r.healed ? silent : null, match: ok });
  }
  const attempted = rejected.length;
  return {
    summary: {
      attempted, healed: healedTotal, healed_clean: clean, healed_flagged: flaggedN, still_rejected: attempted - healedTotal,
      repair_rate: round3(attempted ? healedTotal / attempted : 0), silent_failures: silentN,
      silent_failure_rate: round3(healedTotal ? silentN / healedTotal : 0), valid_records_altered: validAltered, matched,
    },
    accepted: accepted.length, perClass, perDocument,
  };
}

// run_supplement.evaluate(): labelled candidate records fed straight to the loop.
export function evaluateSupplement(labelled) {
  let healed = 0, clean = 0, flaggedN = 0, silent = 0, matched = 0, coerce = 0, applied = 0;
  const perRecord = labelled.map((e) => {
    const r = attemptHeal(e.get('record'), SCHEMAS[e.get('doc_type')], e.get('id'));
    const truthful = e.get('truthful_healed_record');
    let isSilent = null;
    if (r.healed) {
      healed++; r.flagged ? flaggedN++ : clean++;
      isSilent = !(truthful !== null && pyEq(r.record, truthful));
      if (isSilent) silent++;
    }
    coerce += r.repair_log.filter((l) => l.get('rule') === 'coerce_numeric_string' && l.get('outcome') === 'applied').length;
    applied += r.repair_log.filter((l) => l.get('outcome').startsWith('applied')).length;
    let ok = r.status === e.get('expect_status') && r.rounds === e.get('expect_rounds');
    if (truthful !== null && !pyEq(r.record, truthful)) ok = false;
    if (ok) matched++;
    return { ...r, defects: e.get('defects'), expected_status: e.get('expect_status'), silent_failure: isSilent, match: ok };
  });
  const attempted = labelled.length;
  return {
    summary: { attempted, healed, healed_clean: clean, healed_flagged: flaggedN, still_rejected: attempted - healed, repair_rate: round3(healed / attempted),
      silent_failures: silent, silent_failure_rate: round3(healed ? silent / healed : 0), coerce_repairs_applied: coerce, repairs_applied: applied, matched },
    perRecord,
  };
}

// ---------------------------------------------------------------- statistics and counts
const Z95 = 1.959963984540054;
export function wilson(k, n, z = Z95) {
  if (n <= 0) return [0, 1];
  const p = k / n, z2 = z * z, d = 1 + z2 / n;
  const c = (p + z2 / (2 * n)) / d, h = (z * Math.sqrt((p * (1 - p)) / n + z2 / (4 * n * n))) / d;
  return [Math.max(0, c - h), Math.min(1, c + h)];
}
export const countTests = (src) => (src.match(/^\s*def test_/gm) || []).length;
