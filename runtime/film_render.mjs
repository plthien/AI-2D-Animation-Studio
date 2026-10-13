/** P6 browser frame export: 28 seconds x 24fps, shot boundary and replay hashes. */
import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const port=18771,out='outputs/p6_demo';
await mkdir(out+'/frames',{recursive:true});
await mkdir(out+'/previews',{recursive:true});
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
let browser;
try{
  let ready=false;
  for(let i=0;i<100;i++){
    if(server.exitCode!==null)throw Error('Web server exited early');
    try{if((await fetch('http://127.0.0.1:'+port+'/')).ok){ready=true;break}}catch(_){}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  if(!ready)throw Error('Film fixture server never became available');
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
  const page=await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:'+port+'/film_scene.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__FILM_READY__||window.__FILM_ERROR__,null,{timeout:60000});
  const state=await page.evaluate(()=>({ready:window.__FILM_READY__,error:window.__FILM_ERROR__,
    total:window.__FILM_TIMELINE__?.total_frames}));
  if(!state.ready)throw Error('P6 film scene failed: '+state.error);
  if(state.total!==672)throw Error('Expected 28s at 24 FPS = 672 frames');
  const screenshot=page.locator('#app canvas');
  const sample=new Set([0,95,96,239,240,383,384,527,528,671]);
  const hashByFrame=new Map();
  const shotCounts={};
  for(let n=0;n<state.total;n++){
    const info=await page.evaluate(value=>window.__FILM_DRAW_FRAME__(value),n);
    shotCounts[info.shot]=(shotCounts[info.shot]??0)+1;
    const image=await screenshot.screenshot();
    if(sample.has(n)){
      hashByFrame.set(n,createHash('sha256').update(image).digest('hex'));
      await writeFile(join(out,'previews','frame_'+String(n).padStart(6,'0')+'.png'),image);
    }
    await writeFile(join(out,'frames','frame_'+String(n).padStart(6,'0')+'.png'),image);
  }
  for(const [frame,original] of hashByFrame){
    await page.evaluate(n=>window.__FILM_DRAW_FRAME__(n),frame);
    const image=await screenshot.screenshot();
    if(createHash('sha256').update(image).digest('hex')!==original)
      throw Error('Film replay differed at global frame '+frame);
  }
  if(Object.keys(shotCounts).length!==5||Object.values(shotCounts).reduce((a,b)=>a+b,0)!==672)
    throw Error('P6 shot/frame coverage failed');
  const manifest={fps:24,width:640,height:480,totalFrames:672,shots:shotCounts,
    sampleFrameHashes:Object.fromEntries(hashByFrame),replayStable:true,
    renderedWith:'real Genielabs Spine rig + PixiJS',voiceSource:'separate WAV track'};
  await writeFile(out+'/video_manifest.json',JSON.stringify(manifest,null,2));
  console.log(JSON.stringify({frames:manifest.totalFrames,shots:shotCounts,replayStable:true}));
}finally{if(browser)await browser.close();server.kill()}
