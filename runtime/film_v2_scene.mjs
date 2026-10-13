/** Data-driven Spine film.v2 renderer — zero shot-specific animation code.
 * Independent Spine skeletons/motions/background PNGs/prop PNGs are loaded from
 * the compiled asset catalog. Never stretches motion clips between shots.
 */
import { Application, Assets, Container, Sprite, Text, Graphics } from 'pixi.js';
import { Spine } from '@esotericsoftware/spine-pixi-v8';

window.__FILM_V2_READY__=false;
window.__FILM_V2_ERROR__=null;
try {
  const getJson=async path=>{
    const response=await fetch(path);
    if(!response.ok)throw Error('Required fixture missing: '+path+' HTTP '+response.status);
    return response.json();
  };
  const [timeline,motions]=await Promise.all([
    getJson('./fixtures/film_timeline.json'),
    getJson('./fixtures/film_motions.json')]);
  if(timeline.schema_version!=='film.timeline.v2'||timeline.total_frames!==timeline.frames.length||
      timeline.fps!==24)throw Error('film.v2 timeline contract failure');

  const app=new Application();
  await app.init({width:timeline.width,height:timeline.height,
    backgroundColor:0xe7dfce,resolution:1,antialias:false,
    preference:'webgl',autoStart:false});
  app.ticker.stop();
  document.querySelector('#app').appendChild(app.canvas);
  const stage=new Container();
  stage.sortableChildren=true;
  app.stage.addChild(stage);

  const rigs={}, backgrounds={}, props={};
  for(const [id,asset] of Object.entries(timeline.assets.rigs)){
    const base='./fixtures/'+asset.directory+'/';
    Assets.add({alias:'rig_json_'+id,src:base+'skeleton.json'});
    Assets.add({alias:'rig_atlas_'+id,src:base+'skeleton.atlas'});
    rigs[id]={profile:await getJson(base+'rig_profile.json')};
    if(rigs[id].profile.rig_id!==id)throw Error('Rig profile identity mismatch: '+id);
  }
  for(const [id,asset] of Object.entries(timeline.assets.backgrounds)){
    Assets.add({alias:'background_'+id,src:'./fixtures/'+asset.image});
  }
  for(const [id,asset] of Object.entries(timeline.assets.props)){
    Assets.add({alias:'prop_'+id,src:'./fixtures/'+asset.image});
  }
  const aliases=[
    ...Object.keys(rigs).flatMap(id=>['rig_json_'+id,'rig_atlas_'+id]),
    ...Object.keys(timeline.assets.backgrounds).map(id=>'background_'+id),
    ...Object.keys(timeline.assets.props).map(id=>'prop_'+id)
  ];
  await Assets.load(aliases);

  for(const [id,rig] of Object.entries(rigs)){
    const actor=Spine.from({skeleton:'rig_json_'+id,atlas:'rig_atlas_'+id,autoUpdate:false});
    actor.state.clearTracks();
    actor.visible=false;
    stage.addChild(actor);
    rig.actor=actor;
    rig.upper=actor.skeleton.findBone(rig.profile.bones.upper_arm);
    rig.lower=actor.skeleton.findBone(rig.profile.bones.forearm);
    rig.hand=actor.skeleton.findBone(rig.profile.bones.hand);
    if(!rig.upper||!rig.lower||!rig.hand)throw Error('Spine rig missing arm bones: '+id);
  }
  for(const id of Object.keys(timeline.assets.backgrounds)){
    const sprite=new Sprite(Assets.get('background_'+id));
    sprite.width=timeline.width;sprite.height=timeline.height;
    sprite.zIndex=-100;
    sprite.visible=false;
    backgrounds[id]=sprite;
    stage.addChild(sprite);
  }
  for(const id of Object.keys(timeline.assets.props)){
    const sprite=new Sprite(Assets.get('prop_'+id));
    sprite.anchor.set(.5);
    sprite.zIndex=10;sprite.visible=false;
    props[id]=sprite;
    stage.addChild(sprite);
  }

  const titleBand=new Graphics().rect(0,0,timeline.width,34).fill({color:0x263545,alpha:.91});
  app.stage.addChild(titleBand);
  const title=new Text({text:'',style:{fontFamily:'Arial',fontSize:16,fill:0xffffff,fontWeight:'bold'}});
  title.position.set(12,7);app.stage.addChild(title);
  const subtitleBand=new Graphics().rect(0,timeline.height-44,timeline.width,44)
    .fill({color:0x263545,alpha:.9});
  app.stage.addChild(subtitleBand);
  const subtitle=new Text({text:'',style:{fontFamily:'Arial',fontSize:12,fill:0xffffff}});
  subtitle.position.set(10,timeline.height-31);app.stage.addChild(subtitle);

  const cueMap=new Map(timeline.narration.map(event=>[event.shot_id,event]));
  const toSpine=(p,profile)=>({x:p.x-profile.actor_origin.x,y:profile.actor_origin.y-p.y});
  const angle=(p,q)=>Math.atan2(q.y-p.y,q.x-p.x)*180/Math.PI;
  const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const drawFrame=frameIndex=>{
    if(!Number.isSafeInteger(frameIndex)||frameIndex<0||frameIndex>=timeline.total_frames)
      throw Error('Invalid film frame index');
    const frame=timeline.frames[frameIndex];
    for(const rig of Object.values(rigs))rig.actor.visible=false;
    for(const background of Object.values(backgrounds))background.visible=false;
    for(const prop of Object.values(props))prop.visible=false;
    if(!backgrounds[frame.background_id])throw Error('Unknown rendered background');
    backgrounds[frame.background_id].visible=true;

    const actors={};
    for(const assignment of frame.actors){
      const rig=rigs[assignment.rig_id],clip=motions[assignment.motion_id];
      if(!rig||!clip||clip.rig_id!==assignment.rig_id)
        throw Error('Unknown or mismatched actor asset');
      const pose=clip.frames[assignment.pose_frame];
      if(!pose||pose.frame!==assignment.pose_frame)throw Error('Motion clip frame gap');
      const actor=rig.actor,profile=rig.profile;
      actor.skeleton.setToSetupPose();actor.state.clearTracks();
      const shoulder=toSpine(pose.shoulder,profile);
      const elbow=toSpine(pose.elbow,profile);
      const wrist=toSpine(pose.hand,profile);
      const upperAngle=angle(shoulder,elbow),lowerAngle=angle(elbow,wrist);
      rig.upper.rotation=upperAngle;
      rig.lower.rotation=lowerAngle-upperAngle;
      actor.update(0);
      actor.position.set(profile.actor_origin.x+assignment.offset_x,
                         profile.actor_origin.y+assignment.offset_y);
      actor.zIndex=assignment.layer;
      actor.visible=true;
      const actual={x:rig.hand.worldX+profile.actor_origin.x+assignment.offset_x,
        y:rig.hand.worldY+profile.actor_origin.y+assignment.offset_y};
      const planned={x:pose.hand.x+assignment.offset_x,
        y:pose.hand.y+assignment.offset_y};
      if(distance(actual,planned)>0.1)throw Error('Actual Spine wrist drift at frame '+frameIndex);
      actors[assignment.actor_id]={pose,actual,assignment,clip};
    }
    for(const reference of frame.props){
      const owner=actors[reference.owner_actor_id],sprite=props[reference.visual_id];
      if(!owner||!sprite)throw Error('Unresolved prop owner or visual');
      const {pose,actual,assignment,clip}=owner;
      const radians=(pose.prop_rotation_deg??0)*Math.PI/180;
      const offset=clip.grip_offset??{x:0,y:0};
      const rotated={x:offset.x*Math.cos(radians)-offset.y*Math.sin(radians),
        y:offset.x*Math.sin(radians)+offset.y*Math.cos(radians)};
      const position={x:pose.prop.x+assignment.offset_x,y:pose.prop.y+assignment.offset_y};
      if(pose.prop_state==='held'&&
         distance({x:actual.x+rotated.x,y:actual.y+rotated.y},position)>0.001)
        throw Error('Prop detached from real Spine wrist at frame '+frameIndex);
      sprite.position.set(position.x,position.y);
      sprite.rotation=radians;sprite.zIndex=reference.layer;sprite.visible=true;
    }
    stage.scale.set(frame.camera.zoom);
    stage.position.set(timeline.width/2*(1-frame.camera.zoom)+frame.camera.pan_x,
                       timeline.height/2*(1-frame.camera.zoom)+frame.camera.pan_y);
    title.text='AI 2D STUDIO   /   '+frame.shot_id.replaceAll('_',' ').toUpperCase();
    subtitle.text=cueMap.get(frame.shot_id)?.text??'';
    app.render();
    return {frame:frameIndex,shot:frame.shot_id,background:frame.background_id,
      motionIds:frame.actors.map(actor=>actor.motion_id),
      rigIds:frame.actors.map(actor=>actor.rig_id)};
  };
  window.__FILM_V2_DRAW__=drawFrame;
  window.__FILM_V2_TIMELINE__=timeline;
  drawFrame(0);window.__FILM_V2_READY__=true;
}catch(error){window.__FILM_V2_ERROR__=error instanceof Error?error.stack||error.message:String(error);}
