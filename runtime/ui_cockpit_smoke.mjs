/** User-level Chromium smoke with a real local API and built React UI. */
import { chromium } from 'playwright';
import { PNG } from 'pngjs';
import { writeFile, mkdir } from 'node:fs/promises';

const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
try{
 const page=await browser.newPage({viewport:{width:1440,height:920},deviceScaleFactor:1});
 await page.goto('http://127.0.0.1:8000',{waitUntil:'networkidle'});
 await page.getByRole('heading',{name:'Projects',exact:true}).waitFor({timeout:20000});
 await page.getByRole('button',{name:'Create project'}).click();
 await page.getByRole('heading',{name:'Director Studio'}).waitFor();
 await page.getByText('Storyboard',{exact:true}).waitFor();
 await page.getByText('Shot inspector',{exact:true}).waitFor();
 await page.getByRole('button',{name:'Asset Library'}).click();
 await page.getByRole('heading',{name:'Required assets'}).waitFor();
 await page.getByRole('button',{name:'Render & Review'}).click();
 await page.getByRole('heading',{name:'Preflight / Quality gates'}).waitFor();
 const banner=await page.getByText('Cannot render until asset, motion, voice and timeline checks pass.').count();
 if(banner!==1)throw Error('Preflight must prevent missing-asset renders');
 await page.getByRole('button',{name:'Asset Library'}).click();
 await page.getByRole('button',{name:/Prepare demo assets/}).click();
 await page.getByText('Demo assets prepared. Ready for test render.').waitFor({timeout:90000});
 await page.getByRole('button',{name:'Render & Review'}).click();
 await page.getByText('All local readiness checks passed.').waitFor();
 await page.getByRole('button',{name:'Start render'}).click();
 await page.locator('video.preview').waitFor({timeout:480000});
 // Video availability is proved by <video> and a GET from its actual src attribute.
 const videoUrl=await page.locator('video.preview').getAttribute('src');
 if(!videoUrl)throw Error('Missing generated MP4 URL');
 const response=await page.request.get('http://127.0.0.1:8000'+videoUrl);
 if(!response.ok()||(await response.body()).length<12000)throw Error('UI render did not produce a valid MP4');
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
 console.log('UI cockpit browser smoke PASS: create project, storyboard, blocked render, one-click synthetic asset bootstrap, render MP4, screenshot');
} finally {await browser.close()}
