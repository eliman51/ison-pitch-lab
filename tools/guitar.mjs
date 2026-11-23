#!/usr/bin/env node
/* The Guitar lab on the Mac: renders the guitar parts of index.html with the page's own code.

     node tools/guitar.mjs <out folder> [--key -2] [--concert] [--part walk] [--gv 6] [--vv 8] [--stems]
                                       [--strings 5] [--tone 5] [--body 5] [--pluck 5] [--ring 10] [--room 3] [--strum 5] [--human 5] [--lead 5]

   It cuts the block between GT-ENGINE-START and GT-ENGINE-END out of index.html and runs it, so what it writes is
   what the app plays. Needs ffmpeg. Writes one m4a for each part ("Psalm 23 guitar 03 Strum and walk.m4a"), and with
   --stems also the guitar alone (wav) and the list of plucks (json), for measuring. */
import fs from 'node:fs';import path from 'node:path';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
const root=process.env.GT_ROOT||path.dirname(path.dirname(fileURLToPath(import.meta.url))),A=process.argv.slice(2),flag=(n,d)=>{const i=A.indexOf('--'+n);return i<0?d:A[i+1]},has=n=>A.includes('--'+n);
const out=A[0]&&!A[0].startsWith('--')?A[0]:'.',key=+flag('key',0),conc=has('concert'),only=flag('part',null),gv=+flag('gv',6),vv=+flag('vv',8);
const html=fs.readFileSync(process.env.GT_ENGINE||path.join(root,'index.html'),'utf8'),a=html.indexOf('/*GT-ENGINE-START'),b=html.indexOf('/*GT-ENGINE-END*/');if(a<0||b<0)throw new Error('the guitar engine is not in index.html');
const E=new Function(html.slice(a,b)+';return{GT_SR,GT_SONGS,GT_PARTS,GT_BANKS,GT_SND,gtSnd,gtAlign,gtShift,gtSetup,gtLine,gtSheet,gtEvents,gtBank,gtSynth,gtGuitar,gtFx,gtLoud,gtResample,gtMix}')();
const dec=f=>{const r=spawnSync('ffmpeg',['-v','error','-i',f,'-ac','1','-ar',String(E.GT_SR),'-f','f32le','-'],{maxBuffer:1<<30});if(r.status)throw new Error(String(r.stderr));return new Float32Array(r.stdout.buffer,r.stdout.byteOffset,r.stdout.length>>2).slice()};
const wav=(f,y,sr)=>{const n=y.length,buf=Buffer.alloc(44+n*2);buf.write('RIFF',0);buf.writeUInt32LE(36+n*2,4);buf.write('WAVEfmt ',8);buf.writeUInt32LE(16,16);buf.writeUInt16LE(1,20);buf.writeUInt16LE(1,22);buf.writeUInt32LE(sr,24);buf.writeUInt32LE(sr*2,28);buf.writeUInt16LE(2,32);buf.writeUInt16LE(16,34);buf.write('data',36);buf.writeUInt32LE(n*2,40);
  for(let i=0;i<n;i++){const s=Math.max(-1,Math.min(1,y[i]));buf.writeInt16LE(Math.round(s<0?s*32768:s*32767),44+i*2)}fs.writeFileSync(f,buf)};
fs.mkdirSync(out,{recursive:true});
const so={};E.GT_SND.forEach(c=>{const v=flag(c.k,null);if(v!=null)so[c.k]=+v});const snd=E.gtSnd(so),song=E.GT_SONGS.psalm23,sr=E.GT_SR,banks={};
for(const k in E.GT_BANKS)banks[k]=E.gtBank(dec(path.join(root,E.GT_BANKS[k].file)),sr,E.GT_BANKS[k].z);
if(key)console.log('note: on the Mac the singer is not moved to the new key (the app does that); only the guitar is.');
let voice=dec(path.join(root,'psalm23.mp3'));voice=E.gtShift(voice,E.gtAlign(song,voice));let pk=0;for(const s of voice)pk=Math.max(pk,Math.abs(s));for(let i=0;i<voice.length;i++)voice[i]*=.6/pk;
if(conc)voice=E.gtResample(voice,Math.pow(2,song.flat/1200));
const L=E.gtLine(song,conc),G=E.gtSetup(song,key),N=voice.length+Math.round(2.5*sr),Lv=E.gtLoud(voice,sr);
console.log('strings '+snd.strings+' of 10 (0 nylon, 10 steel); capo '+G.capo+', '+G.fam+' shapes: '+Object.values(G.sh).map(s=>s.n+' = '+s.snd).join(', '));
E.GT_PARTS.forEach((P,i)=>{if(only&&P.id!==only)return;const t0=Date.now(),ev=E.gtEvents(song,L,G,P.id,snd),raw=E.gtGuitar(ev,G,banks,N,sr,conc?0:-song.flat/100,snd),g=E.gtFx(raw,sr,snd),Lg=E.gtLoud(g,sr),y=E.gtMix(voice,g,{gv,vv,lv:P.lv,Lv,Lg});
  const nm='Psalm 23 guitar '+String(i+1).padStart(2,'0')+' '+P.name.replace(/^\d+\.\s*/,''),w=path.join(out,nm+'.wav');wav(w,y,sr);
  spawnSync('ffmpeg',['-v','error','-y','-i',w,'-c:a','aac','-b:a','128k',path.join(out,nm+'.m4a')]);fs.unlinkSync(w);
  if(has('stems')){wav(path.join(out,P.id+'.guitar.wav'),raw,sr);wav(path.join(out,P.id+'.guitarfx.wav'),g,sr);fs.writeFileSync(path.join(out,P.id+'.events.json'),JSON.stringify({capo:G.capo,tune:conc?0:-song.flat/100,ev}))}
  console.log(nm+': '+ev.filter(e=>e.k!=='c').length+' plucks, guitar '+(Lg-Lv+(Lv-8+P.lv+(gv-6)*3-Lg)).toFixed(1)+' dB against the voice, made in '+(Date.now()-t0)+' ms')});
