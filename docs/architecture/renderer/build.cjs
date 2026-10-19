/* Run from this folder: node build-drawings.cjs. Requires roughjs, fontkit, sharp. */
const fs=require('fs'), path=require('path'), crypto=require('crypto');
const rough=require('roughjs/bundled/rough.cjs.js'), fontkit=require('fontkit'), sharp=require('sharp');
if(!process.argv[2])throw new Error('Usage: node build.cjs path/to/deck.json');
const specPath=path.resolve(process.argv[2]), spec=JSON.parse(fs.readFileSync(specPath,'utf8'));
const ROOT=path.dirname(specPath), OUT=path.join(ROOT,'drawings');
const font=fontkit.openSync(path.join(__dirname,'fonts/Virgil.woff2'));
const P={ink:'#151a23',accent:'#D9681F',data:'#1971c2',muted:'#666666'};
const DARK={'#151a23':'#EEE9DF','#1971c2':'#5AA9E6','#666666':'#B5B3AF','#D9681F':'#D9681F'};
const boards=[];let b;
function element(type,x,y,width,height,extra={}){
 const id=b.key+'-'+b.elements.length,seed=parseInt(crypto.createHash('sha256').update(id).digest('hex').slice(0,7),16);
 const e={id,type,x,y,width,height,angle:0,strokeColor:P.ink,backgroundColor:'transparent',fillStyle:'solid',strokeWidth:2,strokeStyle:'solid',roughness:1.3,opacity:100,groupIds:[],frameId:null,roundness:null,seed,version:1,versionNonce:seed,isDeleted:false,boundElements:[],updated:1,link:null,locked:false,...extra};b.elements.push(e);return e;
}
function measure(s,size){return font.layout(s).positions.reduce((a,p)=>a+p.xAdvance,0)*size/font.unitsPerEm}
function text(s,x,y,w=1220,size=32,color=P.ink,group){
 const widest=Math.max(...s.split('\n').map(l=>measure(l,size)));
 if(widest>w-10)throw new Error(`Text too wide ${b.key}: ${s} (${widest}>${w})`);
 return element('text',x,y,Math.ceil(widest+10),s.split('\n').length*size*1.25,{text:s,originalText:s,fontSize:size,fontFamily:1,lineHeight:1.25,textAlign:'left',verticalAlign:'top',containerId:null,autoResize:false,strokeColor:color,groupIds:group?[group]:[]});
}
function box(x,y,w,h,color=P.accent,group){return element('rectangle',x,y,w,h,{strokeColor:color,roundness:{type:3},groupIds:group?[group]:[]})}
function node(label,x,y,w=340,h=145,color=P.accent,sub){
 const group=b.key+'-g'+b.elements.length,rect=box(x,y,w,h,color,group);
 text(label,x+24,y+23,w-48,31,color,group);if(sub)text(sub,x+24,y+85,w-48,25,P.ink,group);return rect;
}
function arrow(a,z,route){
 let pts;
 if(route)pts=route;
 else if(a.y===z.y){const right=z.x>a.x;pts=right?[[a.x+a.width+12,a.y+a.height/2],[z.x-12,z.y+z.height/2]]:[[a.x-12,a.y+a.height/2],[z.x+z.width+12,z.y+z.height/2]]}
 else {pts=[[a.x+a.width/2,a.y+a.height+12],[z.x+z.width/2,z.y-12]]}
 const [x,y]=pts[0];const rel=pts.map(p=>[p[0]-x,p[1]-y]);const e=element('arrow',x,y,Math.max(...rel.map(p=>p[0]))-Math.min(...rel.map(p=>p[0])),Math.max(...rel.map(p=>p[1]))-Math.min(...rel.map(p=>p[1])),{points:rel,startArrowhead:null,endArrowhead:'arrow',elbowed:false,strokeColor:P.accent,startBinding:{elementId:a.id,focus:0,gap:12},endBinding:{elementId:z.id,focus:0,gap:12}});for(const n of [a,z])n.boundElements.push({id:e.id,type:'arrow'});return e;
}
function board(key,title,state,cue,sequence){b={key,title,state,cue,sequence,elements:[]};boards.push(b);text(title,100,90,1260,46);text(state,102,176,1240,27);text(spec.brand||'INTELLIGENCE FROM ZERO',102,1000,1250,20);return b}
function note(s,y=880,size=29,color=P.ink){text(s,102,y,1250,size,color)}
if(!Array.isArray(spec.slides)||!spec.slides.length)throw new Error('slides must be a nonempty array');
const keys=new Set();
for(const [i,s] of spec.slides.entries()){
 if(!/^[a-z0-9-]+$/.test(s.key)||keys.has(s.key))throw new Error('Slide keys must be unique lowercase slugs');keys.add(s.key);
 board(s.key,s.title,s.state,s.cue||'',String(i+1));const nodes=new Map();
 for(const e of s.elements||[]){
  if(e.type==='text')text(e.text,e.x,e.y,e.width||1250,e.size||32,P[e.color||'ink']);
  else if(e.type==='card')nodes.set(e.id,node(e.text,e.x,e.y,e.width||350,e.height||165,P[e.color||'accent'],e.sub));
  else if(e.type==='arrow'){if(!nodes.has(e.from)||!nodes.has(e.to))throw new Error('Arrow must refer to earlier card IDs');arrow(nodes.get(e.from),nodes.get(e.to),e.route)}
  else throw new Error('Unknown element type '+e.type);
 }
 if(s.note)note(s.note,s.noteY||875,s.noteSize||28);
}
const gen=rough.generator();
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
function color(c,dark){return dark?(DARK[c]||c):c}
function glyph(e,dark){let out=`<g aria-label="${esc(e.text)}" fill="${color(e.strokeColor,dark)}">`;const scale=e.fontSize/font.unitsPerEm;
 for(const [li,line] of e.text.split('\n').entries()){let x=e.x,baseline=e.y+e.fontSize+li*e.fontSize*e.lineHeight;const run=font.layout(line);run.glyphs.forEach((g,i)=>{const p=run.positions[i];out+=`<path d="${g.path.toSVG()}" transform="translate(${x+p.xOffset*scale},${baseline-p.yOffset*scale}) scale(${scale},${-scale})"/>`;x+=p.xAdvance*scale})}return out+'</g>'}
