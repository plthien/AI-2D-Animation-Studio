/** Spine 4.2 PixiJS renderer. Seek is re-evaluated from frame zero, NOT wall clock. */
import { Application, Assets } from 'pixi.js';
import { Spine } from '@esotericsoftware/spine-pixi-v8';

const fps=24;
const app=new Application();
window.__FRAME_ERROR__=null;
window.__FRAME_READY__=false;
try {
  await app.init({width:640,height:480,backgroundColor:0x202735,antialias:false,
                  preference:'webgl',resolution:1,autoStart:false});
  app.ticker.stop();
  document.querySelector('#app').appendChild(app.canvas);
  Assets.add({alias:'actorData',src:'./fixtures/sombrero.json'});
  Assets.add({alias:'actorAtlas',src:'./fixtures/sombrero.atlas'});
  await Assets.load(['actorData','actorAtlas']);
  const actor=Spine.from({skeleton:'actorData',atlas:'actorAtlas',autoUpdate:false});
  actor.position.set(320,430);
  actor.scale.set(0.44);
  app.stage.addChild(actor);
  let currentFrame = -1;
  const reset=()=>{
    actor.state.clearTracks();
    actor.skeleton.setToSetupPose();
    actor.state.setAnimation(0,'idle',true);
    actor.update(0);
    currentFrame=0;
  };
  const setFrame=(frame) => {
    if(!Number.isSafeInteger(frame)||frame<0||frame>2400) throw Error('frame out of bound');
    if(currentFrame<0||frame<currentFrame) reset();
    while(currentFrame<frame) {
      actor.update(1/fps);
      currentFrame++;
    }
    app.render();
    return currentFrame;
  };
  window.__RENDER_FRAME__=setFrame;
  window.__SPINE_ACTOR__=actor;
  setFrame(0);
  window.__FRAME_READY__=true;
} catch (e) {
  window.__FRAME_ERROR__=e instanceof Error?e.message:String(e);
}
