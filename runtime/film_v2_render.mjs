/** Browser-backed frame exporter: independent clips, 5 shots, reproducible seeks. */
import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const port=18773,out='outputs/p6_v2';
await mkdir(out+'/frames',{recursive:true});
await mkdir(out+'/previews',{recursive:true});
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
let browser;
try {
  let ready=false;
  for(let attempt=0;attempt<100;attempt++){
    if(server.exitCode!==null)throw Error('Fixture HTTP server exited');
    try {if((await fetch('http://127.0.0.1:'+port+'/')).ok){ready=true;break;}}catch(_){}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  if(!ready)throw Error('Renderer fixture server did not start');
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
  const page=await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:'+port+'/film_v2_scene.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__FILM_V2_READY__||window.__FILM_V2_ERROR__,null,{timeout:60000});
  const state=await page.evaluate(()=>({ready:window.__FILM_V2_READY__,error:window.__FILM_V2_ERROR__,
    timeline:window.__FILM_V2_TIMELINE__}));
  if(!state.ready)throw Error('Film v2 failed to initialize: '+state.error);
  const timeline=state.timeline;
  if(timeline.total_frames!==672 || timeline.shots.length!==5)
    throw Error('P6 V2 acceptance requires 5 shots / 672 frames');
  const counts={},motions=new Set(),rigIds=new Set(),backgrounds=new Set();
  const previewIndices=new Set(timeline.shots.flatMap(s=>[s.start,s.end_exclusive-1]));
  const hashes=new Map();
  const canvas=page.locator('#app canvas');
  for(let i=0;i<timeline.total_frames;i++){
    const info=await page.evaluate(frame=>window.__FILM_V2_DRAW__(frame),i);
    counts[info.shot]=(counts[info.shot]??0)+1;
    backgrounds.add(info.background);
    for(const id of info.motionIds)motions.add(id);
    for(const id of info.rigIds)rigIds.add(id);
    const png=await canvas.screenshot();
    if(previewIndices.has(i)){
      hashes.set(i,createHash('sha256').update(png).digest('hex'));
      await writeFile(join(out,'previews','frame_'+String(i).padStart(6,'0')+'.png'),png);
    }
    await writeFile(join(out,'frames','frame_'+String(i).padStart(6,'0')+'.png'),png);
  }
  for(const [i,hash] of hashes){
    await page.evaluate(n=>window.__FILM_V2_DRAW__(n),i);
    const png=await canvas.screenshot();
    if(createHash('sha256').update(png).digest('hex')!==hash)
      throw Error('V2 frame is not replay-stable: '+i);
  }
  if(Object.keys(counts).length!==5 || motions.size<5 || rigIds.size<2 || backgrounds.size<2)
    throw Error('V2 still resembles a single-clip/single-asset demo');
  const report={fps:24,totalFrames:timeline.total_frames,duration:timeline.total_frames/24,
    shots:counts,independentMotions:[...motions],rigs:[...rigIds],backgrounds:[...backgrounds],
    replayStable:true,frameHashes:Object.fromEntries(hashes)};
  await writeFile(out+'/video_manifest.json',JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{if(browser)await browser.close();server.kill();}
