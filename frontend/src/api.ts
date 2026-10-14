export type Project = {id:string;name:string;template:string;created_at:string};
export type Report = {ready:boolean;errors:string[];missing_assets:string[];warnings:string[];frames:number;shots:number;assets_required:number};
export type Job = {id:string;project_id:string;status:'queued'|'running'|'completed'|'failed';error:string|null;log:string;rendered_frames?:number};
export type Asset = {path:string;bytes:number};
export type Film = {schema_version:string;fps:number;width:number;height:number;shots:Array<{shot_id:string;duration_frames:number;background_id:string;camera:{zoom:number;pan_x:number;pan_y:number};actors:Array<{actor_id:string;rig_id:string;motion_id:string}>;props:Array<{prop_id:string;visual_id:string;owner_actor_id:string}>;narration?:{wav:string;text:string;start_frame:number}|null;continuity_break?:boolean}>};
export type Catalog = {rigs:Record<string,{directory:string}>;backgrounds:Record<string,{image:string}>;props:Record<string,{image:string}>};

export class APIError extends Error {constructor(public status:number,message:string){super(message)}}
const base = '';
export async function api<T>(path:string, options:RequestInit={}):Promise<T>{
  let result:Response;
  try{result=await fetch(base+path,options)}catch{throw new APIError(0,'Không kết nối được backend. Hãy khởi động AI 2D Studio trên localhost:8000.')}
  let value:unknown;try{value=await result.json()}catch{value={detail:result.statusText}}
  if(!result.ok){
    const detail=(value as {detail?:unknown}).detail;
    const error=typeof detail==='string'?detail:JSON.stringify(detail ?? value);
    throw new APIError(result.status,error);
  }
  return value as T;
}
export const get=<T>(p:string)=>api<T>(p);
export const post=<T>(p:string,data:unknown)=>api<T>(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
export const put=<T>(p:string,data:unknown)=>api<T>(p,{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
export async function upload(path:string,file:File){
 const form=new FormData();form.append('file',file);
 return api<{saved:boolean,path:string}>(path,{method:'POST',body:form});
}
