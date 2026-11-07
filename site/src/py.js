// A small model of Python values so the JS ports agree with the Python code exactly.
// dict -> Map (keeps insertion order, any string key), list -> Array, None -> null,
// int -> plain number, float -> PyFloat. Python tells 60 from 60.0 and the validator
// rejects 60.0 for "integer"; plain JS numbers cannot, so floats are boxed.
// ponytail: ints beyond 2**53 lose precision (Python ints are unbounded); BigInt if that ever matters.

export class PyFloat {
  constructor(v) { this.v = v; }
  valueOf() { return this.v; }
}
export const F = (v) => new PyFloat(v);
export const isFloat = (x) => x instanceof PyFloat;
export const num = (x) => (x instanceof PyFloat ? x.v : typeof x === 'boolean' ? +x : x);

// Python str.isspace() characters, used for \s, \S and strip().
export const WS = '\\t\\n\\v\\f\\r\\x1c-\\x1f \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000';
const stripRe = new RegExp(`^[${WS}]+|[${WS}]+$`, 'g');
export const strip = (s) => s.replace(stripRe, '');

// int(text): optional sign, ASCII digits with single underscores between them.
// ponytail: Python also accepts non-ASCII Unicode digits; ASCII only here.
export function pyInt(text) {
  const s = strip(String(text));
  if (!/^[+-]?\d+(?:_\d+)*$/.test(s)) return null;
  return Number(s.replace(/_/g, '')) + 0; // + 0 turns -0 into 0, as int('-0') is 0
}
// float(text): Python's float() grammar, including inf / infinity / nan in any case.
export function pyFloat(text) {
  const s = strip(String(text));
  const d = '\\d+(?:_\\d+)*';
  if (new RegExp(`^[+-]?(?:${d}(?:\\.(?:${d})?)?|\\.${d})(?:[eE][+-]?${d})?$`).test(s)) return F(Number(s.replace(/_/g, '')));
  const m = /^([+-]?)(inf|infinity|nan)$/i.exec(s);
  if (m) return F(m[2].toLowerCase() === 'nan' ? NaN : m[1] === '-' ? -Infinity : Infinity);
  return null;
}

export function floatRepr(v) {
  if (Number.isNaN(v)) return 'nan';
  if (!Number.isFinite(v)) return v < 0 ? '-inf' : 'inf';
  if (v === 0) return Object.is(v, -0) ? '-0.0' : '0.0';
  const sign = v < 0 ? '-' : '';
  const [mant, e] = Math.abs(v).toExponential().split('e'); // shortest round-trip digits
  const digits = mant.replace('.', ''), exp = +e;
  if (exp >= -4 && exp < 16) {
    if (exp >= digits.length - 1) return sign + digits + '0'.repeat(exp - digits.length + 1) + '.0';
    if (exp >= 0) return sign + digits.slice(0, exp + 1) + '.' + digits.slice(exp + 1);
    return sign + '0.' + '0'.repeat(-exp - 1) + digits;
  }
  return sign + digits[0] + (digits.length > 1 ? '.' + digits.slice(1) : '') + 'e' + (exp < 0 ? '-' : '+') + String(Math.abs(exp)).padStart(2, '0');
}

function strRepr(s) {
  const q = s.includes("'") && !s.includes('"') ? '"' : "'";
  let out = '';
  for (const ch of s) {
    const c = ch.codePointAt(0);
    if (ch === '\\') out += '\\\\';
    else if (ch === q) out += '\\' + q;
    else if (ch === '\n') out += '\\n';
    else if (ch === '\r') out += '\\r';
    else if (ch === '\t') out += '\\t';
    else if (c < 0x20 || c === 0x7f) out += '\\x' + c.toString(16).padStart(2, '0');
    else out += ch; // ponytail: other non-printable Unicode is escaped by Python, shown raw here
  }
  return q + out + q;
}

// repr(value), as used by the f-strings in the Python error messages.
export function pyRepr(x) {
  if (x === null || x === undefined) return 'None';
  if (x === true) return 'True';
  if (x === false) return 'False';
  if (x instanceof PyFloat) return floatRepr(x.v);
  if (typeof x === 'number') return String(x);
  if (typeof x === 'string') return strRepr(x);
  if (Array.isArray(x)) return '[' + x.map(pyRepr).join(', ') + ']';
  if (x instanceof Map) return '{' + [...x].map(([k, v]) => `${strRepr(k)}: ${pyRepr(v)}`).join(', ') + '}';
  return String(x);
}

