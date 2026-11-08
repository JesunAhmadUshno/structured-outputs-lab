import { useMemo, useState, useEffect, useId } from 'react';
import casesRaw from '../../level-1-learn/cases.json?raw';
import corpusSrc from '../../level-2-build/corpus.py?raw';
import buildRaw from '../../level-2-build/results_build.json?raw';
import deepRaw from '../../level-3-deep/results_deep.json?raw';
import evalDeepRaw from '../../level-3-deep/evaluation_deep.json?raw';
import suppRaw from '../../level-3-deep/supplement.json?raw';
import unc from '../../level-3-deep/uncertainty.json';
import report from '../../REPORT.md?raw';
import { loads, dumps, pyRepr } from './py.js';
import { runCase, callFunction, FUNCTIONS, extractAndValidate, parseCorpus, evaluateDeep, evaluateSupplement, wilson, countTests, RULES, MAX_ROUNDS, DEFECT_CLASSES } from './lab.js';

const REPO = 'https://github.com/JesunAhmadUshno/structured-outputs-lab';
const blob = (p) => `${REPO}/blob/main/${p}`;
const f3 = (x) => (+x).toFixed(3);
const show = (v) => (v === undefined ? '' : dumps(v));
const sorted = (v) => dumps(v, { sortKeys: true }); // same key order on both sides of a comparison

// Everything below is read from the repo at build time.
const CASES = loads(casesRaw);
const DOCS = parseCorpus(corpusSrc);
const BUILD = loads(buildRaw);
const DEEP = loads(deepRaw);
const EVAL_DEEP = loads(evalDeepRaw);
const BS = BUILD.get('summary');
const DS = DEEP.get('summary');
const L1 = CASES.map(runCase);
const TEST_FILES = Object.entries(import.meta.glob('../../tests/*.py', { query: '?raw', import: 'default', eager: true }))
  .map(([p, src]) => [p.split('/').pop(), countTests(src)]).filter(([, n]) => n > 0);
const TESTS_TOTAL = TEST_FILES.reduce((a, [, n]) => a + n, 0);
const RECORDED_RUN = evaluateDeep(DOCS, EVAL_DEEP);
const SUPP = evaluateSupplement(loads(suppRaw));

// Pulls a "## heading" section's bullet or numbered list out of a markdown file.
function mdList(md, heading) {
  const body = md.split(`## ${heading}`)[1]?.split('\n## ')[0] ?? '';
  return body.split(/\n(?:- |\d+\. )/).slice(1).map((t) => t.replace(/\s+/g, ' ').trim());
}
const LIMITS = { 'Level 1': mdList(report, 'Limits: validator and dispatcher'), 'Level 2': mdList(report, 'Limits: extraction pipeline'), 'Level 3': mdList(report, 'Limits: repair loop') };
const BACKLOG = mdList(report, 'Open backlog');
if (Object.values(LIMITS).some((l) => !l.length) || !BACKLOG.length) throw new Error('REPORT.md is missing a Limits or Open backlog section the dashboard quotes');

const SECTIONS = [['top', 'Overview', '{}'], ['flow', 'Pipeline', '⇢'], ['learn', 'Validator', '✓'], ['build', 'Extraction', '¶'], ['deep', 'Repair loop', '↻'], ['whatif', 'What-if', '⚙'], ['followup', 'Follow-up set', '+'], ['classes', 'Defect classes', '▥'], ['limits', 'Limits', '!'], ['reproduce', 'Reproduce', '❯_']];

function useReveal() {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window)) { els.forEach((e) => e.classList.add('in')); return; }
    const io = new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.08 });
    els.forEach((e) => io.observe(e));
    return () => io.disconnect();
  }, []);
}

function MenuBar() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => { const t = setInterval(() => setNow(new Date()), 30000); return () => clearInterval(t); }, []);
  return (
    <div className="menubar" role="banner">
      <span className="apple" aria-hidden="true">◆</span>
      <a className="app" href="#top">Structured Outputs Lab</a>
      <a className="m" href={blob('PROPOSAL.md')}>Proposal</a>
      <a className="m" href={blob('REPORT.md')}>Report</a>
      <span className="spacer" />
      <span className="status"><i /> Ports parity-checked at build</span>
      <a href={REPO}>GitHub ↗</a>
      <span className="clock">{now.toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit' })}</span>
    </div>
  );
}

function Dock() {
  const [active, setActive] = useState('top');
  useEffect(() => {
    const io = new IntersectionObserver((es) => es.forEach((e) => e.isIntersecting && setActive(e.target.id)), { rootMargin: '-45% 0px -50% 0px' });
    SECTIONS.forEach(([id]) => { const el = document.getElementById(id); if (el) io.observe(el); });
    return () => io.disconnect();
  }, []);
  return (
    <nav className="dock" aria-label="Sections">
      {SECTIONS.map(([id, label, icon]) => (
        <a key={id} href={`#${id}`} className={active === id ? 'on' : ''} aria-current={active === id ? 'true' : undefined} aria-label={label}>
          <span className="ico" aria-hidden="true">{icon}</span><span className="lbl">{label}</span>
        </a>
      ))}
    </nav>
  );
}

