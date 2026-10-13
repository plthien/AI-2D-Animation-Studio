import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { PNG } from 'pngjs';

const port = 18765;
await mkdir('outputs', {recursive:true});
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
 browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:640,height:520}});
 await page.goto('http://127.0.0.1:'+port+'/sample.html',{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForFunction(()=>window.__SPINE_READY__||window.__SPINE_ERROR__,{timeout:40000});
 const outcome=await page.evaluate(()=>({ready:window.__SPINE_READY__,error:window.__SPINE_ERROR__}));
 if (!outcome.ready) throw new Error('Spine sample failed: '+outcome.error);
 await page.locator('#player canvas').first().waitFor({timeout:10000});
 // Spine Player fires ready before the first fully painted browser frame.
 // Inspect real screenshot pixels rather than treating an empty canvas as PASS.
 let fraction=0;
 for(let attempt=0;attempt<50;attempt++){
   const screenshot=await page.screenshot();
   await writeFile('outputs/p0_spine_frame.png',screenshot);
   const image=PNG.sync.read(screenshot);
   const sampleX=Math.min(2,image.width-1), sampleY=Math.min(2,image.height-1);
   const origin=(image.width*sampleY+sampleX)*4;
   const bg=[image.data[origin],image.data[origin+1],image.data[origin+2]];
   let changed=0,total=0;
   for(let y=0;y<Math.min(image.height,480);y+=3){
     for(let x=0;x<Math.min(image.width,640);x+=3){
       const k=(y*image.width+x)*4;
       const diff=Math.abs(image.data[k]-bg[0])+Math.abs(image.data[k+1]-bg[1])+Math.abs(image.data[k+2]-bg[2]);
       if(diff>70) changed++;
       total++;
     }
   }
   fraction=changed/total;
   if(fraction>=0.004) break;
   await page.waitForTimeout(300);
 }
 if(fraction<0.004) throw new Error('Spine Player stayed blank after 15 seconds of frame polling');
 console.log('P0 real Spine player image (foreground='+fraction.toFixed(3)+'): outputs/p0_spine_frame.png');
} finally {
 if(browser) await browser.close();
 server.kill();
}
