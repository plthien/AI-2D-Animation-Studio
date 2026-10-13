/** P4 local diagnostic puppet: procedural 2-bone IK playback on a PixiJS stage.
 * Note: this is NOT yet a retargeted Genielabs/Spine bone rig.
 */
import { Application, Graphics, Text } from 'pixi.js';

window.__CONTACT_READY__ = false;
window.__CONTACT_ERROR__ = null;
const app = new Application();
try {
  const response = await fetch('./fixtures/contact_frames.json');
  if (!response.ok) throw Error('Compiled motion fixture unavailable: ' + response.status);
  const clip = await response.json();
  if (clip.schema_version !== 'p4.1' || clip.frames.length !== clip.duration_frames) {
    throw Error('Invalid motion compiler output schema');
  }
  await app.init({width:640,height:480,backgroundColor:0xe7dfce,
    antialias:false,preference:'webgl',resolution:1,autoStart:false});
  app.ticker.stop();
  document.querySelector('#app').appendChild(app.canvas);

  const room = new Graphics()
    .rect(0,0,640,480).fill(0xe9e1d2)
    .rect(0,316,640,164).fill(0xc6a68e)
    .rect(25,42,156,128).fill(0x9ec0cb).stroke({color:0x66544d,width:6})
    .moveTo(103,42).lineTo(103,170).stroke({color:0x66544d,width:4})
    .roundRect(410,70,175,135,10).fill(0xd0bba3).stroke({color:0x907360,width:5})
    .rect(280,212,300,18).fill(0x816149)
    .rect(308,229,16,172).fill(0x705543)
    .rect(538,229,16,172).fill(0x705543);
  app.stage.addChild(room);

  const torso = new Graphics()
    .roundRect(109,164,64,113,18).fill(0xeaa44b).stroke({color:0x3c4651,width:4})
    .moveTo(121,275).lineTo(116,353).stroke({color:0x3c4651,width:15})
    .moveTo(158,275).lineTo(172,353).stroke({color:0x3c4651,width:15})
    .ellipse(140,132,40,37).fill(0x354c62).stroke({color:0x263340,width:4})
    .ellipse(125,124,5,8).fill(0xf6f8f4)
    .ellipse(153,124,5,8).fill(0xf6f8f4)
    .moveTo(126,145).lineTo(151,145).stroke({color:0xf6f8f4,width:3});
  app.stage.addChild(torso);

  const arm = new Graphics();
  const mug = new Graphics()
    .roundRect(-12,-13,24,25,3).fill(0xc55b49).stroke({color:0x633d38,width:3})
    .circle(16,-2,7).stroke({color:0x633d38,width:4});
  const hand = new Graphics().circle(0,0,8).fill(0x354c62).stroke({color:0xffffff,width:1.5});
  app.stage.addChild(arm,mug,hand);

  const label = new Text({text:'P4 / PARAMETRIC CONTACT MOTION',style:{
    fontFamily:'Arial',fontSize:17,fill:0x273543,fontWeight:'bold'}});
  label.position.set(24,18);app.stage.addChild(label);
  const stateLabel = new Text({text:'',style:{fontFamily:'Arial',fontSize:16,fill:0x333333}});
  stateLabel.position.set(24,424);app.stage.addChild(stateLabel);

  const drawFrame = (index) => {
    if(!Number.isInteger(index) || index < 0 || index >= clip.frames.length) {
      throw Error('Frame out of range');
    }
    const f = clip.frames[index];
    arm.clear().moveTo(f.shoulder.x,f.shoulder.y)
      .lineTo(f.elbow.x,f.elbow.y).lineTo(f.hand.x,f.hand.y)
      .stroke({color:0x354c62,width:15,cap:'round',join:'round'});
    hand.position.set(f.hand.x,f.hand.y);
    mug.position.set(f.prop.x,f.prop.y);
    stateLabel.text = 'FRAME '+String(index).padStart(3,'0')+' / '+f.phase.toUpperCase()+
      ' / CUP '+f.prop_state.toUpperCase();
    app.render();
    return f;
  };
  window.__CONTACT_RENDER_FRAME__ = drawFrame;
  window.__CONTACT_CLIP__ = clip;
  drawFrame(0);
  window.__CONTACT_READY__ = true;
} catch (error) {
  window.__CONTACT_ERROR__ = error instanceof Error ? error.message : String(error);
}