function Range({ label, value, min, max, step, onChange, show: shown }) {
  const id = useId();
  return (
    <div className="field">
      <label htmlFor={id}>{label} <span>{shown}</span></label>
      <input id={id} type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(+e.target.value)} />
    </div>
  );
}

export default function App() {
  useReveal();
  return (
    <div className="wrap">
      <MenuBar />
      <div className="glow" aria-hidden="true" />
      <Hero />
      <Flow />
      <Learn />
      <Build />
      <Deep />
      <WhatIf />
      <FollowUp />
      <Classes />
      <Limits />
      <Reproduce />
      <Dock />
      <footer>
        All {DOCS.length} documents are synthetic and no language model is in any measured loop. Code: Apache-2.0. Every number on this page is read from <code>level-*/</code> and <code>tests/</code> at build time;
        the playgrounds run JavaScript ports of the Python code, and the build fails unless the ports reproduce the committed results exactly.
      </footer>
    </div>
  );
}

function Hero() {
  const l1Matched = L1.filter((r) => r.match).length;
  const rr = unc.repair_rate.wilson95, sr = unc.silent_failure_rate.wilson95;
  return (
    <header className="card hero window" id="top" data-title="heal.py · self-healing parse loop">
      <div className="head">
        <p className="eyebrow">Strict schemas · validated extraction · logged repairs</p>
        <span className="pill info">● {DS.get('matched')} of {DS.get('attempted')} matched the pre-labelled outcome</span>
      </div>
      <h1>Self-healing JSON fixes shapes, not <em>facts</em>: of {DS.get('attempted')} rejected documents the repair loop healed {DS.get('healed')}, and {DS.get('silent_failures')} of those {DS.get('healed')} now state a value the source never said.</h1>
      <p className="sub">
        A three-level study of what sits between a model&apos;s output and your code: a strict JSON Schema subset validator guarding function calls, a document extraction pipeline that rejects bad records instead of passing them, and a bounded repair loop that logs every change.
        The extractor is rule based and the documents are synthetic, so these are properties of the guard and the rules, not of any model.
      </p>
      <div className="actions">
        <a className="btn primary" href="#deep">Step through a repair</a>
        <a className="btn ghost" href="#learn">Try the validator</a>
        <span className="hint">Reproduce with <code>python3 level-3-deep/run_deep.py</code></span>
      </div>
      <div className="tiles">
        <div className="tile"><div className="num">{l1Matched}/{L1.length}</div><div className="cap">Level 1 function calls handled as labelled; {L1.filter((r) => r.ok).length} dispatched, {L1.filter((r) => !r.ok).length} stopped before the function ran</div></div>
        <div className="tile"><div className="num">{BS.get('matched')}/{BUILD.get('documents')}</div><div className="cap">Level 2 documents routed as labelled; {BS.get('fields_correct')}/{BS.get('fields_total')} fields extracted correctly</div></div>
        <div className="tile"><div className="num">{BS.get('malformed_caught')}/{BS.get('malformed_total')}</div><div className="cap">Malformed documents caught, {BS.get('false_accepts')} false accepts (95% CI from {f3(unc.validation_catch_rate.wilson95[0])})</div></div>
        <div className="tile"><div className="num">{DS.get('valid_records_altered')}/{DEEP.get('build_accepted_checked')}</div><div className="cap">Valid records altered when fed through the repair loop</div></div>
        <div className="tile"><div className="num">{DS.get('healed')}/{DS.get('attempted')}</div><div className="cap">Repair rate {f3(DS.get('repair_rate'))}; Wilson 95% {f3(rr[0])} to {f3(rr[1])}</div></div>
        <div className="tile"><div className="num">{DS.get('silent_failures')}/{DS.get('healed')}</div><div className="cap">Silent failure rate {f3(DS.get('silent_failure_rate'))}; Wilson 95% {f3(sr[0])} to {f3(sr[1])}</div></div>
        <div className="tile"><div className="num">{DS.get('healed_flagged')}</div><div className="cap">Heals that changed a stated value (clamps), each flagged in the log</div></div>
        <div className="tile"><div className="num">{TESTS_TOTAL}</div><div className="cap">Unit tests defined across {TEST_FILES.length} files in <code>tests/</code></div></div>
      </div>
    </header>
  );
}

