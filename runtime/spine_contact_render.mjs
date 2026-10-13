/** GitHub CI: real Spine rig, IK wrist/prop numerical proof and browser PNG+MP4 */
import { chromium } from 'playwright';
import { createHash } from 'node:crypto';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const port=18769;
const out='outputs/p4_spine_video';
await mkdir(out+'/frames',{recursive:true});
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
async function ready(){
  for(let i=0;i<80;i++){
    if(server.exitCode!==null)throw Error('HTTP server exited');
    try{if((await fetch('http://127.0.0.1:'+port+'/')).ok)return;}catch(_){}
    await new Promise(resolve=>setTimeout(resolve,100));
  }
  throw Error('Fixture server not ready');
}
let browser;
try{
  await ready();
  browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
  const page=await browser.newPage({viewport:{width:640,height:480},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:'+port+'/spine_contact_scene.html',{waitUntil:'domcontentloaded',timeout:30000});
  await page.waitForFunction(()=>window.__CONTACT_SPINE_READY__||window.__CONTACT_SPINE_ERROR__,null,{timeout:45000});
  const state=await page.evaluate(()=>({ready:window.__CONTACT_SPINE_READY__,error:window.__CONTACT_SPINE_ERROR__}));
  if(!state.ready)throw Error('Spine rig contact adapter failed: '+state.error);
  const canvas=page.locator('#app canvas');
  const hashes=[];
  let maxWristError=0;
  const wristPositions=[];
  for(let i=0;i<48;i++){
    const info=await page.evaluate(f=>window.__SPINE_CONTACT_FRAME__(f),i);
    maxWristError=Math.max(maxWristError,info.wristErr);
    wristPositions.push(info.actualWrist);
    const png=await canvas.screenshot();
    hashes.push(createHash('sha256').update(png).digest('hex'));
    await writeFile(join(out,'frames','frame_'+String(i).padStart(6,'0')+'.png'),png);
  }
  if(maxWristError>0.1)throw Error('Unacceptable Spine wrist IK error '+maxWristError);
  if(new Set(hashes).size<15)throw Error('Spine arm motion failed to produce moving images');
  for(const i of [0,11,14,27,47]){
    await page.evaluate(n=>window.__SPINE_CONTACT_FRAME__(n),i);
    const png=await canvas.screenshot();
    if(createHash('sha256').update(png).digest('hex')!==hashes[i])throw Error('Spine replay mismatch at '+i);
  }
  const manifest={frames:48,fps:24,rigSource:'Genielabs build_spine_json.py + make_atlas.py',
    boneChain:['left-upper-arm','left-lower-arm','left-hand'],maxWristError,
    uniqueFrameImages:new Set(hashes).size,deterministic:true,
    restatedLimitations:'5 synthetic parts, no full humanoid, no automatic rigging from AI image'};
  await writeFile(out+'/manifest.json',JSON.stringify(manifest,null,2));
  console.log(JSON.stringify(manifest));
}finally{
  if(browser)await browser.close();
  server.kill();
}
