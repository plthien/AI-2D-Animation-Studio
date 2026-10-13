/** Browser-backed frame smoke: seek multiple times; hash PNG bytes, no audio/GPU services. */
import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';

const port=18766;
await mkdir('outputs/p3',{recursive:true});
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
let browser;
try {
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
  const page=await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:'+port+'/deterministic.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__FRAME_READY__||window.__FRAME_ERROR__,null,{timeout:45000});
  const state=await page.evaluate(()=>({ready:window.__FRAME_READY__,error:window.__FRAME_ERROR__}));
  if(!state.ready) throw Error('fixed renderer failed: '+state.error);
  const canvas=page.locator('#app canvas');
  const capture=async(frame)=>{
    await page.evaluate(n=>window.__RENDER_FRAME__(n),frame);
    const png=await canvas.screenshot();
    const hash=createHash('sha256').update(png).digest('hex');
    return {png,hash};
  };
  const a=await capture(0),b=await capture(12),a2=await capture(0),b2=await capture(12);
  if(a.hash!==a2.hash||b.hash!==b2.hash) throw Error('non-deterministic seek');
  if(a.hash===b.hash) throw Error('idle animation showed no frame change');
  await writeFile('outputs/p3/frame_0000.png',a.png);
  await writeFile('outputs/p3/frame_0012.png',b.png);
  const manifest={fps:24,frameHashes:{0:a.hash,12:b.hash},replayStable:true,animation:'idle',runtime:'Spine 4.2.120 PixiJS 8.21.0'};
  await writeFile('outputs/p3/manifest.json',JSON.stringify(manifest,null,2));
  console.log(JSON.stringify(manifest));
} finally {
  if(browser) await browser.close();
  server.kill();
}