// Boxes and arrows for the flow. Counts come from the results files.
function FlowSvg({ vertical }) {
  const st = { clean: DS.get('healed_clean'), flagged: DS.get('healed_flagged'), still: DS.get('still_rejected') };
  const nodes = vertical
    ? [['doc', 100, 10, 'documents', `${BUILD.get('documents')} synthetic`], ['ext', 100, 80, 'extractor', 'regex, rule based'], ['val', 100, 150, 'validate', 'Level 1, unchanged'],
      ['acc', 10, 230, 'accepted', `${BS.get('accepted')} records`], ['rej', 190, 230, 'rejected', `${BS.get('rejected')} records`], ['heal', 190, 310, 'heal loop', `≤ ${MAX_ROUNDS} rounds`],
      ['hc', 10, 400, 'healed_clean', `${st.clean}`], ['hf', 130, 400, 'healed_flagged', `${st.flagged}`], ['sr', 250, 400, 'still_rejected', `${st.still}`]]
    : [['doc', 10, 70, 'documents', `${BUILD.get('documents')} synthetic`], ['ext', 150, 70, 'extractor', 'regex, rule based'], ['val', 290, 70, 'validate', 'Level 1, unchanged'],
      ['acc', 450, 10, 'accepted', `${BS.get('accepted')} records`], ['rej', 450, 130, 'rejected', `${BS.get('rejected')} records`], ['heal', 610, 130, 'heal loop', `≤ ${MAX_ROUNDS} rounds`],
      ['hc', 790, 30, 'healed_clean', `${st.clean} record`], ['hf', 790, 130, 'healed_flagged', `${st.flagged} records`], ['sr', 790, 230, 'still_rejected', `${st.still} records`]];
  const w = vertical ? 110 : 120, h = 52;
  const at = Object.fromEntries(nodes.map(([k, x, y]) => [k, { x, y }]));
  const edges = [['doc', 'ext'], ['ext', 'val'], ['val', 'acc'], ['val', 'rej'], ['rej', 'heal'], ['heal', 'hc'], ['heal', 'hf'], ['heal', 'sr']];
  const tone = { acc: 'good', hc: 'good', hf: 'warn', sr: 'bad', rej: 'bad' };
  const W = vertical ? 360 : 920, H = vertical ? 462 : 292;
  const port = (k, out) => {
    const p = at[k];
    return vertical ? [p.x + w / 2, out ? p.y + h : p.y] : [out ? p.x + w : p.x, p.y + h / 2];
  };
  return (
    <svg className={`chart flow ${vertical ? 'narrow' : 'wide'}`} viewBox={`0 0 ${W} ${H}`} role="img"
      aria-label={`Pipeline: ${BUILD.get('documents')} documents, ${BS.get('accepted')} accepted, ${BS.get('rejected')} rejected; the heal loop ends with ${st.clean} healed clean, ${st.flagged} healed flagged, ${st.still} still rejected`}>
      <defs><marker id={`ah${vertical ? 'v' : 'h'}`} viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L8 4L0 8z" fill="var(--muted)" /></marker></defs>
      {edges.map(([a, b]) => {
        const [x1, y1] = port(a, true), [x2, y2] = port(b, false);
        const d = vertical ? `M${x1} ${y1} C${x1} ${(y1 + y2) / 2} ${x2} ${(y1 + y2) / 2} ${x2} ${y2 - 2}` : `M${x1} ${y1} C${(x1 + x2) / 2} ${y1} ${(x1 + x2) / 2} ${y2} ${x2 - 2} ${y2}`;
        return <path key={a + b} d={d} fill="none" stroke="var(--muted)" strokeOpacity="0.55" strokeWidth="1.5" markerEnd={`url(#ah${vertical ? 'v' : 'h'})`} />;
      })}
      {nodes.map(([k, x, y, label, sub]) => (
        <g key={k} className={`node ${tone[k] || ''}`}>
          <rect x={x} y={y} width={w} height={h} rx="10" />
          <text x={x + w / 2} y={y + 22} textAnchor="middle" className="nl">{label}</text>
          <text x={x + w / 2} y={y + 40} textAnchor="middle">{sub}</text>
        </g>
      ))}
    </svg>
  );
}

function Flow() {
  return (
    <section id="flow" className="card window reveal" data-title="pipeline.svg">
      <p className="eyebrow">How a record moves</p>
      <h2>One validator, reused at every level, decides what gets through.</h2>
      <p className="sub">
        Each synthetic document goes through a deterministic extractor, then the same strict validator that guards function calls in Level 1.
        Rejected records go to the repair loop, which applies only named rules, re-validates after each round and stops after {MAX_ROUNDS} rounds. Counts are from <a href={blob('level-2-build/results_build.json')}>results_build.json</a> and <a href={blob('level-3-deep/results_deep.json')}>results_deep.json</a>.
      </p>
      <div style={{ marginTop: 16 }}>
        <FlowSvg />
        <FlowSvg vertical />
      </div>
    </section>
  );
}

function ErrorTable({ errors }) {
  if (!errors.length) return null;
  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead><tr><th>Path</th><th>Code</th><th>Message</th></tr></thead>
        <tbody>{errors.map((e, i) => <tr key={i}><td className="mono">{e.get('path')}</td><td className="mono">{e.get('code')}</td><td>{e.get('message')}</td></tr>)}</tbody>
      </table>
    </div>
  );
}

