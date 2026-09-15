(() => {
  'use strict';
  const canvas = document.querySelector('#gameCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  const ui = {
    start: document.querySelector('#startScreen'), over: document.querySelector('#gameOverScreen'),
    pause: document.querySelector('#pauseScreen'), best: document.querySelector('#bestScore'),
    final: document.querySelector('#finalScore'), finalBest: document.querySelector('#finalBest'),
    startBtn: document.querySelector('#startButton'), restartBtn: document.querySelector('#restartButton'),
    sound: document.querySelector('#soundButton')
  };
  let state = 'menu', score = 0, best = +(localStorage.getItem('xeviora-best') || 0), lives = 3;
  let last = 0, elapsed = 0, scroll = 0, spawnClock = 0, groundClock = 0, shake = 0, soundOn = true;
  let bullets = [], enemies = [], enemyBullets = [], bombs = [], targets = [], particles = [], stars = [];
  const keys = new Set();
  const player = { x: W/2, y:H-110, r:15, speed:250, cooldown:0, invuln:0, tilt:0 };
  for(let i=0;i<90;i++) stars.push({x:Math.random()*W,y:Math.random()*H,s:Math.random()*2+.4,a:Math.random()*.5+.2});
  ui.best.textContent = pad(best);

  let audio;
  function tone(freq=220,dur=.06,type='square',vol=.025){
    if(!soundOn) return;
    audio ||= new (window.AudioContext||window.webkitAudioContext)();
    const o=audio.createOscillator(), g=audio.createGain(); o.type=type;o.frequency.value=freq;
    g.gain.setValueAtTime(vol,audio.currentTime);g.gain.exponentialRampToValueAtTime(.0001,audio.currentTime+dur);
    o.connect(g).connect(audio.destination);o.start();o.stop(audio.currentTime+dur);
  }
  function pad(n){return Math.floor(n).toString().padStart(6,'0')}
  function reset(){
    score=0;lives=3;elapsed=scroll=spawnClock=groundClock=shake=0;
    bullets=[];enemies=[];enemyBullets=[];bombs=[];targets=[];particles=[];
    Object.assign(player,{x:W/2,y:H-110,cooldown:0,invuln:0,tilt:0});
    state='playing';ui.start.classList.remove('visible');ui.over.classList.remove('visible');ui.pause.classList.remove('visible');
    last=performance.now();tone(330,.08);setTimeout(()=>tone(660,.1),90);
  }
  function circleHit(a,b,extra=0){return Math.hypot(a.x-b.x,a.y-b.y)<a.r+b.r+extra}
  function burst(x,y,color,count=12,speed=130){
    for(let i=0;i<count;i++){const a=Math.random()*Math.PI*2,v=Math.random()*speed+20;particles.push({x,y,vx:Math.cos(a)*v,vy:Math.sin(a)*v,r:Math.random()*3+1,life:Math.random()*.45+.25,color});}
  }
  function spawnEnemy(){
    const hard=Math.min(1,elapsed/90), type=Math.random()<.22+hard*.12?'zig':'basic';
    enemies.push({x:35+Math.random()*(W-70),y:-25,r:type==='zig'?14:13,hp:type==='zig'?2:1,speed:75+Math.random()*45+hard*45,type,t:Math.random()*6,fire:.8+Math.random()*1.4,baseX:0});
    enemies[enemies.length-1].baseX=enemies[enemies.length-1].x;
  }
  function spawnTarget(){targets.push({x:40+Math.random()*(W-80),y:-40,r:18,hp:2,phase:Math.random()*6});}
  function shoot(){
    if(player.cooldown<=0){bullets.push({x:player.x-8,y:player.y-15,r:3},{x:player.x+8,y:player.y-15,r:3});player.cooldown=.13;tone(760,.035,'square',.018);}
  }
  function dropBomb(){
    if(bombs.length<2){bombs.push({x:player.x,y:player.y-3,r:5,t:0,tx:player.x,ty:Math.max(120,player.y-190)});tone(180,.08,'sine',.035);}
  }
  function hitPlayer(){
    if(player.invuln>0) return; lives--;player.invuln=2.2;shake=10;burst(player.x,player.y,'#8efff5',28,210);tone(70,.45,'sawtooth',.05);
    if(lives<=0) endGame();
  }
  function endGame(){
    state='over';best=Math.max(best,score);localStorage.setItem('xeviora-best',best);ui.best.textContent=pad(best);ui.final.textContent=pad(score);ui.finalBest.textContent=pad(best);ui.over.classList.add('visible');
  }
  function update(dt){
    elapsed+=dt;scroll+=dt*(75+Math.min(55,elapsed*.5));shake=Math.max(0,shake-dt*30);
    player.cooldown-=dt;player.invuln-=dt;
    let dx=(keys.has('ArrowRight')||keys.has('KeyD')?1:0)-(keys.has('ArrowLeft')||keys.has('KeyA')?1:0);
    let dy=(keys.has('ArrowDown')||keys.has('KeyS')?1:0)-(keys.has('ArrowUp')||keys.has('KeyW')?1:0);
    if(dx&&dy){dx*=.707;dy*=.707} player.x=Math.max(20,Math.min(W-20,player.x+dx*player.speed*dt));player.y=Math.max(75,Math.min(H-35,player.y+dy*player.speed*dt));player.tilt+=(dx-player.tilt)*dt*10;
    if(keys.has('Space'))shoot();
    spawnClock-=dt;groundClock-=dt;
    if(spawnClock<=0){spawnEnemy();spawnClock=Math.max(.28,.8-elapsed*.004)*(Math.random()*.5+.75)}
    if(groundClock<=0){spawnTarget();groundClock=2.2+Math.random()*2}
    bullets.forEach(b=>b.y-=540*dt); bullets=bullets.filter(b=>b.y>-20);
    enemies.forEach(e=>{e.t+=dt;e.y+=e.speed*dt;if(e.type==='zig')e.x=e.baseX+Math.sin(e.t*3)*55;e.fire-=dt;if(e.fire<0&&e.y>40&&e.y<H*.7){const a=Math.atan2(player.y-e.y,player.x-e.x);enemyBullets.push({x:e.x,y:e.y,r:4,vx:Math.cos(a)*150,vy:Math.sin(a)*150});e.fire=1.1+Math.random()*1.3}});
    targets.forEach(t=>{t.y+=(75+Math.min(55,elapsed*.5))*dt;t.phase+=dt});
    enemyBullets.forEach(b=>{b.x+=b.vx*dt;b.y+=b.vy*dt});
    bombs.forEach(b=>{b.t+=dt;const p=Math.min(1,b.t/.65);b.x+=(b.tx-b.x)*dt*5;b.y+=(b.ty-b.y)*dt*5;b.r=5+p*7;if(p>=1){targets.forEach(t=>{if(Math.hypot(t.x-b.x,t.y-b.y)<55){t.hp-=2;t.dead=t.hp<=0;if(t.dead){score+=250;burst(t.x,t.y,'#ffc45b',24,170)}}});burst(b.x,b.y,'#ffd36c',32,210);shake=7;b.dead=true;tone(90,.25,'sawtooth',.05)}});
    for(const b of bullets)for(const e of enemies)if(!b.dead&&!e.dead&&circleHit(b,e)){b.dead=true;e.hp--;burst(b.x,b.y,'#8efff5',4,70);if(e.hp<=0){e.dead=true;score+=e.type==='zig'?150:100;burst(e.x,e.y,'#ff755f',16,150);tone(120,.09,'square',.025)}}
    for(const e of enemies)if(!e.dead&&circleHit(player,e)){e.dead=true;hitPlayer()}
    for(const b of enemyBullets)if(!b.dead&&circleHit(player,b)){b.dead=true;hitPlayer()}
    enemies=enemies.filter(e=>!e.dead&&e.y<H+40);enemyBullets=enemyBullets.filter(b=>!b.dead&&b.y<H+20&&b.x>-20&&b.x<W+20);targets=targets.filter(t=>!t.dead&&t.y<H+50);bullets=bullets.filter(b=>!b.dead);bombs=bombs.filter(b=>!b.dead);
    particles.forEach(p=>{p.x+=p.vx*dt;p.y+=p.vy*dt;p.vx*=.97;p.vy*=.97;p.life-=dt;p.r*=.985});particles=particles.filter(p=>p.life>0);
  }
  function drawBackground(){
    const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#0b4550');g.addColorStop(1,'#153e36');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    ctx.save();ctx.translate(0,scroll%180);for(let y=-180;y<H;y+=180){
      ctx.fillStyle='#35614c';ctx.beginPath();ctx.moveTo(0,y+25);ctx.bezierCurveTo(100,y-20,150,y+90,245,y+30);ctx.bezierCurveTo(330,y-15,385,y+70,W,y+15);ctx.lineTo(W,y+95);ctx.bezierCurveTo(360,y+130,310,y+65,220,y+115);ctx.bezierCurveTo(120,y+160,70,y+75,0,y+120);ctx.fill();
      ctx.strokeStyle='#50765c';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(-20,y+75);ctx.bezierCurveTo(100,y+15,170,y+145,300,y+75);ctx.bezierCurveTo(380,y+35,430,y+100,510,y+55);ctx.stroke();
    }ctx.restore();
    for(const s of stars){let yy=(s.y+scroll*s.s*.35)%H;ctx.fillStyle=`rgba(191,255,235,${s.a})`;ctx.fillRect(s.x,yy,s.s,s.s*3)}
    ctx.fillStyle='rgba(8,37,38,.22)';for(let x=20;x<W;x+=58){const off=(scroll*.55+x*3)%140;for(let y=-140;y<H;y+=140)ctx.fillRect(x,y+off,2,12)}
  }
  function drawTarget(t){ctx.save();ctx.translate(t.x,t.y);ctx.rotate(t.phase*.25);ctx.strokeStyle='#e7bd63';ctx.lineWidth=3;ctx.beginPath();ctx.arc(0,0,17,0,7);ctx.stroke();ctx.rotate(-t.phase);ctx.fillStyle='#9b5639';ctx.fillRect(-10,-10,20,20);ctx.fillStyle='#ffce65';ctx.fillRect(-3,-3,6,6);ctx.restore()}
  function drawEnemy(e){ctx.save();ctx.translate(e.x,e.y);ctx.fillStyle=e.type==='zig'?'#e25f5c':'#d8b05f';ctx.beginPath();ctx.moveTo(0,16);ctx.lineTo(-17,-10);ctx.lineTo(-6,-7);ctx.lineTo(0,-18);ctx.lineTo(6,-7);ctx.lineTo(17,-10);ctx.closePath();ctx.fill();ctx.fillStyle='#401f28';ctx.fillRect(-4,-7,8,11);ctx.strokeStyle='#fff2b0';ctx.lineWidth=1;ctx.stroke();ctx.restore()}
  function drawPlayer(){
    if(player.invuln>0&&Math.floor(player.invuln*12)%2===0)return;ctx.save();ctx.translate(player.x,player.y);ctx.rotate(player.tilt*.18);ctx.shadowColor='#5ef2e5';ctx.shadowBlur=12;ctx.fillStyle='#c9f3ea';ctx.beginPath();ctx.moveTo(0,-23);ctx.lineTo(-7,-5);ctx.lineTo(-23,8);ctx.lineTo(-9,9);ctx.lineTo(-5,20);ctx.lineTo(0,15);ctx.lineTo(5,20);ctx.lineTo(9,9);ctx.lineTo(23,8);ctx.lineTo(7,-5);ctx.closePath();ctx.fill();ctx.shadowBlur=0;ctx.fillStyle='#15556a';ctx.beginPath();ctx.moveTo(0,-14);ctx.lineTo(-4,2);ctx.lineTo(4,2);ctx.closePath();ctx.fill();ctx.fillStyle='#ffbd54';ctx.fillRect(-3,16,6,10);ctx.restore();
  }
  function drawHud(){
    ctx.fillStyle='rgba(3,12,17,.72)';ctx.fillRect(12,12,148,52);ctx.strokeStyle='#315b63';ctx.strokeRect(12.5,12.5,148,52);ctx.font='11px Share Tech Mono, monospace';ctx.fillStyle='#6f999c';ctx.fillText('SCORE',24,29);ctx.fillStyle='#e7fff9';ctx.font='21px Share Tech Mono, monospace';ctx.fillText(pad(score),24,52);
    ctx.fillStyle='rgba(3,12,17,.72)';ctx.fillRect(W-106,12,94,52);ctx.strokeStyle='#315b63';ctx.strokeRect(W-105.5,12.5,93,52);ctx.font='11px Share Tech Mono, monospace';ctx.fillStyle='#6f999c';ctx.fillText('SHIPS',W-94,29);for(let i=0;i<lives;i++){ctx.fillStyle='#68e7dc';ctx.beginPath();ctx.moveTo(W-88+i*20,51);ctx.lineTo(W-82+i*20,36);ctx.lineTo(W-76+i*20,51);ctx.closePath();ctx.fill()}
    if(state==='playing'){const warning=elapsed%18>15;if(warning){ctx.textAlign='center';ctx.fillStyle=`rgba(255,196,91,${.55+Math.sin(elapsed*10)*.35})`;ctx.font='12px Share Tech Mono, monospace';ctx.fillText('! ENEMY WAVE APPROACHING !',W/2,88);ctx.textAlign='left'}}
  }
  function render(){
    ctx.save();if(shake){ctx.translate((Math.random()-.5)*shake,(Math.random()-.5)*shake)}drawBackground();
    targets.forEach(drawTarget);for(const b of bombs){ctx.strokeStyle=`rgba(255,206,94,${1-b.t})`;ctx.lineWidth=2;ctx.beginPath();ctx.arc(b.tx,b.ty,18+Math.sin(b.t*18)*5,0,7);ctx.stroke();ctx.fillStyle='#ffc95c';ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,7);ctx.fill()}
    ctx.fillStyle='#7cfff2';ctx.shadowColor='#7cfff2';ctx.shadowBlur=9;for(const b of bullets){ctx.fillRect(b.x-2,b.y-7,4,13)}ctx.shadowBlur=0;
    enemies.forEach(drawEnemy);ctx.fillStyle='#ff855f';for(const b of enemyBullets){ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,7);ctx.fill()}
    drawPlayer();for(const p of particles){ctx.globalAlpha=Math.max(0,p.life*2);ctx.fillStyle=p.color;ctx.fillRect(p.x-p.r/2,p.y-p.r/2,p.r,p.r)}ctx.globalAlpha=1;drawHud();ctx.restore();
  }
  function loop(now){const dt=Math.min(.033,(now-last)/1000||0);last=now;if(state==='playing')update(dt);render();requestAnimationFrame(loop)}
  function togglePause(){if(state==='playing'){state='paused';ui.pause.classList.add('visible')}else if(state==='paused'){state='playing';ui.pause.classList.remove('visible');last=performance.now()}}
  addEventListener('keydown',e=>{if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();keys.add(e.code);if(e.code==='Enter'&&(state==='menu'||state==='over'))reset();if(e.code==='KeyP')togglePause();if(e.code==='KeyX'&&state==='playing'&&!e.repeat)dropBomb()});
  addEventListener('keyup',e=>keys.delete(e.code));ui.startBtn.addEventListener('click',reset);ui.restartBtn.addEventListener('click',reset);
  ui.sound.addEventListener('click',()=>{soundOn=!soundOn;ui.sound.textContent=`SOUND: ${soundOn?'ON':'OFF'}`;if(soundOn)tone(440,.05)});
  let touchShoot=false;canvas.addEventListener('pointerdown',e=>{if(state!=='playing')return;touchShoot=true;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!touchShoot)return;const r=canvas.getBoundingClientRect();player.x=(e.clientX-r.left)*W/r.width;player.y=(e.clientY-r.top)*H/r.height;shoot()});canvas.addEventListener('pointerup',()=>{touchShoot=false});
  requestAnimationFrame(loop);
})();
