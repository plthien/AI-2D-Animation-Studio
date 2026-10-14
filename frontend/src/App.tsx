import {useEffect,useState} from 'react';
import {Activity,Clapperboard,FolderKanban,Images,Film as FilmIcon,Settings2,Plus,Save,Upload,RefreshCcw,Play,Download,Copy,CheckCircle2,AlertTriangle} from 'lucide-react';
import {api,get,post,put,upload} from './api';
import {GlabsPanel} from './GlabsPanel';
import {RigWorkshop} from './RigWorkshop';
import type {Project,Report,Job,Asset,Film,Catalog} from './api';
type View='projects'|'director'|'assets'|'render'|'settings';
type Doc='film'|'catalog'|'motions';
const views:View[]=['projects','director','assets','render','settings'];
const names=['Projects','Director Studio','Asset Library','Render & Review','Settings'];
const icons=[FolderKanban,Clapperboard,Images,FilmIcon,Settings2];
const endpoint='/studio/projects';
const shown=(v:unknown)=>JSON.stringify(v,null,2);
function Btn({children,click,primary=false,disabled=false}:{children:React.ReactNode;click?:()=>void;primary?:boolean;disabled?:boolean}){
 return <button type="button" className={'btn '+(primary?'primary':'')} onClick={click} disabled={disabled}>{children}</button>;
}
export default function App(){
 const [view,setView]=useState<View>('projects');
 const [projects,setProjects]=useState<Project[]>([]);
 const [pid,setPid]=useState('');
 const [film,setFilm]=useState<Film|null>(null);
 const [catalog,setCatalog]=useState<Catalog|null>(null);
 const [motions,setMotions]=useState<Record<string,unknown>|null>(null);
 const [preflight,setPreflight]=useState<Report|null>(null);
 const [files,setFiles]=useState<Asset[]>([]);
 const [job,setJob]=useState<Job|null>(null);
 const [backend,setBackend]=useState(false);
 const [newName,setNewName]=useState('My Animation');
 const [template,setTemplate]=useState('coffee');
 const [shotIdx,setShotIdx]=useState(0);
 const [doc,setDoc]=useState<Doc>('film');
 const [draft,setDraft]=useState('{}');
 const [dirtyDoc,setDirtyDoc]=useState(false);
 const [brief,setBrief]=useState('A funny five-shot 2D animation with clear cause and effect.');
 const [loading,setLoading]=useState(false);
 const [notice,setNotice]=useState('');
 const [problem,setProblem]=useState('');
 const current=projects.find(p=>p.id===pid);
 const err=(e:unknown)=>{setProblem(e instanceof Error?e.message:String(e));setNotice('')};
 const success=(msg:string)=>{setProblem('');setNotice(msg)};
 const list=async()=>{const response=await get<{projects:Project[]}>(endpoint);setProjects(response.projects)};
 const load=async(id:string)=>{
  const [f,c,m,a,p]=await Promise.all([
   get<Film>(endpoint+'/'+id+'/documents/film'),
   get<Catalog>(endpoint+'/'+id+'/documents/catalog'),
   get<Record<string,unknown>>(endpoint+'/'+id+'/documents/motions'),
   get<{files:Asset[]}>(endpoint+'/'+id+'/assets'),
   get<Report>(endpoint+'/'+id+'/preflight')
  ]);
  setFilm(f);setCatalog(c);setMotions(m);setFiles(a.files);setPreflight(p);
 };
 useEffect(()=>{get<{ok:boolean}>('/health').then(x=>setBackend(x.ok)).catch(()=>setBackend(false));list().catch(err)},[]);
 useEffect(()=>{if(pid)load(pid).catch(err)},[pid]);
 useEffect(()=>{if(!dirtyDoc)setDraft(shown(doc==='film'?film:doc==='catalog'?catalog:motions))},[doc,film,catalog,motions,dirtyDoc]);
 useEffect(()=>{
  if(!job||!['queued','running'].includes(job.status))return;
  const timer=window.setInterval(()=>get<Job>('/studio/jobs/'+job.id).then(setJob).catch(err),2000);
  return ()=>window.clearInterval(timer);
 },[job?.id,job?.status]);
 const work=async(action:()=>Promise<void>)=>{setLoading(true);try{await action()}catch(e){err(e)}finally{setLoading(false)}};
 const create=()=>work(async()=>{
  const item=await post<Project>(endpoint,{name:newName,template});
  await list();setPid(item.id);setView('director');success('Project created. Add required media before render.');
 });
 const save=(kind:Doc,value:unknown)=>work(async()=>{
  await put(endpoint+'/'+pid+'/documents/'+kind,value);setDirtyDoc(false);await load(pid);success(kind+' saved and validated.');
 });
 const selectProject=(id:string)=>{setPid(id);setShotIdx(0);setView('director');setJob(null);setDirtyDoc(false)};
 const uploadPath=(path:string,file:File)=>work(async()=>{
  const parts=path.split('/');
  const url=parts[0]==='rigs'?endpoint+'/'+pid+'/rigs/'+parts[1]+'/'+parts[2]:endpoint+'/'+pid+'/assets/'+parts[0]+'/'+parts[1];
  await upload(url,file);await load(pid);success('Uploaded '+path);
 });
 const refresh=()=>work(async()=>{await load(pid);success('Preflight updated.')});
 const render=()=>work(async()=>{
  const result=await api<Job>(endpoint+'/'+pid+'/render',{method:'POST'});
  setJob(result);success('Render queued locally. No image generation or TTS charged.');
 });
 const updateShot=(field:string,value:unknown)=>{
  if(!film)return;
  const shots=film.shots.map((s,i)=>i===shotIdx?{...s,[field]:value}:s);
  setFilm({...film,shots});
 };
 const exportPrompt=()=>work(async()=>{
  const prompt='Create film.v2 and matching per-shot MotionPlan JSON; every motion must have exact shot duration (24 fps). Use ONLY rig IDs, backgrounds, props from catalog. Keep prop and wrist continuity; no automatic API calls. Story: '+brief+'\nCATALOG:\n'+shown(catalog)+'\nCURRENT FILM:\n'+shown(film)+'\nMOTIONS:\n'+shown(motions);
  await navigator.clipboard.writeText(prompt);success('Director prompt copied for manual ChatGPT/DeepSeek authoring.');
 });
 const selected=film?.shots[shotIdx];
 const stageFlags=[Boolean(film&&catalog&&motions),Boolean(catalog&&Object.keys(catalog.rigs).length&&files.some(f=>f.path.startsWith('rigs/'))),Boolean(catalog&&Object.values(catalog.backgrounds).every(a=>files.some(f=>f.path===a.image))),Boolean(motions&&Object.keys(motions).length>0),Boolean(film&&film.shots.every(s=>!s.narration||files.some(f=>f.path==='voices/'+s.narration?.wav))),Boolean(preflight?.ready)];
 const missing=preflight?.missing_assets??[];
 const running=job?.status==='queued'||job?.status==='running';
 const primary=preflight?.ready===true;
 const itemCount=film?.shots.reduce((a,s)=>a+s.duration_frames,0)??0;
 return <div className="layout">
  <aside className="sidebar">
   <div className="logo"><span className="logoicon"><Clapperboard/></span><div><div className="brand">AI 2D Animation Studio</div><div className="eyebrow">Creative Cockpit</div></div></div>
   <div className="eyebrow" style={{marginTop:24}}>Workspace</div>
   <nav className="menu">{views.map((v,i)=>{const Icon=icons[i];return <button key={v} className={'navbutton '+(view===v?'active':'')} onClick={()=>setView(v)}>
    <Icon size={19}/><span>{names[i]}</span></button>})}</nav>
   <div className="sidebarfoot"><div className="eyebrow">Selected project</div><p className="small">{current?.name??'None'}</p><span className={'pill '+(backend?'ok':'bad')}>{backend?'Backend online':'Backend offline'}</span><p className="tiny muted">Local-first workflow · manual AI handoff · external billing never automatic</p></div>
  </aside>
  <main className="main">
   <header className="pagehead"><div><div className="eyebrow">AI Animation / {view}</div><h1>{names[views.indexOf(view)]}</h1><p className="muted small">{current?current.name:'Select or create a local project'}</p></div><span className={'pill '+(primary?'ok':'warn')}>{!pid?'No project':primary?'Preflight ready':'Preflight required'}</span></header>
   {problem&&<div className="alert" role="alert"><AlertTriangle size={15}/> {problem}</div>}
   {notice&&<div className="alert ok" role="status"><CheckCircle2 size={15}/> {notice}</div>}
   {view==='projects'&&<div className="stack">
    <section className="panel"><h2>Create a project</h2><div className="fields">
     <label className="field">Name<input value={newName} onChange={e=>setNewName(e.target.value)} /></label>
     <label className="field">Starter FilmPlan<select value={template} onChange={e=>setTemplate(e.target.value)}><option value="coffee">Coffee Cup Save</option><option value="lost_key">The Lost Key</option></select></label>
    </div><div className="row" style={{marginTop:16}}><Btn primary disabled={loading||newName.trim().length<2} click={create}><Plus size={15}/> Create project</Btn><span className="muted small">JSON template only · import actual rig/images/WAV from Assets</span></div></section>
    <section className="panel"><h2>Projects on this computer</h2><div className="list">{projects.map(p=><button key={p.id} className="item spread" onClick={()=>selectProject(p.id)} style={{color:'inherit',textAlign:'left'}}><span><b>{p.name}</b><p className="tiny muted">{p.template} · {p.created_at.slice(0,10)}</p></span><Activity size={17}/></button>)}{projects.length===0&&<p className="muted">No projects yet.</p>}</div></section>
   </div>}
   {view==='director'&&pid&&film&&catalog&&<div className="stack">
    <div className="steps">{['Director','Rig','Background','Motion','Voice','Render'].map((step,i)=><button type="button" key={step} onClick={()=>setView(i===5?'render':i===0?'director':'assets')} className={'step '+(stageFlags[i]?'active':'')}><b>{i+1} · {step} {stageFlags[i]?'✓':'·'}</b><span>{i===0?'Story and shots':i===1?'Spine character':i===2?'Artwork PNG':i===3?'MotionPlan':i===4?'WAV input':'MP4 output'}</span></button>)}</div>
    <div className="dashboard"><div className="metric"><div className="eyebrow">Shots</div><b>{film.shots.length}</b></div><div className="metric"><div className="eyebrow">Duration</div><b>{(itemCount/24).toFixed(1)}s</b></div><div className="metric"><div className="eyebrow">Resolution</div><b>{film.width}×{film.height}</b></div></div>
    <section className="panel"><div className="spread"><h2>Storyboard</h2><span className="pill">Select shot to edit</span></div><div className="shotgrid">{film.shots.map((s,i)=>{
     const image=catalog.backgrounds[s.background_id]?.image;const ready=files.some(x=>x.path===image);
     return <button key={s.shot_id} className={'shot '+(shotIdx===i?'active':'')} onClick={()=>setShotIdx(i)}>
      <div className="shotvisual">{image&&ready?<img alt={s.background_id} style={{width:'100%',height:'100%',objectFit:'cover'}} src={endpoint+'/'+pid+'/media/'+image}/>:<Images size={23}/>}</div>
      <b className="small">{i+1}. {s.shot_id}</b><p className="tiny muted">{(s.duration_frames/24).toFixed(2)}s · {s.background_id}</p>
      <p className="tiny muted">{s.narration?.text.slice(0,60)||'No narration'}</p></button>
    })}</div></section>
    {selected&&<section className="panel"><div className="spread"><h2>Shot inspector</h2><Btn primary disabled={loading} click={()=>void save('film',film)}><Save size={14}/> Save shot changes</Btn></div>
     <div className="fields">
      <label className="field">Shot ID<input value={selected.shot_id} onChange={e=>updateShot('shot_id',e.target.value)}/></label>
      <label className="field">Duration in frames<input type="number" min="1" value={selected.duration_frames} onChange={e=>updateShot('duration_frames',Number(e.target.value))}/></label>
      <label className="field">Background<select value={selected.background_id} onChange={e=>updateShot('background_id',e.target.value)}>{Object.keys(catalog.backgrounds).map(name=><option key={name}>{name}</option>)}</select></label>
      <label className="field">Camera zoom<input type="number" step=".05" min=".75" max="2" value={selected.camera.zoom} onChange={e=>updateShot('camera',{...selected.camera,zoom:Number(e.target.value)})}/></label>
      <label className="field">Camera pan X<input type="number" value={selected.camera.pan_x} onChange={e=>updateShot('camera',{...selected.camera,pan_x:Number(e.target.value)})}/></label>
      <label className="field">Camera pan Y<input type="number" value={selected.camera.pan_y} onChange={e=>updateShot('camera',{...selected.camera,pan_y:Number(e.target.value)})}/></label>
     </div>
     <label className="field" style={{marginTop:14}}>Narration text<textarea rows={3} value={selected.narration?.text??''} onChange={e=>updateShot('narration',{...selected.narration,wav:selected.narration?.wav??'shot_01.wav',start_frame:selected.narration?.start_frame??0,text:e.target.value})}/></label>
     <p className="muted small">Motion: {selected.actors.map(a=>a.actor_id+' / '+a.rig_id+' / '+a.motion_id).join(', ')}</p>
    </section>}
    <section className="panel"><h2>Manual ChatGPT / DeepSeek handoff</h2><label className="field">Creative brief<textarea rows={2} value={brief} onChange={e=>setBrief(e.target.value)}/></label><div className="row" style={{marginTop:12}}><Btn click={exportPrompt}><Copy size={14}/> Copy Director prompt</Btn><span className="small muted">Import returned film, catalog and motions JSON below; no LLM API used.</span></div></section>
    <section className="panel"><div className="spread"><h2>JSON editor / Import</h2><div className="row">{(['film','catalog','motions'] as Doc[]).map(k=><button key={k} className={'btn '+(doc===k?'primary':'ghost')} onClick={()=>{if(dirtyDoc&&!window.confirm('Discard unsaved JSON changes?'))return;setDirtyDoc(false);setDoc(k);setDraft(shown(k==='film'?film:k==='catalog'?catalog:motions))}}>{k}</button>)}</div></div>
     <textarea aria-label="Director JSON" spellCheck={false} className="code" value={draft} onChange={e=>{setDraft(e.target.value);setDirtyDoc(true)}}/>
     <div className="row" style={{marginTop:12}}><Btn primary disabled={loading} click={()=>{try{void save(doc,JSON.parse(draft))}catch(e){err(e)}}}><Save size={14}/> Validate and save {dirtyDoc?'* ':''}</Btn><Btn click={()=>void work(async()=>{if(dirtyDoc&&!window.confirm('Discard unsaved JSON changes?'))return;setDirtyDoc(false);await load(pid);success('Reloaded source files.')})}><RefreshCcw size={14}/> Reload</Btn></div></section>
   </div>}
   {view==='assets'&&pid&&<div className="stack">
    <section className="panel"><div className="spread"><h2>Required assets</h2><Btn click={()=>void work(async()=>{await load(pid);success('Assets checked.')})}><RefreshCcw size={14}/> Recheck</Btn></div>
     <p className="muted text">Import file đúng tên theo Asset Catalog. Background phải trùng độ phân giải của film. Rig cần 4 file Spine. WAV phải mono PCM16 24kHz.</p>
     <div className="pills"><span className={'pill '+(primary?'ok':'warn')}>{primary?'Ready':'Missing '+missing.length}</span><span className="pill">{files.length} uploaded</span></div>
     <div className="row" style={{marginTop:14}}>
     <Btn disabled={loading} click={()=>void work(async()=>{
      const result=await api<{preflight:Report}>(endpoint+'/'+pid+'/bootstrap-demo',{method:'POST'});
      await load(pid);success(result.preflight.ready?'Demo assets prepared. Ready for test render.':'Synthetic assets prepared; inspect preflight warnings.');
     })}><Play size={14}/> Prepare demo assets (offline)</Btn>
     <span className="small muted">Uses local pinned rigging scripts, fixture art and tone WAV; overwrites demo-named assets in this project.</span>
    </div>
     <div className="list" style={{marginTop:14}}>{missing.map(path=><div key={path} className="item spread"><span className="small">{path}</span><label className="btn"><Upload size={14}/> Import<input type="file" style={{display:'none'}} aria-label={'Upload '+path} accept={path.endsWith('.png')?'.png,.jpg,.jpeg,.webp':path.endsWith('.wav')?'.wav':undefined} onChange={e=>{const f=e.target.files?.[0];if(f)void uploadPath(path,f);e.target.value=''}}/></label></div>)}{!missing.length&&<p className="muted small">No missing files found.</p>}</div>
     {preflight?.errors.map((s,i)=><div key={i} className="alert">{s}</div>)}
    </section>
    <section className="panel"><h2>Media library</h2><div className="imagegrid">{files.map(a=><div key={a.path} className="imagecard">{(a.path.startsWith('backgrounds/')||a.path.startsWith('props/'))&&<img alt={a.path} src={endpoint+'/'+pid+'/media/'+a.path}/>}<span>{a.path}</span><div className="tiny muted">{(a.bytes/1024).toFixed(1)} KB</div></div>)}</div></section>
    {catalog&&<GlabsPanel projectId={pid} catalog={catalog} onImported={()=>load(pid)}/>} 
    {catalog&&<RigWorkshop projectId={pid} catalog={catalog} onBuilt={()=>load(pid)}/>} 
   </div>}
   {view==='render'&&pid&&<div className="stack">
    <section className="panel"><div className="spread"><h2>Preflight / Quality gates</h2><Btn click={refresh}><RefreshCcw size={14}/> Recheck</Btn></div>
     <div className="dashboard"><div className="metric"><div className="eyebrow">Frames</div><b>{preflight?.frames??'—'}</b></div><div className="metric"><div className="eyebrow">Shots</div><b>{preflight?.shots??'—'}</b></div><div className="metric"><div className="eyebrow">Missing files</div><b>{missing.length}</b></div></div>
     <div className={'alert '+(primary?'ok':'')} style={{marginTop:15}}>{primary?'All local readiness checks passed.':'Cannot render until asset, motion, voice and timeline checks pass.'}</div>
     {preflight?.errors.map((s,i)=><div className="alert" key={i}>{s}</div>)}
     {missing.map(s=><p className="warning small" key={s}>Missing: {s}</p>)}
     {preflight?.warnings.map((s,i)=><p className="warning small" key={i}>{s}</p>)}
    </section>
    <section className="panel"><div className="spread"><h2>Render movie</h2><span className="pill">{job?.status??'Idle'}</span></div>
     <p className="muted text">Uses local Spine/PixiJS + FFmpeg. One project render at a time. No model, G-Labs or Kokoro call is triggered.</p>
     <Btn primary disabled={loading||!primary||running} click={render}><Play size={15}/> Start render</Btn>
     {job&&<div className="item" style={{marginTop:14}}><div className="spread"><b>Job {job.id.slice(0,8)}</b><span>{job.status} {job.rendered_frames!==undefined?' · '+job.rendered_frames+' frames':''}</span></div>{job.error&&<pre>{job.error}</pre>}{job.log&&<details><summary className="muted small">Renderer log</summary><pre>{job.log}</pre></details>}</div>}
    </section>
    {job?.status==='completed'&&<section className="panel"><h2>Video review</h2><video className="preview" controls src={endpoint+'/'+pid+'/video'}/><p><a className="btn primary" href={endpoint+'/'+pid+'/video'} download><Download size={15}/> Download MP4</a></p></section>}
   </div>}
   {view==='settings'&&<section className="panel"><h2>Local pipeline status</h2>
    <div className="list"><div className="item spread">API backend <span className={'pill '+(backend?'ok':'bad')}>{backend?'Connected':'Offline'}</span></div>
    <div className="item spread">Manual AI Director <span className="pill ok">Ready</span></div>
    <div className="item spread">G-Labs generation <span className="pill warn">Live not tested</span></div>
    <div className="item spread">Local Kokoro <span className="pill warn">Not integrated</span></div>
    <div className="item spread">Spine/PixiJS + FFmpeg <span className="pill">Requires Node / Chromium / FFmpeg</span></div></div>
    <p className="text muted">Build frontend: cd frontend &amp;&amp; npm install &amp;&amp; npm run build. Start backend: python -m studio. Open http://127.0.0.1:8000.</p>
    <p className="small warning">This is a local workspace, not a production multi-user internet-facing service.</p>
   </section>}
   {view!=='projects'&&!pid&&<section className="panel"><h2>No project selected</h2><Btn click={()=>setView('projects')}>Open Projects</Btn></section>}
   <footer>AI 2D Animation Studio · Local-first · Cockpit layout inspired by your ytb-ai-studio · Synthetic CI rigs are not production artwork</footer>
  </main>
 </div>;
}
