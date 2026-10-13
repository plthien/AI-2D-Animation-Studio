/** P4 Spine-BONE retarget proof. All arm art comes from Genielabs-generated
 * Spine attachments. IK positions come from the independent P4 Python compiler.
 * No Pixi line drawing of the actor arm is used.
 */
import { Application, Assets, Graphics, Text } from 'pixi.js';
import { Spine } from '@esotericsoftware/spine-pixi-v8';

window.__CONTACT_SPINE_READY__ = false;
window.__CONTACT_SPINE_ERROR__ = null;
try {
  const data = await fetch('./fixtures/contact_frames.json');
  if(!data.ok) throw Error('Missing compiled P4 motion frames');
  const clip = await data.json();
  if(clip.schema_version!=='p4.1' || clip.duration_frames!==clip.frames.length) throw Error('Invalid motion plan');
  const app = new Application();
  await app.init({width:640,height:480,backgroundColor:0xe7dfce,antialias:false,
    resolution:1,preference:'webgl',autoStart:false});
  app.ticker.stop();
  document.querySelector('#app').appendChild(app.canvas);

  Assets.add({alias:'p4skeleton',src:'./fixtures/skeleton.json'});
  Assets.add({alias:'p4atlas',src:'./fixtures/skeleton.atlas'});
  await Assets.load(['p4skeleton','p4atlas']);
  const actor = Spine.from({skeleton:'p4skeleton',atlas:'p4atlas',autoUpdate:false});
  actor.position.set(320,480);
  actor.scale.set(1);
  actor.state.clearTracks();
  app.stage.addChild(actor);

  const table = new Graphics()
    .rect(270,208,308,18).fill(0x866549)
    .rect(296,226,17,175).fill(0x735640)
    .rect(542,226,17,175).fill(0x735640);
  // Place the table behind/next to the character without masking the arm.
  app.stage.addChildAt(table,0);

  const prop = new Graphics()
    .roundRect(-12,-13,24,25,3).fill(0xc55b49).stroke({color:0x633d38,width:3})
    .circle(16,-2,7).stroke({color:0x633d38,width:4});
  app.stage.addChild(prop);

  const label = new Text({text:'GENIELABS SPINE RIG / TRUE BONE IK',style:
    {fontFamily:'Arial',fontSize:16,fill:0x2e3d4b,fontWeight:'bold'}});
  label.position.set(12,16);app.stage.addChild(label);
  const stateLabel = new Text({text:'',style:{fontFamily:'Arial',fontSize:13,fill:0x354251}});
  stateLabel.position.set(12,435);app.stage.addChild(stateLabel);

  const upper=actor.skeleton.findBone('left-upper-arm');
  const lower=actor.skeleton.findBone('left-lower-arm');
  const wrist=actor.skeleton.findBone('left-hand');
  const torso=actor.skeleton.findBone('torso');
  if(!upper||!lower||!wrist||!torso) throw Error('Genielabs Spine rig missing required arm bones');
  // Pixel screen x to Spine skeleton x: root lies at screen x=320.
  // Pixel screen y to Spine world y: root lies at screen y=480, positive Y up.
  const pixelToSpine=(p)=>({x:p.x-320,y:480-p.y});
  const spineToPixel=(p)=>({x:p.worldX+320,y:480+p.worldY}); // Spine-Pixi v8 uses y-down bone worldY
  const angle=(p,q)=>Math.atan2(q.y-p.y,q.x-p.x)*180/Math.PI;
  const mismatch=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
  const drawFrame=(frame)=>{
    if(!Number.isInteger(frame)||frame<0||frame>=clip.frames.length)throw Error('Frame out of range');
    const pose=clip.frames[frame];
    const shoulder=pixelToSpine(pose.shoulder);
    const elbow=pixelToSpine(pose.elbow);
    const hand=pixelToSpine(pose.hand);
    const upperAngle=angle(shoulder,elbow);
    const lowerAngle=angle(elbow,hand);
    actor.skeleton.setToSetupPose();
    actor.state.clearTracks();
    upper.rotation=upperAngle;
    lower.rotation=lowerAngle-upperAngle;
    actor.update(0); // Spine recomputes bone world transforms in hierarchy order
    const actualShoulder=spineToPixel(upper);
    const actualElbow=spineToPixel(lower);
    const actualWrist=spineToPixel(wrist);
    const shoulderErr=mismatch(actualShoulder,pose.shoulder);
    const elbowErr=mismatch(actualElbow,pose.elbow);
    const wristErr=mismatch(actualWrist,pose.hand);
    if(shoulderErr>0.1||elbowErr>0.1||wristErr>0.1) {
      throw Error('Spine IK bone mismatch frame='+frame+
        ' shoulder='+shoulderErr+' elbow='+elbowErr+' wrist='+wristErr+
        ' actual='+JSON.stringify({actualShoulder,actualElbow,actualWrist}));
    }
    if(pose.prop_state==='held'&&mismatch(pose.prop,actualWrist)>0.001) {
      throw Error('Prop contact drift on real Spine wrist at frame '+frame);
    }
    prop.position.set(pose.prop.x,pose.prop.y);
    stateLabel.text='FRAME '+String(frame).padStart(3,'0')+' | '+pose.phase+
      ' | PROP '+pose.prop_state+' | WRIST ERROR '+wristErr.toFixed(4)+'px';
    app.render();
    return {frame,shoulderErr,elbowErr,wristErr,propState:pose.prop_state,
      actualWrist,actualElbow,upperRotation:upper.rotation,lowerRotation:lower.rotation};
  };
  window.__SPINE_CONTACT_FRAME__=drawFrame;
  window.__SPINE_CONTACT_ACTOR__=actor;
  window.__SPINE_CONTACT_CLIP__=clip;
  drawFrame(0);
  window.__CONTACT_SPINE_READY__=true;
} catch(e) {
  window.__CONTACT_SPINE_ERROR__=e instanceof Error?e.stack||e.message:String(e);
}