function roughSVG(shape){return gen.toPaths(shape).map(p=>`<path d="${p.d}" stroke="${p.stroke}" stroke-width="${p.strokeWidth}" fill="${p.fill||'none'}" stroke-linecap="round" stroke-linejoin="round"/>`).join('')}
function draw(e,dark){if(e.type==='text')return glyph(e,dark);const opt={seed:e.seed,roughness:e.roughness,stroke:color(e.strokeColor,dark),strokeWidth:e.strokeWidth};
 if(e.type==='rectangle'){const {x,y,width:w,height:h}=e,r=20;return roughSVG(gen.path(`M${x+r} ${y} H${x+w-r} Q${x+w} ${y} ${x+w} ${y+r} V${y+h-r} Q${x+w} ${y+h} ${x+w-r} ${y+h} H${x+r} Q${x} ${y+h} ${x} ${y+h-r} V${y+r} Q${x} ${y} ${x+r} ${y}`,opt))}
 if(e.type==='arrow'){const ps=e.points.map(([x,y])=>[x+e.x,y+e.y]);let out=roughSVG(gen.linearPath(ps,opt));const q=ps.at(-1),p=ps.at(-2),ang=Math.atan2(q[1]-p[1],q[0]-p[0]),l=18;return out+roughSVG(gen.linearPath([[q[0]-l*Math.cos(ang-.42),q[1]-l*Math.sin(ang-.42)],q,[q[0]-l*Math.cos(ang+.42),q[1]-l*Math.sin(ang+.42)]],opt))}return ''}
