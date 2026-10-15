/* Ison Pitch Lab offline cache. The app is one page, so after one visit with internet it can open
   anywhere, even in airplane mode. Pages are fetched fresh when the connection is good (so updates
   arrive), and from the cache when the network is down or too slow (4 seconds). */
const CACHE='ison-pitch-lab-v1';
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(['./','./index.html']).catch(()=>{})));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
function fromCache(){return caches.match('./index.html').then(m=>m||caches.match('./'))}
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET')return;const u=new URL(r.url);
  const page=r.mode==='navigate'||(u.origin===location.origin&&(u.pathname.endsWith('/')||u.pathname.endsWith('/index.html')));
  if(page){e.respondWith(new Promise(resolve=>{let done=false;
      const t=setTimeout(()=>{fromCache().then(m=>{if(m&&!done){done=true;resolve(m)}})},4000);
      fetch(r).then(res=>{if(res&&res.ok){const cp=res.clone();caches.open(CACHE).then(c=>c.put('./index.html',cp))}if(!done){done=true;clearTimeout(t);resolve(res)}})
        .catch(()=>fromCache().then(m=>{if(!done){done=true;clearTimeout(t);resolve(m||new Response('Offline and not cached yet. Open the app once with internet.',{status:503,headers:{'Content-Type':'text/plain'}}))}}))}));return}
  if(/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)){e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));return res}).catch(()=>new Response('',{status:503}))))}
});
