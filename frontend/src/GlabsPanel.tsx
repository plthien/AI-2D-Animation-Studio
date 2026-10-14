import {useEffect,useState} from 'react';
import {ImagePlus,RefreshCcw} from 'lucide-react';
import {get,post,type Catalog} from './api';

type Provider={configured:boolean;reachable:boolean;message?:string};
type Task={task_id:string;asset_path:string;status:string;error?:string};
export function GlabsPanel({projectId,catalog,onImported}:{projectId:string;catalog:Catalog;onImported:()=>Promise<void>}){
 const [provider,setProvider]=useState<Provider|null>(null);
 const [assetPath,setAssetPath]=useState('');
 const [prompt,setPrompt]=useState('Clean hand-drawn flat 2D cartoon background, same art style and landmarks, no text, no watermark.');
 const [model,setModel]=useState('nano_banana_2');
 const [ratio,setRatio]=useState('16:9');
 const [task,setTask]=useState<Task|null>(null);
 const [error,setError]=useState('');
 const [busy,setBusy]=useState(false);
 const options=[...Object.values(catalog.backgrounds).map(x=>x.image),...Object.values(catalog.props).map(x=>x.image)];
 useEffect(()=>{get<Provider>('/studio/provider/glabs').then(setProvider).catch(()=>setProvider({configured:false,reachable:false}))},[]);
 useEffect(()=>{if(options.length&&!options.includes(assetPath))setAssetPath(options[0])},[catalog,assetPath]);
 useEffect(()=>{
  if(!task||!['pending','running'].includes(task.status))return;
  const timer=window.setInterval(()=>{
   get<Task>('/studio/projects/'+projectId+'/images/tasks/'+task.task_id)
    .then(async response=>{setTask(response);if(response.status==='completed')await onImported()})
    .catch(e=>setError(e instanceof Error?e.message:String(e)));
  },4000);
  return ()=>window.clearInterval(timer);
 },[projectId,task?.task_id,task?.status,onImported]);
 const submit=async()=>{
  if(!window.confirm('G-Labs có thể tiêu thụ quota/credits. Xác nhận gửi MỘT tác vụ image generation? Không có retry tự động.'))return;
  setBusy(true);setError('');
  try{
   const response=await post<Task>('/studio/projects/'+projectId+'/images/generate',{
    asset_path:assetPath,prompt,model,aspect_ratio:ratio,allow_replace:false
   });
   setTask(response);
  }catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(false)}
 };
 return <section className="panel">
  <div className="spread"><h2>G-Labs Webhook — manual image task</h2>
   <button className="btn" onClick={()=>get<Provider>('/studio/provider/glabs').then(setProvider)}><RefreshCcw size={14}/> Check provider</button></div>
  <div className="pills"><span className={'pill '+(provider?.reachable?'ok':'warn')}>{provider?.reachable?'Local webhook reachable':'Local webhook not connected'}</span>
   <span className="pill">{provider?.configured?'Backend credential configured':'Missing backend credential'}</span></div>
  <p className="muted small">API key stays in the Python backend environment. Images will be imported to the selected project asset after completion. Never automatically submits or retries paid generation.</p>
  <div className="fields">
   <label className="field">Target catalog asset<select value={assetPath} onChange={e=>setAssetPath(e.target.value)}>{options.map(x=><option key={x} value={x}>{x}</option>)}</select></label>
   <label className="field">Model<select value={model} onChange={e=>setModel(e.target.value)}><option value="nano_banana_2">nano_banana_2</option><option value="nano_banana_pro">nano_banana_pro</option><option value="nano_banana_2_lite">nano_banana_2_lite</option></select></label>
   <label className="field">Aspect ratio<select value={ratio} onChange={e=>setRatio(e.target.value)}>{['16:9','9:16','1:1','4:3','3:4'].map(x=><option key={x}>{x}</option>)}</select></label>
  </div>
  <label className="field" style={{marginTop:13}}>Generation prompt<textarea rows={4} value={prompt} onChange={e=>setPrompt(e.target.value)}/></label>
  <div className="row" style={{marginTop:12}}>
   <button className="btn primary" disabled={busy||!provider?.reachable||!assetPath||prompt.trim().length<10||task?.status==='pending'||task?.status==='running'} onClick={submit}>
    <ImagePlus size={15}/> Generate once (may consume quota)
   </button>
   {task&&<span className="pill">{task.task_id} · {task.status}</span>}
  </div>
  {error&&<div className="alert" role="alert">{error}</div>}
  {task?.status==='completed'&&<div className="alert ok">Image imported as normalized PNG. Review it in the Asset Library and then run preflight.</div>}
  {task?.status==='failed'&&<div className="alert">The provider reported a failed generation. Review quota and prompt before any new submission.</div>}
 </section>;
}
