/** P6 authored film with camera cuts and actual Genielabs Spine bone poses.
 * Reads P4 world-motion clips and P5 FilmPlan compiled timeline.
 * No realtime ticker, AI video generation, or procedural impostor arm.
 */
import { Application, Assets, Container, Graphics, Text } from 'pixi.js';
import { Spine } from '@esotericsoftware/spine-pixi-v8';

window.__FILM_READY__=false;
window.__FILM_ERROR__=null;
try{
  const requests=['./fixtures/film_timeline.json','./fixtures/baseline/contact_frames.json',
    './fixtures/baseline/rig_profile.json'];
  const documents=await Promise.all(requests.map(async path=>{
    const r=await fetch(path);if(!r.ok)throw Error('Film fixture missing: '+path);
    return r.json();
  }));
  const [timeline,clip,profile]=documents;
  if(timeline.schema_version!=='film.timeline.v1'||timeline.total_frames!==timeline.frames.length||
     timeline.fps!==24||clip.frames.length!==48)throw Error('Film source/timeline incompatible');
  const app=new Application();
  await app.init({width:timeline.width,height:timeline.height,backgroundColor:0xe7dfce,
      antialias:false,resolution:1,preference:'webgl',autoStart:false});
  app.ticker.stop();document.querySelector('#app').appendChild(app.canvas);

  Assets.add({alias:'film-skeleton',src:'./fixtures/baseline/skeleton.json'});
  Assets.add({alias:'film-atlas',src:'./fixtures/baseline/skeleton.atlas'});
  await Assets.load(['film-skeleton','film-atlas']);
  const scene=new Container();app.stage.addChild(scene);
  const bg=new Graphics().rect(-500,-500,1600,1600).fill(0xe9e1d2)
    .rect(0,330,640,220).fill(0xcba88d)
    .rect(30,35,150,133).fill(0xa3c3ca).stroke({color:0x675346,width:5})
    .rect(270,208,308,18).fill(0x866549)
    .rect(296,226,17,175).fill(0x735640)
    .rect(542,226,17,175).fill(0x735640);
  scene.addChild(bg);

  const actor=Spine.from({skeleton:'film-skeleton',atlas:'film-atlas',autoUpdate:false});
  actor.position.set(profile.actor_origin.x,profile.actor_origin.y);
  actor.state.clearTracks();scene.addChild(actor);
  const upper=actor.skeleton.findBone(profile.bones.upper_arm);
  const lower=actor.skeleton.findBone(profile.bones.forearm);
  const wrist=actor.skeleton.findBone(profile.bones.hand);
  if(!upper||!lower||!wrist)throw Error('Required actor bone missing');

  const cup=new Graphics().roundRect(-12,-13,24,25,3).fill(0xc55b49)
    .stroke({color:0x633d38,width:3}).circle(16,-2,7)
    .stroke({color:0x633d38,width:4});
  scene.addChild(cup);
  const banner=new Graphics().rect(0,0,640,39).fill({color:0x243444,alpha:0.91});
  app.stage.addChild(banner);
  const heading=new Text({text:'',style:{fontFamily:'Arial',fontSize:17,fill:0xffffff,fontWeight:'bold'}});
  heading.position.set(18,8);app.stage.addChild(heading);
  const footer=new Graphics().rect(0,439,640,41).fill({color:0x243444,alpha:0.9});
  app.stage.addChild(footer);
  const subtitles=new Text({text:'',style:{fontFamily:'Arial',fontSize:13,fill:0xffffff}});
  subtitles.position.set(13,449);app.stage.addChild(subtitles);

  const angle=(a,b)=>Math.atan2(b.y-a.y,b.x-a.x)*180/Math.PI;
  const toSpine=p=>({x:p.x-profile.actor_origin.x,y:profile.actor_origin.y-p.y});
  const toPixels=b=>({x:b.worldX+profile.actor_origin.x,y:profile.actor_origin.y+b.worldY});
  const dist=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const cues=new Map(timeline.narration.map(x=>[x.shot_id,x]));
  const drawFrame=n=>{
    if(!Number.isSafeInteger(n)||n<0||n>=timeline.total_frames)throw Error('Film frame out of range');
    const frame=timeline.frames[n], pose=clip.frames[frame.clip_frame];
    if(frame.rig_id!==profile.rig_id)throw Error('Film needs an unavailable rig: '+frame.rig_id);
    const sh=toSpine(pose.shoulder),el=toSpine(pose.elbow),hand=toSpine(pose.hand);
    const upperAngle=angle(sh,el),lowerAngle=angle(el,hand);
    actor.skeleton.setToSetupPose();actor.state.clearTracks();
    upper.rotation=upperAngle;lower.rotation=lowerAngle-upperAngle;
    actor.update(0);
    const actual=toPixels(wrist);
    if(dist(actual,pose.hand)>0.1)throw Error('P6 actual Spine wrist drift at '+n);
    const theta=(pose.prop_rotation_deg??0)*Math.PI/180;
    const ox=clip.grip_offset.x*Math.cos(theta)-clip.grip_offset.y*Math.sin(theta);
    const oy=clip.grip_offset.x*Math.sin(theta)+clip.grip_offset.y*Math.cos(theta);
    if(pose.prop_state==='held'&&dist({x:actual.x+ox,y:actual.y+oy},pose.prop)>0.001)
      throw Error('P6 cup lost the real Spine wrist at '+n);
    cup.position.set(pose.prop.x,pose.prop.y);cup.rotation=theta;
    scene.scale.set(frame.camera.zoom);
    scene.position.set(320-(320*frame.camera.zoom)+frame.camera.pan_x,
       240-(240*frame.camera.zoom)+frame.camera.pan_y);
    const cue=cues.get(frame.shot_id);
    heading.text='THE COFFEE CUP SAVE     '+frame.shot_id.replaceAll('_',' ').toUpperCase();
    subtitles.text=cue.text;
    app.render();
    return {frame:n,shot:frame.shot_id,clipFrame:frame.clip_frame,wristError:dist(actual,pose.hand)};
  };
  window.__FILM_DRAW_FRAME__=drawFrame;
  window.__FILM_TIMELINE__=timeline;
  drawFrame(0);
  window.__FILM_READY__=true;
}catch(error){window.__FILM_ERROR__=error instanceof Error?error.stack||error.message:String(error);}