const argsText = (a) => (typeof a === 'string' ? a : dumps(a));

function Learn() {
  const [pick, setPick] = useState(4);
  const [name, setName] = useState(CASES[4].get('function'));
  const [args, setArgs] = useState(argsText(CASES[4].get('arguments')));
  const choose = (i) => {
    setPick(i);
    if (i >= 0) { setName(CASES[i].get('function')); setArgs(argsText(CASES[i].get('arguments'))); }
  };
  const out = useMemo(() => callFunction(name, args), [name, args]);
  const c = pick >= 0 ? CASES[pick] : null;
  const edited = c && (name !== c.get('function') || args !== argsText(c.get('arguments')));
  return (
    <section id="learn" className="card window reveal" data-title="function_calling.py · playground">
      <div className="head">
        <div>
          <p className="eyebrow">Level 1 · live in your browser</p>
          <h2>Invalid arguments never reach the function.</h2>
          <p className="sub">
            Pick one of the {CASES.length} recorded cases from <a href={blob('level-1-learn/cases.json')}>cases.json</a> or write your own call. A port of <a href={blob('level-1-learn/schema_validate.py')}>schema_validate.py</a> and the dispatcher checks it the way the Python does:
            unknown name, then JSON parse, then strict schema. Python types are kept, so <code>45.0</code> is a float and is rejected where an integer is required.
          </p>
        </div>
        <span className={`pill ${out.ok ? 'good' : 'bad'}`}>{out.ok ? '● accepted, function called' : '● rejected, function not called'}</span>
      </div>
      <div className="grid2">
        <div>
          <div className="controls" style={{ gridTemplateColumns: '1fr' }}>
            <div className="field"><label htmlFor="case">Recorded case</label>
              <select id="case" value={pick} onChange={(e) => choose(+e.target.value)}>
                {CASES.map((k, i) => <option key={k.get('id')} value={i}>{k.get('id')}</option>)}
                <option value={-1}>Your own call</option>
              </select>
            </div>
            <div className="field"><label htmlFor="fname">Function name</label>
              <input id="fname" type="text" value={name} spellCheck="false" aria-describedby="fnames" onChange={(e) => { setName(e.target.value); }} />
              <p className="hint" id="fnames" style={{ margin: '6px 0 0' }}>Registered: <span className="mono">{Object.keys(FUNCTIONS).join(', ')}</span></p>
            </div>
            <div className="field"><label htmlFor="fargs">Arguments (JSON text, as a model would emit)</label>
              <textarea id="fargs" rows="6" value={args} spellCheck="false" onChange={(e) => setArgs(e.target.value)} />
            </div>
          </div>
          {c && (
            <p className="hint">
              Recorded expectation: <b>{c.get('expect_ok') ? 'accept' : 'reject'}</b>{c.has('expect_first_path') && <> at <span className="mono">{c.get('expect_first_path')}</span></>}.{' '}
              {edited ? 'You have edited this case.' : L1[pick].match ? 'The port matches it.' : 'The port does not match it.'}
            </p>
          )}
        </div>
        <div>
          <h3>Schema for <span className="mono">{Object.hasOwn(FUNCTIONS, name) ? name : 'unknown'}</span></h3>
          <pre className="code">{Object.hasOwn(FUNCTIONS, name) ? JSON.stringify(FUNCTIONS[name].schema, null, 1) : '// no such function: the call is refused before parsing'}</pre>
        </div>
      </div>
      <div style={{ marginTop: 16 }}>
        {out.ok ? (<><h3>Function result</h3><pre className="code">{dumps(out.result)}</pre></>) : (<><h3>{out.errors.length} error{out.errors.length === 1 ? '' : 's'}, first at <span className="mono">{out.errors[0].get('path')}</span></h3><ErrorTable errors={out.errors} /></>)}
      </div>
    </section>
  );
}

