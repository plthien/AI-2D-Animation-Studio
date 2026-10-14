/** User-level Chromium smoke with a real local API and built React UI. */
import { chromium } from 'playwright';
import { PNG } from 'pngjs';
import { writeFile, mkdir } from 'node:fs/promises';

const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:920},deviceScaleFactor:1});
 await page.goto('http://127.0.0.1:8000',{waitUntil:'networkidle'});
 await page.getByRole('heading',{name:'Projects'}).waitFor({timeout:20000});
 await page.getByRole('button',{name:'Create project'}).click();
 await page.getByRole('heading',{name:'Director Studio'}).waitFor();
 await page.getByText('Storyboard',{exact:true}).waitFor();
 await page.getByText('Shot inspector',{exact:true}).waitFor();
 await page.getByRole('button',{name:'Asset Library'}).click();
 await page.getByRole('heading',{name:'Required assets'}).waitFor();
 await page.getByText('Missing: ',{exact:false}).count();
 await page.getByRole('button',{name:'Render & Review'}).click();
 await page.getByRole('heading',{name:'Preflight / Quality gates'}).waitFor();
 const banner=await page.getByText('Cannot render until asset, motion, voice and timeline checks pass.').count();
 if(banner!==1)throw Error('Preflight must prevent missing-asset renders');
 const data=await page.screenshot({fullPage:true});
 const png=PNG.sync.read(data);
 let nonDark=0;
 for(let i=0;i<png.data.length;i+=4){
   const [r,g,b]=png.data.subarray(i,i+3);
   if(r>60||g>70||b>85)nonDark++;
 }
 if(nonDark/png.width/png.height<.03)throw Error('Cockpit screenshot appears blank');
 await mkdir('outputs/ui',{recursive:true});
 await writeFile('outputs/ui/cockpit.png',data);
 console.log('UI cockpit browser smoke PASS: create project, edit/storyboard, assets, blocked render, nonblank screenshot');
} finally {await browser.close()}