function scene(elems){return {type:'excalidraw',version:2,source:'https://excalidraw.com',elements:elems,appState:{viewBackgroundColor:'#ffffff',gridSize:null,zoom:{value:.5},scrollX:0,scrollY:0,exportWithDarkMode:true,frameRendering:{enabled:true,name:true,outline:true,clip:true}},files:{}}}
function placed(board,x,y){const id='frame-'+board.key;return [{id,type:'frame',x,y,width:1920,height:1080,angle:0,strokeColor:P.ink,backgroundColor:'transparent',fillStyle:'solid',strokeWidth:1,strokeStyle:'solid',roughness:0,opacity:100,groupIds:[],frameId:null,roundness:null,seed:1,version:1,versionNonce:1,isDeleted:false,boundElements:[],updated:1,link:null,locked:false,name:`${String(board.order).padStart(2,'0')} / ${boards.length} | ${board.title} | ${board.state}`},...board.elements.map(e=>({...e,x:e.x+x,y:e.y+y,frameId:id}))]}
(async()=>{
 for(const dir of ['scenes','svg-dark','svg-light','png-dark','contact-sheets'])fs.mkdirSync(path.join(OUT,dir),{recursive:true});
 const master=[],failures=[];
 boards.forEach((board,i)=>board.order=i+1);
 for(const board of boards){
  const lookup=new Map(board.elements.map(e=>[e.id,e]));
  for(const e of board.elements){if(e.type!=='arrow'&&(e.x<80||e.x+e.width>1382.4||e.y<60||e.y+e.height>1040))failures.push(board.key+' safe area: '+e.id);
   if(e.type==='text'&&e.fontSize<25&&!e.text.includes('INTELLIGENCE FROM ZERO'))failures.push('Small text: '+e.text);
   for(const side of ['startBinding','endBinding'])if(e[side]&&!lookup.get(e[side].elementId)?.boundElements.some(t=>t.id===e.id))failures.push('Broken binding: '+e.id);
  }
  fs.writeFileSync(path.join(OUT,'scenes',board.key+'.excalidraw'),JSON.stringify(scene(placed(board,0,0)),null,2));
  master.push(...placed(board,((board.order-1)%4)*2200,Math.floor((board.order-1)/4)*1320));
  for(const dark of [true,false]){let svg=`<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><title>${esc(board.title+' / '+board.state)}</title><desc>${esc(board.cue)}</desc><rect width="1920" height="1080" fill="${dark?'#111315':'#ffffff'}"/>${board.elements.map(e=>draw(e,dark)).join('')}</svg>`;fs.writeFileSync(path.join(OUT,dark?'svg-dark':'svg-light',board.key+'.svg'),svg);if(dark)await sharp(Buffer.from(svg)).png().toFile(path.join(OUT,'png-dark',board.key+'.png'))}
 }
 fs.writeFileSync(path.join(OUT,'master.excalidraw'),JSON.stringify(scene(master),null,2));
 fs.writeFileSync(path.join(OUT,'boards.json'),JSON.stringify(boards.map(({elements,...b})=>b),null,2));
 fs.writeFileSync(path.join(ROOT,'VIEW-STAGE.html'),fs.readFileSync(path.join(__dirname,'viewer-template.html'),'utf8').replace('__TITLE__',esc(spec.title||'Tutorial')).replaceAll('__OTHER__',esc(spec.otherLabel||'Other section')).replace('__OTHER_URL__',esc(spec.otherUrl||'../')).replace('__BOARDS__',JSON.stringify(boards.map(({elements,...b})=>b)).replaceAll('<','\\u003c')));
 for(let start=0;start<boards.length;start+=6){const items=boards.slice(start,start+6),comps=[];for(let i=0;i<items.length;i++)comps.push({input:await sharp(path.join(OUT,'png-dark',items[i].key+'.png')).resize(640,360).png().toBuffer(),left:(i%2)*660+10,top:Math.floor(i/2)*390+35});await sharp({create:{width:1320,height:Math.ceil(items.length/2)*390+35,channels:4,background:'#343434'}}).composite(comps).png().toFile(path.join(OUT,'contact-sheets',`sheet-${start/6+1}.png`))}
 const ids=master.map(e=>e.id);if(new Set(ids).size!==ids.length)failures.push('Duplicate IDs');
 const qa={boards:boards.length,elements:master.length,handwriting:'Virgil fontFamily 1',safeRightPercent:28,sourcePalette:'Light source for native theme switching; separate dark recording previews.',failures,nativeVerification:'Pending',rendering:'Rough.js + outlined bundled Virgil; native master retains editable text.'};fs.writeFileSync(path.join(OUT,'QA.json'),JSON.stringify(qa,null,2));
 if(failures.length)throw new Error(failures.join('\n'));console.log(JSON.stringify(qa,null,2));
})();
