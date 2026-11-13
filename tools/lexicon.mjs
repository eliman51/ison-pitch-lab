#!/usr/bin/env node
/* Builds the syllable and accent word list inside index.html (between the LEX markers).

   The app splits words into syllables with its own spelling rules (chWordSyl, chWordStress). Those rules are
   right for most words. This script checks every common English and Bible word against the CMU Pronouncing
   Dictionary and stores ONLY the words the rules get wrong, with their true syllables and accents.

   Needs a folder with: cmudict.dict (github.com/cmusphinx/cmudict), en50k.txt (a word frequency list),
   and any number of plain text files to take vocabulary from (for example a public domain Bible).
     node tools/lexicon.mjs /path/to/that/folder
   Run it again whenever chWordSyl or chWordStress change. */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const dir = process.argv[2];
if (!dir) { console.error('usage: node tools/lexicon.mjs <data folder>'); process.exit(1); }
const htmlPath = path.join(root, 'index.html');
let html = fs.readFileSync(htmlPath, 'utf8');

/* the app's own rules, taken straight from index.html so both always agree */
const a = html.indexOf('const CH_FN='), b = html.indexOf('/*END-RULES*/');
if (a < 0 || b < 0) { console.error('rule block not found in index.html'); process.exit(1); }
const rules = new Function(html.slice(a, b) + '\nreturn {chWordSyl,chWordStress,sgRulePat,CH_EX,SG_LIT};')();