// a == b with Python semantics (True == 1, 1 == 1.0, dicts compare by content).
export function pyEq(a, b) {
  const numeric = (x) => typeof x === 'number' || typeof x === 'boolean' || x instanceof PyFloat;
  if (numeric(a) && numeric(b)) return num(a) === num(b);
  if (typeof a === 'string' || typeof b === 'string' || a === null || b === null) return a === b;
  if (Array.isArray(a) && Array.isArray(b)) return a.length === b.length && a.every((v, i) => pyEq(v, b[i]));
  if (a instanceof Map && b instanceof Map) return a.size === b.size && [...a].every(([k, v]) => b.has(k) && pyEq(v, b.get(k)));
  return false;
}

export function deepCopy(x) {
  if (Array.isArray(x)) return x.map(deepCopy);
  if (x instanceof Map) return new Map([...x].map(([k, v]) => [k, deepCopy(v)]));
  return x; // ints, floats, strings, bools and None are immutable
}

// json.dumps(value, indent=2[, sort_keys=True]).
export function dumps(x, { sortKeys = false, indent = 2 } = {}, depth = 0) {
  const pad = (d) => '\n' + ' '.repeat(indent * d);
  if (x === null || x === undefined) return 'null';
  if (typeof x === 'boolean') return String(x);
  if (x instanceof PyFloat) return Number.isNaN(x.v) ? 'NaN' : !Number.isFinite(x.v) ? (x.v < 0 ? '-Infinity' : 'Infinity') : floatRepr(x.v);
  if (typeof x === 'number') return String(x);
  if (typeof x === 'string') return JSON.stringify(x);
  if (Array.isArray(x)) {
    if (!x.length) return '[]';
    return '[' + x.map((v) => pad(depth + 1) + dumps(v, { sortKeys, indent }, depth + 1)).join(',') + pad(depth) + ']';
  }
  const entries = [...x];
  if (!entries.length) return '{}';
  if (sortKeys) entries.sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0));
  return '{' + entries.map(([k, v]) => pad(depth + 1) + JSON.stringify(k) + ': ' + dumps(v, { sortKeys, indent }, depth + 1)).join(',') + pad(depth) + '}';
}
// Exact equality including int versus float: used by the parity checks.
export const same = (a, b) => dumps(a, { sortKeys: true }) === dumps(b, { sortKeys: true });

// json.loads(text) with CPython 3.12's acceptance rules and error messages (exc.msg).
export class JSONDecodeError extends Error {}
export function loads(text) {
  let i = 0;
  const fail = (msg) => { throw new JSONDecodeError(msg); };
  const ws = () => { while (i < text.length && ' \t\n\r'.includes(text[i])) i++; };
  const value = () => {
    const c = text[i];
    if (c === '"') return string();
    if (c === '{') return object();
    if (c === '[') return array();
    for (const [lit, v] of [['null', null], ['true', true], ['false', false], ['NaN', F(NaN)], ['Infinity', F(Infinity)], ['-Infinity', F(-Infinity)]])
      if (text.startsWith(lit, i)) { i += lit.length; return v; }
    const m = /^(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?/.exec(text.slice(i));
    if (!m) fail('Expecting value');
    i += m[0].length;
    return m[2] || m[3] ? F(Number(m[0])) : Number(m[1]) + 0;
  };
  const string = () => {
    i++;
    let out = '';
    for (;;) {
      if (i >= text.length) fail('Unterminated string starting at');
      const c = text[i++];
      if (c === '"') return out;
      if (c < ' ') fail('Invalid control character at');
      if (c !== '\\') { out += c; continue; }
      const e = text[i++];
      const map = { '"': '"', '\\': '\\', '/': '/', b: '\b', f: '\f', n: '\n', r: '\r', t: '\t' };
      if (e in map) out += map[e];
      else if (e === 'u') {
        const h = text.slice(i, i + 4);
        if (!/^[0-9a-fA-F]{4}$/.test(h)) fail('Invalid \\uXXXX escape');
        out += String.fromCharCode(parseInt(h, 16)); i += 4;
      } else fail('Invalid \\escape');
    }
  };
  const object = () => {
    i++; ws();
    const out = new Map();
    if (text[i] === '}') { i++; return out; }
    for (;;) {
      if (text[i] !== '"') fail('Expecting property name enclosed in double quotes');
      const k = string(); ws();
      if (text[i] !== ':') fail("Expecting ':' delimiter");
      i++; ws();
      out.set(k, value()); ws();
      if (text[i] === '}') { i++; return out; }
      if (text[i] !== ',') fail("Expecting ',' delimiter");
      i++; ws();
    }
  };
  const array = () => {
    i++; ws();
    const out = [];
    if (text[i] === ']') { i++; return out; }
    for (;;) {
      out.push(value()); ws();
      if (text[i] === ']') { i++; return out; }
      if (text[i] !== ',') fail("Expecting ',' delimiter");
      i++; ws();
    }
  };
  ws();
  const v = value();
  ws();
  if (i !== text.length) fail('Extra data');
  return v;
}
