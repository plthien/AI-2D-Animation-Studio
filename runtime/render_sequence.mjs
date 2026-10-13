/** Export a sequential PNG frame run (no wall-clock ticks), replay-check at end. */
import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { mkdir, writeFile } from 'node:fs/promises';
import { spawn } from 'node:child_process';
import { resolve, join } from 'node:path';

const frames=Number(process.argv[2]??24);
const output=resolve(process.argv[3]??'outputs/p3/sequence');
if(!Number.isSafeInteger(frames)||frames<1||frames>2400) throw Error('Frame count must be integer in [1,2400]');
await mkdir(output,{recursive:true});
const port=18767;
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
async function waitForLocalServer() {
  const url='http://127.0.0.1:'+port+'/';
  for(let attempt=0;attempt<80;attempt++) {
    if(server.exitCode!==null) throw Error('Fixture server exited: '+server.exitCode);
    try {
      const response=await fetch(url);
      if(response.ok) return;
    }catch (_) { /* Still booting. */ }
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  throw Error('Fixture HTTP server not ready after 8 seconds');
}

let browser;
try {
  await waitForLocalServer();
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
  const page=await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:'+port+'/deterministic.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__FRAME_READY__||window.__FRAME_ERROR__,null,{timeout:45000});
  const status=await page.evaluate(()=>({ready:window.__FRAME_READY__,error:window.__FRAME_ERROR__}));
  if(!status.ready) throw Error('Spine initialization failed: '+status.error);
  const canvas=page.locator('#app canvas');
  const hashes=[];
  for(let i=0;i<frames;i++){
    await page.evaluate(n=>window.__RENDER_FRAME__(n),i);
    const image=await canvas.screenshot();
    const hash=createHash('sha256').update(image).digest('hex');
    hashes.push(hash);
    await writeFile(join(output,'frame_'+String(i).padStart(6,'0')+'.png'),image);
  }
  for(const i of [0,Math.floor((frames-1)/2),frames-1]){
    await page.evaluate(n=>window.__RENDER_FRAME__(n),i);
    const image=await canvas.screenshot();
    if(createHash('sha256').update(image).digest('hex')!==hashes[i]){
      throw Error('Nonrepeatable pixel output at frame '+i);
    }
  }
  const result={frames,fps:24,width:640,height:480,animation:'idle',
    firstHash:hashes[0],lastHash:hashes[hashes.length-1],replayStable:true};
  await writeFile(join(output,'manifest.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result));
}finally{
  if(browser)await browser.close();
  server.kill();
}