/* CMU: first pronunciation of each word */
const cmu = new Map();
for (const line of fs.readFileSync(path.join(dir, 'cmudict.dict'), 'utf8').split('\n')) {
  const m = line.match(/^([a-z']+)(\(\d+\))? (.+?)( #.*)?$/); if (!m || m[2]) continue;
  if (!cmu.has(m[1])) cmu.set(m[1], m[3].split(' '));
}
/* vocabulary: frequent words plus every word of the text files in the folder */
const vocab = new Set();
fs.readFileSync(path.join(dir, 'en50k.txt'), 'utf8').split('\n').slice(0, 32000).forEach(l => { const w = l.split(' ')[0]; if (/^[a-z]+$/.test(w)) vocab.add(w); });
for (const f of fs.readdirSync(dir)) {
  if (!/\.txt$/.test(f) || f === 'en50k.txt') continue;
  for (const w of fs.readFileSync(path.join(dir, f), 'utf8').toLowerCase().match(/[a-z]+/g) || []) vocab.add(w);
}

const isVowelAt = (l, i) => { const n = l.length, c = l[i]; if ('aeio'.includes(c)) return true;
  if (c === 'u') return !(i > 0 && (l[i - 1] === 'q' || (l[i - 1] === 'g' && i + 1 < n && 'aeiou'.includes(l[i + 1]))));
  if (c === 'y') return !(i === 0 && n > 1 && 'aeiou'.includes(l[1])) && !(i > 0 && i + 1 < n && 'aeiou'.includes(l[i - 1]) && 'aeiou'.includes(l[i + 1]));
  return false; };
/* letters cut into exactly n syllables: choose which vowel groups are silent, single or double */
function splitTo(l, n) {
  const G = []; for (let i = 0; i < l.length;) { if (!isVowelAt(l, i)) { i++; continue; } let j = i; while (j < l.length && isVowelAt(l, j)) j++; G.push([i, j]); i = j; }
  if (!G.length) return null;
  const cost = (g, k, last) => { const [x, y] = G[g], s = l.slice(x, y), rest = l.slice(y);
    if (k === 1) return 0;
    if (k === 0) { if (s === 'e' && last && (rest === '' || rest === 's' || rest === 'd')) return 0.2; if (s === 'e') return 1; if (s === 'ue' && last && rest === '') return 0.4; return 3; }
    if (y - x >= 2) return /^(ia|io|iu|ua|uo|eo|ea|ie|iou|eou|uou|oi|oe|ue|ui|ya|yi|ii|ao|ae|ei|eu|ou|oa|au|ai|ay|ey|oy|ee|oo)/.test(s) ? (/^(ia|io|iu|ua|uo|eo|iou|eou|uou|ya|yi|ii|ao)/.test(s) ? 0.4 : 0.9) : 1.2;
    return 6; };
  /* dp over groups */
  const INF = 1e9, M = G.length, best = Array.from({ length: M + 1 }, () => new Array(n + 1).fill(INF)), from = Array.from({ length: M + 1 }, () => new Array(n + 1).fill(-1));
  best[0][0] = 0;
  for (let g = 0; g < M; g++) for (let c = 0; c <= n; c++) { if (best[g][c] >= INF) continue;
    for (let k = 0; k <= 2; k++) { if (c + k > n) continue; const v = best[g][c] + cost(g, k, g === M - 1); if (v < best[g + 1][c + k]) { best[g + 1][c + k] = v; from[g + 1][c + k] = k; } } }
  if (best[M][n] >= 5) return null;
  const nu = []; let c = n; const ks = [];
  for (let g = M; g > 0; g--) { const k = from[g][c]; ks.unshift(k); c -= k; }
  ks.forEach((k, g) => { const [x, y] = G[g]; if (k === 1) nu.push([x, y]); else if (k === 2) { let cut = x + 1; const s = l.slice(x, y); if (s.length >= 3) { const m = s.search(/[aeiouy](?=[aou])/); cut = x + (m >= 0 ? m + 1 : Math.ceil(s.length / 2)); } nu.push([x, cut]); nu.push([cut, y]); } });
  /* same consonant sharing as the app */
  const DG = ['th', 'sh', 'ch', 'ph', 'wh', 'gh', 'ck', 'ng'], cuts = [];
  for (let k = 0; k + 1 < nu.length; k++) { const e = nu[k][1], s = nu[k + 1][0], run = s - e; let q;
    if (run <= 0) q = s; else if (run === 1) q = e; else { const dg = DG.includes(l.slice(e, e + 2)); q = run === 2 && dg ? e : dg ? e + 2 : e + 1; } cuts.push(q); }
  const parts = []; let p = 0; cuts.forEach(q => { parts.push(l.slice(p, q)); p = q; }); parts.push(l.slice(p));
  return parts.every(s => s.length) ? parts : null;
}

const out = []; let same = 0, cnt = 0, str = 0, miss = 0;
for (const w of [...vocab].sort()) {
  if (w.length < 2 || !cmu.has(w)) { miss++; continue; }
  let pat = cmu.get(w).filter(p => /\d$/.test(p)).map(p => p.slice(-1)).join('');
  if (!pat) continue;
  /* church English keeps some syllables everyday speech drops */
  const lit = rules.SG_LIT[w]; if (lit) { same++; continue; }
  if (rules.CH_EX[w] && rules.CH_EX[w] !== pat.length) { same++; continue; }
  const n = pat.length; if (n === 1) { if (rules.chWordSyl(w).length === 1) { same++; continue; } }
  if (!pat.includes('1')) pat = pat.replace(/[02]/, '1');
  const rp = rules.chWordSyl(w), rpat = rp.length === n ? rules.sgRulePat(w, n) : null;
  if (rpat === pat) { same++; continue; }
  if (rp.length === n) { str++; out.push(w + (n === 1 ? '' : pat)); continue; }
  const parts = splitTo(w, n); if (!parts) { miss++; continue; }
  cnt++; out.push(parts.join('-') + (n === 1 ? '1' : pat));
}
const lex = out.join(' ');
const A = '/*LEX*/', B = '/*END-LEX*/', i0 = html.indexOf(A), i1 = html.indexOf(B);
if (i0 < 0 || i1 < 0) { console.error('LEX markers not found in index.html'); process.exit(1); }
html = html.slice(0, i0 + A.length) + JSON.stringify(lex) + html.slice(i1);
fs.writeFileSync(htmlPath, html);
console.log(`vocabulary ${vocab.size}: rules already right ${same}, accent fixed ${str}, syllables fixed ${cnt}, not in dictionary ${miss}. Stored ${out.length} words, ${(lex.length / 1024).toFixed(0)} KB.`);
