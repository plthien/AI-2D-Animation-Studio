/** Export the exact P4 contact timeline as PNG and test replay pixel hashes. */
import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const port=18768;
const output='outputs/p4/frames';
await mkdir(output,{recursive:true});
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
async function ready() {
  for(let i=0;i<80;i++){
    if(server.exitCode!==null)throw Error('HTTP server exited');
    try { if((await fetch('http://127.0.0.1:'+port+'/')).ok) return; } catch (_) {}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  throw Error('Local HTTP server not ready');
}
let browser;
try{
  await ready();
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
  const page=await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:'+port+'/contact_scene.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.__CONTACT_READY__||window.__CONTACT_ERROR__,null,{timeout:45000});
  const {ok,error,count}=await page.evaluate(()=>({
    ok:window.__CONTACT_READY__,error:window.__CONTACT_ERROR__,
    count:window.__CONTACT_CLIP__?.frames.length}));
  if(!ok) throw Error('Contact scene failed: '+error);
  const target=page.locator('#app canvas');
  const hashes=[];
  for(let i=0;i<count;i++){
    await page.evaluate(frame=>window.__CONTACT_RENDER_FRAME__(frame),i);
    const image=await target.screenshot();
    const hash=createHash('sha256').update(image).digest('hex');
    hashes.push(hash);
    await writeFile(join(output,'frame_'+String(i).padStart(6,'0')+'.png'),image);
  }
  for(const frame of [0,11,14,25,47]){
    await page.evaluate(n=>window.__CONTACT_RENDER_FRAME__(n),frame);
    const buf=await target.screenshot();
    const hash=createHash('sha256').update(buf).digest('hex');
    if(hash!==hashes[frame])throw Error('Replay mismatch at frame '+frame);
  }
  if(new Set(hashes).size<10) throw Error('Contact scene did not meaningfully animate');
  const summary={frames:count,fps:24,verified:[0,11,14,25,47],
    uniqueFrameImages:new Set(hashes).size,deterministic:true,contactScene:'procedural diagnostic puppet (not Spine IK)'};
  await writeFile('outputs/p4/manifest.json',JSON.stringify(summary,null,2));
  console.log(JSON.stringify(summary));
}finally{
  if(browser)await browser.close();
  server.kill();
}
