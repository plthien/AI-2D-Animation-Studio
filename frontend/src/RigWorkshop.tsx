import {useEffect,useState} from 'react';
import {Layers3,Save,Wrench} from 'lucide-react';
import {get,post,upload,type Catalog} from './api';
type Inspect={rig_id:string;has_atlas:boolean;has_reference:boolean;parts:string[];layout:unknown;semantic:Record<string,string>|null;anchors:Record<string,{x:number;y:number}>|null;built:boolean};
export function RigWorkshop({projectId,catalog,onBuilt}:{projectId:string;catalog:Catalog;onBuilt:()=>Promise<void>}){
 const ids=Object.keys(catalog.rigs);
 const [rig,setRig]=useState(ids[0]??'baseline');
 const [info,setInfo]=useState<Inspect|null>(null);
 const [semantic,setSemantic]=useState('{}');
 const [anchors,setAnchors]=useState('{}');
 const [busy,setBusy]=useState(false);
 const [status,setStatus]=useState('');
 const [error,setError]=useState('');
 const root='/studio/projects/'+projectId+'/rigging/'+rig;
 const reload=async()=>{
  const data=await get<Inspect>(root+'/inspect');setInfo(data);
  if(data.semantic)setSemantic(JSON.stringify(data.semantic,null,2));
  else if(data.parts.length)setSemantic(JSON.stringify(Object.fromEntries(data.parts.map(x=>[x.replace(/\.png$/,''),''])),null,2));
  if(data.anchors)setAnchors(JSON.stringify(data.anchors,null,2));
 };
 useEffect(()=>{reload().catch(e=>setError(String(e)))},[projectId,rig]);
 const run=async(label:string,task:()=>Promise<unknown>)=>{
  setBusy(true);setError('');setStatus('');
  try{await task();await reload();setStatus(label+' completed. Review the results.')}
  catch(e){setError(e instanceof Error?e.message:String(e))}
  finally{setBusy(false)}
 };
 const file=(name:string,value:File)=>run('Uploaded '+name,()=>upload(root+'/source/'+name,value));
 const stage=(step:string)=>run(step,async()=>{
  await post(root+'/stage/'+step,{});
  if(step==='build')await onBuilt();
 });
 const save=()=>run('Approved mapping',()=>post(root+'/configuration',{semantic:JSON.parse(semantic),anchors:JSON.parse(anchors)}));
 return <section className="panel">
  <div className="spread"><h2>Character Rig Workshop</h2><span className="pill warn">Manual pivot approval</span></div>
  <p className="muted text">Upload a separated-parts character atlas and reference pose. Genielabs segments/positions the parts. Review every part, semantic label and joint pivot before building a Spine rig. This step does not call an AI model.</p>
  <label className="field">Rig ID<select value={rig} onChange={e=>setRig(e.target.value)}>{ids.map(x=><option key={x}>{x}</option>)}</select></label>
  <div className="fields" style={{marginTop:12}}>{(['atlas.png','reference.png'] as const).map(name=><label key={name} className="item" style={{cursor:'pointer'}}>
   <b className="small">{name}</b><p className="tiny muted">Upload PNG, JPEG or WebP · {(name==='atlas.png'?info?.has_atlas:info?.has_reference)?'Ready':'Missing'}</p>
   <input type="file" accept=".png,.jpg,.jpeg,.webp" style={{display:'none'}} onChange={e=>{const selected=e.target.files?.[0];if(selected)void file(name,selected);e.target.value=''}}/>
  </label>)}</div>
  <div className="row" style={{marginTop:13}}>
   <button className="btn" disabled={busy||!info?.has_atlas||!info.has_reference} onClick={()=>void stage('segment')}><Layers3 size={14}/> 1. Segment</button>
   <button className="btn" disabled={busy||!info?.parts.length} onClick={()=>void stage('position')}>2. Position parts</button>
   <button className="btn primary" disabled={busy||!info?.layout} onClick={()=>void stage('build')}><Wrench size={14}/> 3. Build rig</button>
  </div>
  {info?.parts.length?<div className="imagegrid" style={{marginTop:15}}>{info.parts.map(name=><div className="imagecard" key={name}>
   <img src={root+'/part/'+name} alt={name}/><span>{name}</span></div>)}</div>:null}
  {info?.layout?<>
   <details style={{marginTop:12}}><summary className="small muted">Inspect positioned layout</summary><pre>{JSON.stringify(info.layout,null,2)}</pre></details>
   <div className="fields" style={{marginTop:12}}>
    <label className="field">Part stem to semantic label JSON<textarea className="code" style={{minHeight:215}} value={semantic} onChange={e=>setSemantic(e.target.value)} spellCheck={false}/></label>
    <label className="field">Approved joint anchors JSON (x,y)<textarea className="code" style={{minHeight:215}} value={anchors} onChange={e=>setAnchors(e.target.value)} spellCheck={false}/></label>
   </div>
   <p className="small muted">Labels include torso, head, left_upper_arm, left_forearm and left_hand. Anchors are exact reference-image pixel coordinates. Currently only a neutral +X straight setup arm is supported.</p>
   <button className="btn" disabled={busy} onClick={()=>void save()}><Save size={14}/> Save approved mapping</button>
  </>:null}
  {info?.built&&<div className="alert ok">Spine rig output exists. Motion arm lengths and shoulder must match its rig_profile.json.</div>}
  {status&&<div className="alert ok">{status}</div>}
  {error&&<div role="alert" className="alert">{error}</div>}
 </section>;
}