function Build() {
  const [pick, setPick] = useState(11);
  const [text, setText] = useState(DOCS[11].text);
  const doc = DOCS[pick];
  const out = useMemo(() => extractAndValidate({ ...doc, text }), [doc, text]);
  const recorded = BUILD.get('per_document');
  return (
    <section id="build" className="card window reveal" data-title="pipeline.py · extraction lab">
      <div className="head">
        <div>
          <p className="eyebrow">Level 2 · live in your browser</p>
          <h2>Edit a document and watch the strict schema answer.</h2>
          <p className="sub">
            A port of the three regex extractors in <a href={blob('level-2-build/pipeline.py')}>pipeline.py</a>, fed the {DOCS.length} synthetic documents read straight from <a href={blob('level-2-build/corpus.py')}>corpus.py</a>.
            A token that does not parse stays a string, so the validator reports the type error instead of the extractor hiding it. Try <code>Total: 1_200.50</code> or <code>Stock: 4.5</code>.
          </p>
        </div>
        <span className={`pill ${out.accepted ? 'good' : 'bad'}`}>{out.accepted ? '● accepted' : `● rejected, ${out.errors.length} error${out.errors.length === 1 ? '' : 's'}`}</span>
      </div>
      <div className="grid2">
        <div>
          <div className="field"><label htmlFor="doc">Synthetic document <span>{doc.doc_type}</span></label>
            <select id="doc" value={pick} onChange={(e) => { setPick(+e.target.value); setText(DOCS[+e.target.value].text); }}>
              {DOCS.map((d, i) => <option key={d.id} value={i}>{d.id}</option>)}
            </select>
          </div>
          <div className="field" style={{ marginTop: 12 }}><label htmlFor="doctext">Document text {text !== doc.text && <button className="linkbtn" onClick={() => setText(doc.text)}>reset</button>}</label>
            <textarea id="doctext" rows="7" value={text} spellCheck="false" onChange={(e) => setText(e.target.value)} />
          </div>
        </div>
        <div>
          <h3>Extracted candidate record</h3>
          <pre className="code">{show(out.record)}</pre>
        </div>
      </div>
      <div style={{ marginTop: 12 }}><ErrorTable errors={out.errors} /></div>
      <h3 style={{ marginTop: 24 }}>Recorded run, all {recorded.length} documents <span className="pill info" style={{ marginLeft: 6 }}>recorded · results_build.json</span></h3>
      <div style={{ overflowX: 'auto', marginTop: 8 }}>
        <table>
          <thead><tr><th>Document</th><th>Type</th><th>Expected</th><th>Actual</th><th>First error path</th><th>Fields</th><th>Match</th></tr></thead>
          <tbody>
            {recorded.map((r) => (
              <tr key={r.get('id')}><td className="mono">{r.get('id')}</td><td>{r.get('doc_type')}</td><td>{r.get('expected')}</td><td>{r.get('actual')}</td>
                <td className="mono">{r.get('first_error_path') ?? '-'}</td><td>{r.get('fields_total') === null ? '-' : `${r.get('fields_correct')}/${r.get('fields_total')}`}</td>
                <td className={r.get('match') ? 'ok' : 'no'}>{r.get('match') ? 'MATCH' : 'MISMATCH'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Deep() {
  const docs = RECORDED_RUN.perDocument;
  const first = docs.findIndex((d) => d.status === 'healed_flagged');
  const [pick, setPick] = useState(first);
  const [step, setStep] = useState(docs[first].repair_log.length); // open on the end state so the clamp is visible
  const d = docs[pick];
  const steps = d.repair_log.length;
  const done = step === steps;
  const statusTone = { healed_clean: 'good', healed_flagged: 'warn', still_rejected: 'bad' }[d.status];
  const compareTo = d.truthful ?? d.true_record;
  return (
    <section id="deep" className="card window reveal" data-title="run_deep.py · repair stepper">
      <div className="head">
        <div>
          <p className="eyebrow">Level 3 · live in your browser</p>
          <h2>Step through every repair, and see where a heal becomes a <em>false fact</em>.</h2>
          <p className="sub">
            The loop runs here as a port of <a href={blob('level-3-deep/heal.py')}>heal.py</a> over the {docs.length} Build rejections; the build fails unless its records and logs equal <a href={blob('level-3-deep/results_deep.json')}>results_deep.json</a>.
            On the right is the labelled record from <a href={blob('level-3-deep/evaluation_deep.json')}>evaluation_deep.json</a>, written before the run.
          </p>
        </div>
        <span className={`pill ${statusTone}`}>● {d.status}</span>
      </div>
      <div className="controls">
        <div className="field"><label htmlFor="rej">Rejected document <span>{d.defect_class}</span></label>
          <select id="rej" value={pick} onChange={(e) => { setPick(+e.target.value); setStep(0); }}>
            {docs.map((x, i) => <option key={x.id} value={i}>{x.id}</option>)}
          </select>
        </div>
        <div className="field"><span className="flabel">Step {step} of {steps}</span>
          <div className="actions" style={{ marginTop: 0 }}>
            <button className="btn ghost" onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0}>← Back</button>
            <button className="btn primary" onClick={() => setStep(Math.min(steps, step + 1))} disabled={done}>Next repair →</button>
          </div>
        </div>
      </div>
      <ol className="log" aria-live="polite">
        {d.repair_log.slice(0, step).map((e, i) => (
          <li key={i} className={i === step - 1 ? 'cur' : ''}>
            <span className="mono">round {e.get('round')} · {e.get('path')} · {e.get('code')}</span>
            <b className="mono">{e.get('rule')}</b>
            <span className="mono">{pyRepr(e.get('before'))} → {pyRepr(e.get('after'))}</span>
            <span className={`pill ${e.get('value_changing') ? 'warn' : e.get('outcome') === 'applied' ? 'good' : 'bad'}`}>{e.get('value_changing') ? 'value changed' : e.get('outcome')}</span>
          </li>
        ))}
        {step === 0 && <li className="hint">Press “Next repair” to apply the first logged attempt.</li>}
      </ol>
      {done && (
        <p className="hint">
          Ended <b>{d.status}</b> after {d.rounds} round{d.rounds === 1 ? '' : 's'}{d.healed ? (d.silent_failure ? ': the record validates, but it does not equal any truthful record, so it counts as a silent failure.' : ': the healed record equals the labelled truthful record.') : `: ${d.errors.length} error${d.errors.length === 1 ? '' : 's'} remain, no rule can safely repair ${d.errors.length === 1 ? 'it' : 'them'}.`}
        </p>
      )}
      <div className="grid2" style={{ marginTop: 12 }}>
        <div><h3>{done ? 'Final record' : 'Record before repair'}</h3><pre className="code">{sorted(done ? d.record : d.original_record)}</pre></div>
        <div><h3>{d.truthful ? 'Labelled truthful healed record' : 'Labelled true record (what the document says)'}</h3><pre className="code">{sorted(compareTo)}</pre></div>
      </div>
    </section>
  );
}

function WhatIf() {
  const [rules, setRules] = useState(Object.fromEntries(RULES.map((r) => [r, true])));
  const [rounds, setRounds] = useState(MAX_ROUNDS);
  const run = useMemo(() => evaluateDeep(DOCS, EVAL_DEEP, { rules, maxRounds: rounds }), [rules, rounds]);
  const s = run.summary;
  const isDefault = rounds === MAX_ROUNDS && RULES.every((r) => rules[r]);
  const reproduces = s.repair_rate === +DS.get('repair_rate') && s.silent_failure_rate === +DS.get('silent_failure_rate');
  const ci = (k, n) => (n ? wilson(k, n).map(f3).join(' to ') : 'undefined (no heals)');
  const tone = { healed_clean: 'good', healed_flagged: 'warn', still_rejected: 'bad' };
  return (
    <section id="whatif" className="card window reveal" data-title="rules.json · what-if">
      <div className="head">
        <div>
          <p className="eyebrow">Rule ablation · what-if on the recorded set</p>
          <h2>Turn a rule off and the trade-off shows: fewer heals, or fewer false facts.</h2>
          <p className="sub">
            The same port re-runs the loop over the {s.attempted} Build rejections and the {run.accepted} accepted records with your settings, scoring against the pre-labelled truthful records.
            This re-computes the existing set; it is not a new benchmark. The intervals are Wilson 95%, computed here from the counts, to show how little n = {s.attempted} can pin down.
          </p>
        </div>
        <span className={`pill ${isDefault && reproduces ? 'good' : 'info'}`}>{isDefault ? (reproduces ? '● defaults reproduce the recorded rates' : '● defaults do not match') : '● what-if settings'}</span>
      </div>
      <div className="controls">
        <fieldset className="checks"><legend>Repair rules</legend>
          {RULES.map((r) => (
            <label key={r}><input type="checkbox" checked={rules[r]} onChange={(e) => setRules({ ...rules, [r]: e.target.checked })} /> <span className="mono">{r}</span></label>
          ))}
        </fieldset>
        <Range label="max_rounds" value={rounds} min={1} max={5} step={1} onChange={setRounds} show={rounds === MAX_ROUNDS ? `${rounds} (repo default)` : rounds} />
      </div>
      <div className="tiles" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', marginTop: 0 }}>
        <div className="tile"><div className="num">{s.healed}/{s.attempted}</div><div className="cap">Repair rate {f3(s.repair_rate)}; 95% {ci(s.healed, s.attempted)}</div></div>
        <div className="tile"><div className="num">{s.silent_failures}/{s.healed}</div><div className="cap">Silent failure rate {s.healed ? f3(s.silent_failure_rate) : 'n/a'}; 95% {ci(s.silent_failures, s.healed)}</div></div>
        <div className="tile"><div className="num">{s.valid_records_altered}/{run.accepted}</div><div className="cap">Valid records altered by the loop</div></div>
      </div>
      <div className="chips" style={{ marginTop: 16 }}>
        {run.perDocument.map((d) => <span key={d.id} className={`pill ${tone[d.status]}`} title={d.status}><span className="mono">{d.id.slice(0, 3)}</span> {d.status.replace('_', ' ')}</span>)}
      </div>
    </section>
  );
}

function FollowUp() {
  const s = SUPP.summary;
  const rr = unc.supplement_repair_rate.wilson95, sr = unc.supplement_silent_failure_rate.wilson95;
  const tone = { healed_clean: 'good', healed_flagged: 'warn', still_rejected: 'bad' };
  return (
    <section id="followup" className="card window reveal" data-title="run_supplement.py · follow-up set">
      <div className="head">
        <div>
          <p className="eyebrow">Follow-up set · labelled before the run</p>
          <h2>Numeric strings heal cleanly; a clamp still turns a heal into a <em>false fact</em>.</h2>
          <p className="sub">
            The v1.0 benchmark never exercises the coercion rule, because the extractor already parses numbers. This follow-up feeds {s.attempted} candidate records straight to the loop, shaped like model JSON:
            numeric strings in typed fields, and records with two or three defects at once. The labels in <a href={blob('level-3-deep/supplement.json')}>supplement.json</a> were committed before <a href={blob('level-3-deep/run_supplement.py')}>run_supplement.py</a> existed.
            The rows below are re-computed by the port and checked against <a href={blob('level-3-deep/results_supplement.json')}>results_supplement.json</a> at build. It is a second small designed set, not model output.
          </p>
        </div>
        <span className={`pill ${s.matched === s.attempted ? 'good' : 'bad'}`}>● {s.matched} of {s.attempted} matched the label</span>
      </div>
      <div className="tiles" style={{ gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', marginTop: 0 }}>
        <div className="tile"><div className="num">{s.healed}/{s.attempted}</div><div className="cap">Repair rate {f3(s.repair_rate)}; Wilson 95% {f3(rr[0])} to {f3(rr[1])}</div></div>
        <div className="tile"><div className="num">{s.silent_failures}/{s.healed}</div><div className="cap">Silent failure rate {f3(s.silent_failure_rate)}; Wilson 95% {f3(sr[0])} to {f3(sr[1])}</div></div>
        <div className="tile"><div className="num">{s.coerce_repairs_applied}</div><div className="cap">Numeric-string coercions applied (0 in the v1.0 benchmark)</div></div>
      </div>
      <div style={{ overflowX: 'auto', marginTop: 16 }}>
        <table>
          <thead><tr><th>Record</th><th>Defects</th><th>Repairs, in order</th><th>Rounds</th><th>Status</th><th>Silent</th></tr></thead>
          <tbody>
            {SUPP.perRecord.map((r) => (
              <tr key={r.id}><td className="mono">{r.id.slice(0, 3)}</td><td>{r.defects.join(' + ')}</td>
                <td className="mono">{r.repair_log.map((l) => l.get('rule').replace('none_unrepairable', 'unrepairable')).join(' → ')}</td>
                <td>{r.rounds}</td><td><span className={`pill ${tone[r.status]}`}>{r.status}</span></td><td>{r.silent_failure === null ? '-' : r.silent_failure ? 'yes' : 'no'}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function Classes() {
  const pc = DEEP.get('per_defect_class');
  const word = (n) => ['no', 'one', 'two', 'three', 'four', 'five'][n] ?? String(n);
  const healing = DEFECT_CLASSES.filter((c) => pc.get(c).get('healed') > 0);
  const honest = healing.filter((c) => pc.get(c).get('silent_failures') === 0);
  const series = [['attempted', 'Attempted', 'var(--muted)'], ['healed', 'Healed', 'var(--primary)'], ['healed_flagged', 'Healed with a changed value', 'var(--warn)'], ['silent_failures', 'Silent failures', 'var(--bad)']];
  const max = Math.max(...DEFECT_CLASSES.map((c) => pc.get(c).get('attempted')));
  const W = 520, H = 290, pad = { l: 34, r: 8, t: 14, b: 58 };
  const gw = (W - pad.l - pad.r) / DEFECT_CLASSES.length, bw = (gw - 18) / series.length;
  const y = (v) => pad.t + (1 - v / max) * (H - pad.t - pad.b);
  return (
    <section id="classes" className="card window reveal" data-title="per_defect_class.svg">
      <p className="eyebrow">Per defect class · recorded</p>
      <h2>Only {word(healing.length)} kinds of defect heal, and only {word(honest.length)} heals honestly.</h2>
      <p className="sub">
        From <span className="mono">per_defect_class</span> in <a href={blob('level-3-deep/results_deep.json')}>results_deep.json</a>. Missing fields are never invented and bad enum values are never guessed, so they stay rejected by design.
        Both wrong-type documents hold strings that do not parse (<code>FREE</code>, <code>many</code>), so the coercion rule is never exercised by this set.
      </p>
      <div className="grid2" style={{ marginTop: 16, alignItems: 'center' }}>
        <svg className="chart classes" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Grouped bars of attempted, healed, flagged and silent failure counts for each defect class">
          {Array.from({ length: max + 1 }, (_, v) => <g key={v}><line className="axis" x1={pad.l} x2={W - pad.r} y1={y(v)} y2={y(v)} /><text x={pad.l - 8} y={y(v) + 4} textAnchor="end">{v}</text></g>)}
          {DEFECT_CLASSES.map((c, i) => (
            <g key={c} transform={`translate(${pad.l + i * gw + 9} 0)`}>
              {series.map(([k, label, col], j) => {
                const v = pc.get(c).get(k);
                return <rect key={k} x={j * bw} y={y(v)} width={bw - 3} height={Math.max(0, y(0) - y(v))} rx="3" fill={col}><title>{`${c}: ${label} ${v}`}</title></rect>;
              })}
              <text x={(gw - 18) / 2} y={H - pad.b + 22 + (i % 2) * 22} textAnchor="middle" className="cl">{c}</text>
            </g>
          ))}
        </svg>
        <div>
          <div className="legend" style={{ flexDirection: 'column', gap: 8 }}>
            {series.map(([k, label, col]) => <span key={k}><i style={{ background: col }} />{label}</span>)}
          </div>
          <div style={{ overflowX: 'auto', marginTop: 12 }}>
            <table>
              <thead><tr><th>Class</th>{['Attempted', 'Healed', 'Flagged', 'Silent'].map((l) => <th key={l}>{l}</th>)}</tr></thead>
              <tbody>{DEFECT_CLASSES.map((c) => <tr key={c}><td className="mono">{c}</td>{series.map(([k]) => <td key={k}>{pc.get(c).get(k)}</td>)}</tr>)}</tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
}

function Limits() {
  const [tab, setTab] = useState('Level 3');
  return (
    <section id="limits" className="card window reveal" data-title="LIMITS.md">
      <div className="head">
        <div>
          <p className="eyebrow">Limits and threats to validity</p>
          <h2>What these numbers cannot tell you.</h2>
          <p className="sub">
            Quoted from the limits sections of <a href={blob('REPORT.md')}>REPORT.md</a>, plus the gaps found in its 2026-11-07 review.
          </p>
        </div>
        <div className="seg" role="group" aria-label="Level">
          {Object.keys(LIMITS).map((k) => <button key={k} aria-pressed={tab === k} onClick={() => setTab(k)}>{k}</button>)}
        </div>
      </div>
      <div className="grid2">
        <div>
          <h3>{tab} · REPORT.md limits</h3>
          <ul className="quote">{LIMITS[tab].map((t) => <li key={t}>{t}</li>)}</ul>
        </div>
        <div>
          <h3>Threats this review adds</h3>
          <ul className="quote plain">
            <li>No language model is measured anywhere. The extractor is regex based, so the rates describe the guard and the rules, not model output.</li>
            <li>Every rate rests on a handful of designed cases, one defect each. The intervals above are wide on purpose.</li>
            <li>The truthful records were labelled by the same author who designed the defects; there is no independent labelling.</li>
            <li>The validator is a teaching subset (no <code>$ref</code>, <code>oneOf</code>, <code>format</code>). It agrees with the jsonschema package on every measured input, and differs by design on floats such as <code>60.0</code> for integers.</li>
          </ul>
          <h3 style={{ marginTop: 16 }}>Open backlog (REPORT.md)</h3>
          <ol className="quote">{BACKLOG.map((t) => <li key={t}>{t.split(':')[0]}</li>)}</ol>
        </div>
      </div>
    </section>
  );
}

function Reproduce() {
  const steps = [
    ['Unit tests', 'python3 -m unittest discover -s tests', `${TESTS_TOTAL} tests across ${TEST_FILES.map(([f, n]) => `${f} (${n})`).join(', ')}.`],
    ['The three runners', 'python3 level-1-learn/run_cases.py && python3 level-2-build/run_build.py && python3 level-3-deep/run_deep.py', 'Each writes deterministic output; CI re-runs them and fails on any byte difference in the results files.'],
    ['Follow-up set', 'python3 level-3-deep/run_supplement.py', 'Numeric-string and multi-defect records, labelled before the run, written to results_supplement.json.'],
    ['Uncertainty', 'python3 level-3-deep/uncertainty.py', 'Wilson 95% intervals for each rate, written to level-3-deep/uncertainty.json.'],
    ['This dashboard', 'cd site && npm ci && npm run build', 'The build first runs src/lab.check.mjs: the JavaScript ports must reproduce all three results files exactly.'],
  ];
  const docs = [
    ['PROPOSAL.md', 'Proposal', 'Scope, prior work, designs (not locked)'],
    ['REPORT.md', 'Report', 'Results, hypotheses scored, limits, failure modes, review'],
    ['CHANGELOG.md', 'Changelog', 'What changed, and when'],
    ['fanout/tutorial.md', 'Tutorial', 'Course module walk-through'],
  ];
  return (
    <section id="reproduce" className="card window reveal" data-title="Terminal · reproduce">
      <p className="eyebrow">Reproduce it</p>
      <h2>Standard library Python, no keys, a few seconds.</h2>
      <ol className="steps" style={{ marginTop: 16 }}>
        {steps.map(([t, cmd, note], i) => <li key={t}><span className="n">{i + 1}</span><div><b>{t}</b><div className="hint"><code>{cmd}</code></div><div className="hint">{note}</div></div></li>)}
      </ol>
      <div className="docs" style={{ marginTop: 20 }}>
        {docs.map(([p, t, d]) => <a key={p} href={blob(p)}><b>{t}</b><small>{d}</small></a>)}
      </div>
      <p className="hint" style={{ marginTop: 16 }}><a href={`${REPO}/releases`}>Releases</a> · <a href={REPO}>Source on GitHub</a></p>
    </section>
  );
}
