import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { mkdir } from 'node:fs/promises';

const port = 18765;
await mkdir('outputs', {recursive:true});
const server=spawn('python',['-m','http.server',String(port),'--directory','runtime'],{stdio:'ignore'});
let browser;
try {
 browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:640,height:520}});
 await page.goto('http://127.0.0.1:'+port+'/sample.html',{waitUntil:'domcontentloaded',timeout:30000});
 await page.waitForFunction(()=>window.__SPINE_READY__||window.__SPINE_ERROR__,{timeout:40000});
 const outcome=await page.evaluate(()=>({ready:window.__SPINE_READY__,error:window.__SPINE_ERROR__}));
 if (!outcome.ready) throw new Error('Spine sample failed: '+outcome.error);
 await page.locator('#player canvas').first().waitFor({timeout:10000});
 await page.screenshot({path:'outputs/p0_spine_frame.png'});
 console.log('P0 real Spine player image: outputs/p0_spine_frame.png');
} finally {
 if(browser) await browser.close();
 server.kill();
}
