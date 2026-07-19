// ─── MULTIPLAYER ─────────────────────────────────────────────
let socket=null;
let MP={active:false,roomId:null,playerIndex:null};

window._startOnlineGame=function(){
  if(socket&&MP.roomId)socket.emit("start_game",{room_id:MP.roomId});
};

function toggleMP(){
  const m=document.getElementById("mpMode").value;
  document.getElementById("mpFields").style.display=m==="online"?"block":"none";
  if(m==="online"){
    const s=document.getElementById("mpServer");
    if(!s.value)s.value=window.location.origin;
  }
}

function initMP(serverUrl,roomCode,playerName){
  loadSocketIO(()=>{
    if(!window.io){showToast("Socket.IO unavailable","err");MP.active=false;return;}
    socket=io(serverUrl,{transports:["websocket","polling"]});
    socket.on("connect",()=>showToast("Connected ✓","ok"));
    socket.on("connect_error",()=>{showToast("Cannot connect to server","err");MP.active=false;});
    socket.on("error",d=>showToast("⚠ "+d.msg,"err"));

    socket.on("room_created",d=>{
      MP.roomId=d.room_id;MP.playerIndex=d.player_index;
      showInfo("Room Created",
        "<p style='text-align:center;font-size:12px;color:#8b9099'>Share this code:</p>"+
        "<div style='text-align:center;font-size:40px;font-weight:bold;letter-spacing:10px;color:#c9a227;padding:12px'>"+d.room_id+"</div>"+
        "<p id='waitList' style='font-size:12px;color:#8b9099;text-align:center'>Waiting for players...</p>",
        null,null);
      document.getElementById("infoBtns").innerHTML=
        "<button class='btn primary' onclick='window._startOnlineGame()'>▶ Start Game</button>";
    });

    socket.on("room_joined",d=>{
      MP.roomId=d.room_id;MP.playerIndex=d.player_index;
      showInfo("Joined Room "+d.room_id,
        "<p style='text-align:center;color:#8b9099;font-size:13px'>Waiting for host to start...</p>",
        null,null);
    });

    socket.on("room_update",d=>{
      const el=document.getElementById("waitList");
      if(el)el.innerHTML=d.players.map((p,i)=>
        "<div style='padding:4px 0;font-size:13px'>"+(i===0?"👑 ":"")+p+(i===MP.playerIndex?" (You)":"")+"</div>"
      ).join("");
    });

    socket.on("game_started",d=>{
      document.getElementById("ovInfo").classList.remove("show");
      document.getElementById("ovSetup").classList.remove("show");
      G.players=d.players.map(name=>({name,score:0,hand:[],isAI:false}));
      G.ci=0; G.board=Array.from({length:15},()=>Array(15).fill(null));
      G.bht=false; G.placed=[]; G.hist=[]; G.tn=1;
      buildUI();renderAll();
      showToast(d.first+" goes first!","info");
    });

    socket.on("game_state",d=>{
      if(d.board){
        for(let r=0;r<15;r++)for(let c=0;c<15;c++){
          const cell=d.board[r][c];
          G.board[r][c]=(cell&&cell.symbol)?{symbol:cell.symbol,points:cell.points,type:cell.type}:null;
        }
      }
      if(d.players)d.players.forEach((p,i)=>{if(G.players[i])G.players[i].score=p.score;});
      G.ci=d.current_turn;
      renderBoard();renderSB();
      const pill=document.getElementById("turnPill");
      if(pill)pill.textContent="Turn "+d.turn_number+" — "+G.players[G.ci].name;
      const bag=document.querySelector(".bag-info");
      if(bag)bag.textContent="🎴 "+d.bag_count+" in bag";
    });

    socket.on("your_hand",d=>{
      if(d.player_index===MP.playerIndex&&G.players[d.player_index]){
        G.players[d.player_index].hand=d.hand;
        if(G.ci===MP.playerIndex)renderRack();
      }
    });

    socket.on("your_turn",d=>{
      if(d.player_index===MP.playerIndex){
        G.ci=MP.playerIndex;
        showToast("Your turn!","ok");
        renderAll();
      }
    });

    socket.on("word_played",d=>showToast(d.player+": /"+d.word+"/ +"+d.score+"pts","ok"));
    socket.on("player_passed",d=>showToast(d.player+" passed.","info"));
    socket.on("tiles_replaced",d=>showToast(d.player+" replaced "+d.count+" tile(s).","info"));
    socket.on("turn_skipped",d=>showToast(d.player+"'s turn skipped.","info"));

    socket.on("game_over",d=>{
      const rows=d.final_scores.map((p,i)=>
        "<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #2a2f36;"+(i===0?"color:#c9a227;font-weight:bold":"")+"'>"+
        "<span>"+(i===0?"🥇":i===1?"🥈":"🥉")+" "+p.name+"</span><span>"+p.score+" pts</span></div>"
      ).join("");
      showInfo("🏆 "+d.winner+" Wins!",rows,"New Game",()=>location.reload());
    });

    if(roomCode){
      socket.emit("join_room_game",{name:playerName,room_id:roomCode});
    }else{
      socket.emit("create_room",{name:playerName});
    }
  });
}

// ============================================================
// JEREMI app.js — v2
// Fixes: correct quadrant colours, tile reference panel,
//        less rigid gameplay (hint system, relaxed AI)
// ============================================================

// ─── TILE DATA ───────────────────────────────────────────────
const T = {
  "m":{c:2,p:4,t:"C"},"ɱ":{c:8,p:1,t:"C"},"n":{c:2,p:4,t:"C"},
  "ɲ":{c:6,p:2,t:"C"},"ŋ":{c:4,p:3,t:"C"},"ɴ":{c:8,p:1,t:"C"},
  "ŋm":{c:8,p:1,t:"C"},"p":{c:2,p:4,t:"C"},"b":{c:2,p:4,t:"C"},
  "t":{c:2,p:4,t:"C"},"d":{c:2,p:4,t:"C"},"c":{c:8,p:1,t:"C"},
  "ɟ":{c:8,p:1,t:"C"},"k":{c:2,p:4,t:"C"},"g":{c:2,p:4,t:"C"},
  "q":{c:8,p:1,t:"C"},"ɢ":{c:8,p:1,t:"C"},"ʔ":{c:8,p:1,t:"C"},
  "kp":{c:2,p:4,t:"C"},"gb":{c:4,p:3,t:"C"},"pʼ":{c:8,p:1,t:"C"},
  "tʼ":{c:8,p:1,t:"C"},"cʼ":{c:8,p:1,t:"C"},"kʼ":{c:8,p:1,t:"C"},
  "qʼ":{c:8,p:1,t:"C"},"ʘ":{c:8,p:1,t:"C"},"[":{c:8,p:1,t:"C"},
  "ǃ":{c:8,p:1,t:"C"},"ǂ":{c:8,p:1,t:"C"},"pɸ":{c:8,p:1,t:"C"},
  "bβ":{c:8,p:1,t:"C"},"ts":{c:8,p:1,t:"C"},"dz":{c:8,p:1,t:"C"},
  "tʃ":{c:8,p:1,t:"C"},"dʒ":{c:8,p:1,t:"C"},"kx":{c:8,p:1,t:"C"},
  "gɣ":{c:8,p:1,t:"C"},"ɸ":{c:8,p:1,t:"C"},"β":{c:8,p:1,t:"C"},
  "f":{c:4,p:3,t:"C"},"v":{c:6,p:2,t:"C"},"s":{c:2,p:4,t:"C"},
  "z":{c:6,p:2,t:"C"},"ʃ":{c:6,p:2,t:"C"},"ʒ":{c:8,p:1,t:"C"},
  "ç":{c:8,p:1,t:"C"},"ʝ":{c:8,p:1,t:"C"},"x":{c:8,p:1,t:"C"},
  "ɣ":{c:8,p:1,t:"C"},"χ":{c:8,p:1,t:"C"},"ʁ":{c:8,p:1,t:"C"},
  "ħ":{c:8,p:1,t:"C"},"ʕ":{c:8,p:1,t:"C"},"h":{c:8,p:1,t:"C"},
  "ʋ":{c:8,p:1,t:"C"},"r":{c:4,p:3,t:"C"},"j":{c:2,p:4,t:"C"},
  "w":{c:2,p:4,t:"C"},"l":{c:2,p:4,t:"C"},
  "i":{c:1,p:20,t:"V"},"e":{c:3,p:13,t:"V"},"ɛ":{c:5,p:8,t:"V"},
  "a":{c:1,p:20,t:"V"},"ɔ":{c:1,p:16,t:"V"},"o":{c:3,p:11,t:"V"},
  "u":{c:3,p:14,t:"V"},"ɪ":{c:8,p:2,t:"V"},"ʊ":{c:8,p:3,t:"V"},
  "ʷ":{c:12,p:2,t:"D"},"ʲ":{c:12,p:1,t:"D"},
  "̩":{c:12,p:2,t:"D"},"ˤ":{c:12,p:1,t:"D"},
  "ː":{c:8,p:7,t:"D"},"̃":{c:4,p:14,t:"D"},"ˬ":{c:8,p:3,t:"D"},
};

// ─── BONUS SQUARES ───────────────────────────────────────────
const BONUS = {
  "0,9":"TM","2,7":"TM","7,7":"TM","12,8":"TM","14,5":"TM",
  "12,0":"DS","2,14":"DS","13,1":"TL","1,13":"TL",
  "12,2":"DS","2,12":"DS","11,3":"DL","3,11":"DL",
  "10,4":"DS","4,10":"DS","8,4":"DM","6,10":"DM",
  "9,5":"DL","5,9":"DL","10,6":"DS","4,8":"DS",
  "10,8":"DS","4,6":"DS","9,9":"DM","5,5":"DM",
  "8,10":"DM","6,4":"DM","10,10":"DS","4,4":"DS",
  "11,11":"DL","3,3":"DL","12,12":"DM","2,2":"DM",
  "13,13":"TL","1,1":"TL","14,12":"DM","0,2":"DM",
};
const SR=7, SC=0;

// Quadrant colours — matches physical board exactly:
// upper-left=green, upper-right=blue, lower-left=purple, lower-right=yellow
function quadrant(r,c){
  if(r<=7&&c<=7) return "green";
  if(r<=7&&c>7)  return "blue";
  if(r>7&&c<=7)  return "purple";
  return "yellow";
}
function cellClass(r,c){
  const b=BONUS[`${r},${c}`];
  if(!b) return "";
  if(b==="TM") return "TM";
  return `${b}-${quadrant(r,c)}`;
}

// ─── PHONOLOGY ───────────────────────────────────────────────
const VOWELS=new Set(["i","e","ɛ","a","ɔ","o","u","ɪ","ʊ"]);
const GLIDES=new Set(["j","w"]);
const NASALS=new Set(["m","ɱ","n","ɲ","ŋ","ɴ","ŋm"]);
const ROUNDED=new Set(["u","o","ɔ"]);
const FRONT_V=new Set(["i","e"]);
const PHARYNGS=new Set(["ħ","ʕ"]);
const SYL_NAS=new Set(["m̩","ɱ̩","n̩","ɲ̩","ŋ̩","ŋm̩"]);
const EXT_V=new Set([...VOWELS,"iː","eː","ɛː","aː","ɔː","oː","uː","ĩ","ẽ","ɛ̃","ã","ɔ̃","õ","ũ"]);

function isVL(s){return EXT_V.has(s)||SYL_NAS.has(s);}
function isCons(s){return !isVL(s);}

function splitSyl(syms){
  const sl=[];let i=0;
  while(i<syms.length){
    const s=syms[i];
    if(SYL_NAS.has(s)){sl.push([s]);i++;continue;}
    if(i+2<syms.length&&isCons(s)&&GLIDES.has(syms[i+1])&&isVL(syms[i+2])){sl.push(syms.slice(i,i+3));i+=3;continue;}
    if(i+1<syms.length&&isCons(s)&&isVL(syms[i+1])){sl.push(syms.slice(i,i+2));i+=2;continue;}
    if(isVL(s)){sl.push([s]);i++;continue;}
    return null;
  }
  return sl;
}

function validateWord(tiles){
  const syms=tiles.filter(t=>t.type!=="boundary").map(t=>t.symbol);
  if(!syms.length) return{ok:false,r:"No tiles"};
  const sl=splitSyl(syms);
  if(!sl) return{ok:false,r:`Invalid syllable structure /${syms.join(" ")}/. Only CV, V, CGV.`};
  let root=[...syms];
  if(root[0]==="i"&&root.length>1) root=root.slice(1);
  if(root.length>=2&&root[root.length-2]==="n"&&root[root.length-1]==="ɛ") root=root.slice(0,-2);
  const rs=splitSyl(root);
  if(rs&&rs.length>3) return{ok:false,r:`Root has ${rs.length} syllables (max 3).`};
  if(syms[0]==="i"&&syms.length>1&&VOWELS.has(syms[1])) return{ok:false,r:"Negation [i] only on verbs."};
  for(let i=0;i<syms.length-1;i++){
    const s1=syms[i],s2=syms[i+1];
    if(isCons(s1)&&!SYL_NAS.has(s1)&&isCons(s2)&&!SYL_NAS.has(s2)){
      if(GLIDES.has(s2)&&i+2<syms.length&&isVL(syms[i+2])) continue;
      if(GLIDES.has(s1)&&!isVL(s2)) return{ok:false,r:`Glide /${s1}/ must precede a vowel.`};
      if(!GLIDES.has(s2)) return{ok:false,r:`Illegal cluster /${s1}${s2}/.`};
    }
  }
  return{ok:true};
}

function diacEnv(diac,r,c){
  const adj=[];
  for(const[dr,dc]of[[-1,0],[1,0],[0,-1],[0,1]]){
    const nr=r+dr,nc=c+dc;
    if(nr>=0&&nr<15&&nc>=0&&nc<15&&G.board[nr][nc]?.symbol) adj.push(G.board[nr][nc].symbol);
  }
  const has=set=>adj.some(s=>set.has(s));
  if(diac==="̃")  return has(NASALS)?null:"Needs adjacent nasal.";
  if(diac==="ʷ")  return(has(ROUNDED)||adj.includes("w"))?null:"Needs adjacent rounded vowel /u,o,ɔ/ or /w/.";
  if(diac==="ʲ")  return(has(FRONT_V)||adj.includes("j"))?null:"Needs adjacent /i,e/ or /j/.";
  if(diac==="ˤ")  return has(PHARYNGS)?null:"Needs adjacent /ħ/ or /ʕ/.";
  if(diac==="ˬ")  return adj.some(s=>VOWELS.has(s))?null:"Needs to be between vowels.";
  return null;
}

// ─── SCORING ─────────────────────────────────────────────────
function scoreTiles(tiles,pset){
  const notBnd=tiles.filter(t=>t.type!=="boundary");
  // DS on individual tiles
  for(const t of tiles){
    const b=BONUS[`${t.row},${t.col}`];
    t._s=t.points;
    if(pset.has(`${t.row},${t.col}`)&&b==="DS") t._s*=2;
  }
  // Identify morphemes
  const syms=notBnd.map(t=>t.symbol);
  let s=0,e=notBnd.length;
  const morphs=[];
  if(syms[0]==="i"&&syms.length>1){morphs.push([notBnd[0]]);s=1;}
  const hasSuf=syms.length>=2&&syms[syms.length-2]==="n"&&syms[syms.length-1]==="ɛ";
  if(hasSuf) e=notBnd.length-2;
  morphs.push(notBnd.slice(s,e));
  if(hasSuf) morphs.push(notBnd.slice(-2));
  let total=0;
  for(const m of morphs){
    let ms=m.reduce((a,t)=>a+t._s,0),mm=1;
    for(const t of m){
      const b=BONUS[`${t.row},${t.col}`];
      if(!pset.has(`${t.row},${t.col}`)) continue;
      if(b==="TM"&&mm<3)mm=3;else if(b==="DM"&&mm<2)mm=2;
    }
    total+=ms*mm;
  }
  let wm=1;
  for(const t of tiles){
    const b=BONUS[`${t.row},${t.col}`];
    if(!pset.has(`${t.row},${t.col}`)) continue;
    if(b==="TL"&&wm<3)wm=3;else if(b==="DL"&&wm<2)wm=2;
  }
  return total*wm;
}

function getConn(r,c,dir){
  const tiles=[];
  if(dir==="h"){let col=c;while(col>0&&G.board[r][col-1]?.symbol&&G.board[r][col-1].type!=="boundary")col--;while(col<15&&G.board[r][col]?.symbol&&G.board[r][col].type!=="boundary"){tiles.push({...G.board[r][col],row:r,col});col++;}}
  else{let row=r;while(row>0&&G.board[row-1][c]?.symbol&&G.board[row-1][c].type!=="boundary")row--;while(row<15&&G.board[row][c]?.symbol&&G.board[row][c].type!=="boundary"){tiles.push({...G.board[row][c],row,col:c});row++;}}
  return tiles;
}

function getAllWords(rp){
  if(!rp.length) return[];
  const rows=rp.map(p=>p.row),cols=rp.map(p=>p.col);
  let md,cd;
  if(rp.length===1){md="h";cd="v";}
  else if(new Set(rows).size===1){md="h";cd="v";}
  else{md="v";cd="h";}
  const words=[];
  const mw=md==="h"?getConn(rows[0],Math.min(...cols),"h"):getConn(Math.min(...rows),cols[0],"v");
  if(mw.length>1)words.push(mw);
  else if(rp.length===1){
    const v=getConn(rp[0].row,rp[0].col,"v"),h=getConn(rp[0].row,rp[0].col,"h");
    if(v.length>1)words.push(v);if(h.length>1)words.push(h);return words;
  }
  const seen=new Set();
  for(const p of rp){
    const cw=getConn(p.row,p.col,cd);
    if(cw.length>1){const key=`${cw[0].row},${cw[0].col}|${cw[cw.length-1].row},${cw[cw.length-1].col}`;if(!seen.has(key)){seen.add(key);words.push(cw);}}
  }
  return words;
}

// ─── GAME STATE ───────────────────────────────────────────────
let G={board:null,bag:[],players:[],ci:0,tn:1,hist:[],bht:false,placed:[],si:-1,dragIdx:-1,repSel:[],blankIdx:-1};

function buildBag(){
  const bag=[];
  for(const[sym,info]of Object.entries(T))for(let i=0;i<info.c;i++)bag.push({symbol:sym,points:info.p,type:info.t});
  for(let i=0;i<6;i++)bag.push({symbol:null,points:0,type:"blank"});
  return shuffle(bag);
}

function drawTiles(n,initial=false){
  const hand=[];
  if(initial&&G.bag.length>=9){
    const pickType=type=>{const idx=G.bag.reduce((a,t,i)=>t.type===type?[...a,i]:a,[]);const ci=idx[~~(Math.random()*idx.length)];return G.bag.splice(ci,1)[0];};
    for(let i=0;i<3;i++)hand.push(pickType("V"));
    for(let i=0;i<2;i++)hand.push(pickType("C"));
    while(hand.length<9&&G.bag.length)hand.push(G.bag.splice(~~(Math.random()*G.bag.length),1)[0]);
  }else{
    for(let i=0;i<n&&G.bag.length;i++)hand.push(G.bag.splice(~~(Math.random()*G.bag.length),1)[0]);
  }
  return shuffle(hand);
}

// ─── AI ──────────────────────────────────────────────────────
function aiTurn(){
  const p=G.players[G.ci];
  showToast(`🤖 ${p.name} thinking...`,"info");
  setTimeout(()=>{
    const move=findMove(p);
    if(!move){
      // AI tries replacing tiles before passing
      if(G.bag.length>=3){
        const vowels=p.hand.filter(t=>t.type==="V");
        const toRep=vowels.length<2?p.hand.filter(t=>t.type==="C").slice(0,3):[];
        if(toRep.length){
          const idxs=toRep.map(t=>p.hand.indexOf(t)).sort((a,b)=>b-a);
          const removed=idxs.map(i=>p.hand.splice(i,1)[0]);
          p.hand.push(...drawTiles(removed.length));
          G.bag.push(...removed);shuffle(G.bag);
          G.hist.push({tn:G.tn,player:p.name,word:"replaced",score:""});
          showToast(`🤖 ${p.name} replaces tiles.`,"info");
          advanceTurn();return;
        }
      }
      G.hist.push({tn:G.tn,player:p.name,word:"pass",score:""});
      showToast(`🤖 ${p.name} passes.`,"info");
      advanceTurn();return;
    }
    execMove(p,move);
    p.score+=move.score;
    G.bht=true;
    const ws=move.word.join("");
    G.hist.push({tn:G.tn,player:p.name,word:ws,score:move.score});
    const needed=9-p.hand.length;
    if(needed>0)p.hand.push(...drawTiles(needed));
    showToast(`🤖 ${p.name}: /${ws}/ +${move.score}pts`,"ok");
    advanceTurn();
  },600);
}

function execMove(player,move){
  let r=move.sr,c=move.sc;
  const dr=move.dir==="v"?1:0,dc=move.dir==="h"?1:0;
  const hand=[...player.hand];
  for(const sym of move.word){
    if(!G.board[r][c]){
      let idx=hand.findIndex(t=>t.symbol===sym);
      let tile;
      if(idx>=0){tile=hand.splice(idx,1)[0];}
      else{const bi=hand.findIndex(t=>t.type==="blank");if(bi>=0){tile={...hand.splice(bi,1)[0],symbol:sym,type:T[sym]?.t||"C",points:0};}}
      if(tile)G.board[r][c]={symbol:sym,points:tile.points,type:tile.type};
    }
    r+=dr;c+=dc;
  }
  player.hand=hand;
}

function findMove(player){
  const diff=player.difficulty||"medium";
  const cands=genCands(player.hand);
  const anchors=getAnchors();
  const all=[];
  const maxC=diff==="soft"?60:diff==="medium"?200:cands.length;
  for(const word of cands.slice(0,maxC)){
    for(const[ar,ac]of anchors){
      for(const dir of["h","v"]){
        const dr=dir==="v"?1:0,dc=dir==="h"?1:0;
        for(let off=0;off<word.length;off++){
          const sr=ar-off*dr,sc=ac-off*dc;
          const score=simScore(word,sr,sc,dir,player.hand);
          if(score>0)all.push({word,sr,sc,dir,score});
        }
      }
    }
    if(all.length>1000)break;
  }
  if(!all.length)return null;
  all.sort((a,b)=>b.score-a.score);
  if(diff==="soft"){const pool=all.slice(Math.max(0,Math.floor(all.length*.5)));return pool[~~(Math.random()*pool.length)];}
  if(diff==="medium"){const pool=all.slice(0,Math.max(1,Math.floor(all.length*.4)));return pool[~~(Math.random()*pool.length)];}
  const best=all[0].score;
  const top=all.filter(m=>m.score>=best*.9);
  return top[~~(Math.random()*top.length)];
}

function genCands(hand){
  const base=hand.filter(t=>t.symbol&&t.type!=="D"&&t.type!=="blank");
  const blanks=hand.filter(t=>t.type==="blank").length;
  const syms=base.map(t=>t.symbol);
  // Blanks become best vowel available
  const blankOpts=["a","e","i","o","u","ɛ","ɔ"];
  const pools=[syms];
  for(let b=0;b<blanks;b++) pools.forEach((_,i,arr)=>{
    blankOpts.forEach(v=>{const ns=[...arr[i],v];if(!arr.some(a=>a.join()===ns.join()))arr.push(ns);});
  });
  const cands=new Set();
  for(const pool of pools.slice(0,5)){
    for(let len=2;len<=Math.min(9,pool.length);len++){
      for(const perm of perms(pool,len)){
        const base2=perm.map(s=>s.length>1?s.normalize("NFD")[0]:s);
        if(validStruct(base2))cands.add(perm.join("|"));
      }
      if(cands.size>600)break;
    }
    if(cands.size>600)break;
  }
  return shuffle([...cands].map(s=>s.split("|")));
}

function validStruct(syms){
  let root=[...syms];
  if(root[0]==="i"&&root.length>1)root=root.slice(1);
  if(root.length>=2&&root[root.length-2]==="n"&&root[root.length-1]==="ɛ")root=root.slice(0,-2);
  if(!root.length)return false;
  const sl=splitSyl(root);
  return sl!==null&&sl.length<=3;
}

function*perms(arr,len){
  if(len===1){for(const x of arr)yield[x];return;}
  for(let i=0;i<arr.length;i++){const rest=[...arr.slice(0,i),...arr.slice(i+1)];for(const p of perms(rest,len-1))yield[arr[i],...p];}
}

function getAnchors(){
  if(!G.bht)return[[SR,SC]];
  const a=[];
  for(let r=0;r<15;r++)for(let c=0;c<15;c++){
    if(G.board[r][c])continue;
    for(const[dr,dc]of[[-1,0],[1,0],[0,-1],[0,1]]){
      const nr=r+dr,nc=c+dc;
      if(nr>=0&&nr<15&&nc>=0&&nc<15&&G.board[nr][nc]?.symbol&&G.board[nr][nc].type!=="boundary"){a.push([r,c]);break;}
    }
  }
  return shuffle(a);
}

function simScore(word,sr,sc,dir,hand){
  const dr=dir==="v"?1:0,dc=dir==="h"?1:0;
  const er=sr+dr*(word.length-1),ec=sc+dc*(word.length-1);
  if(sr<0||sc<0||er>14||ec>14)return -1;
  const hc=[...hand];const np=[];
  let r=sr,c=sc;
  for(const sym of word){
    const cell=G.board[r][c];
    if(cell?.symbol){if(cell.symbol!==sym)return -1;}
    else{
      const info=T[sym];if(!info)return -1;
      const ti=hc.findIndex(t=>t.symbol===sym);
      if(ti>=0)hc.splice(ti,1);
      else{const bi=hc.findIndex(t=>t.type==="blank");if(bi>=0)hc.splice(bi,1);else return -1;}
      np.push({row:r,col:c,sym,points:info.p});
    }
    r+=dr;c+=dc;
  }
  if(!np.length)return -1;
  if(!G.bht&&!np.some(p=>p.row===SR&&p.col===SC))return -1;
  if(G.bht){
    const ps=new Set(np.map(p=>`${p.row},${p.col}`));
    let con=false;
    for(const p of np){for(const[dr2,dc2]of[[-1,0],[1,0],[0,-1],[0,1]]){const nr=p.row+dr2,nc=p.col+dc2;if(nr>=0&&nr<15&&nc>=0&&nc<15&&!ps.has(`${nr},${nc}`)&&G.board[nr][nc]?.symbol){con=true;break;}}if(con)break;}
    if(!con)return -1;
  }
  // Validate
  const tb=G.board.map(row=>[...row]);
  for(const p of np)tb[p.row][p.col]={symbol:p.sym,points:p.points,type:T[p.sym]?.t||"C"};
  const pset=new Set(np.map(p=>`${p.row},${p.col}`));
  const words=getAllWordsOn(tb,np,dir);
  for(const wt of words){const res=validateWord(wt);if(!res.ok)return -1;}
  return words.reduce((s,wt)=>s+scoreTiles(wt,pset),0)+(np.length===9?30:0);
}

function getAllWordsOn(board,np,dir){
  if(!np.length)return[];
  const rows=np.map(p=>p.row),cols=np.map(p=>p.col);
  const md=dir==="h"?"h":"v",cd=dir==="h"?"v":"h";
  const getC=(r,c,d)=>{const tiles=[];if(d==="h"){let col=c;while(col>0&&board[r][col-1]?.symbol&&board[r][col-1].type!=="boundary")col--;while(col<15&&board[r][col]?.symbol&&board[r][col].type!=="boundary"){tiles.push({...board[r][col],row:r,col});col++;}}else{let row=r;while(row>0&&board[row-1][c]?.symbol&&board[row-1][c].type!=="boundary")row--;while(row<15&&board[row][c]?.symbol&&board[row][c].type!=="boundary"){tiles.push({...board[row][c],row,col:c});row++;}}return tiles;};
  const words=[];
  const mw=md==="h"?getC(rows[0],Math.min(...cols),"h"):getC(Math.min(...rows),cols[0],"v");
  if(mw.length>1)words.push(mw);
  const seen=new Set();
  for(const p of np){const cw=getC(p.row,p.col,cd);if(cw.length>1){const key=`${cw[0].row},${cw[0].col}|${cw[cw.length-1].row},${cw[cw.length-1].col}`;if(!seen.has(key)){seen.add(key);words.push(cw);}}}
  return words;
}

// ─── SETUP ───────────────────────────────────────────────────
function updateFields(){
  const n=+document.getElementById("numPlayers").value;
  document.getElementById("playerFields").innerHTML=
    Array.from({length:n},(_,i)=>`<div class="setup-field"><label>Player ${i+1} Name</label><input type="text" id="pn${i}" value="Player ${i+1}"></div>`).join("");
}

function startGame(){
  const mode=document.getElementById("mpMode")?.value||"local";
  if(mode==="online"){
    const serverUrl=document.getElementById("mpServer").value.trim()||window.location.origin;
    const roomCode=document.getElementById("mpRoom").value.trim().toUpperCase();
    const name=document.getElementById("pn0")?.value.trim()||"Player 1";
    MP.active=true;
    initMP(serverUrl,roomCode,name);
    return;
  }
  const n=+document.getElementById("numPlayers").value;
  const aiDiff=document.getElementById("aiDiff").value;
  const players=[];
  for(let i=0;i<n;i++){
    const name=document.getElementById(`pn${i}`)?.value.trim()||`Player ${i+1}`;
    const isAI=aiDiff!=="none"&&i===n-1;
    players.push({name:isAI?"JEREMI-AI":name,hand:[],score:0,isAI,difficulty:aiDiff,skipNext:false});
  }
  G.bag=buildBag();G.board=Array.from({length:15},()=>Array(15).fill(null));
  G.players=players;G.ci=0;G.tn=1;G.hist=[];G.bht=false;G.placed=[];G.si=-1;
  for(const p of G.players)p.hand=drawTiles(9,true);
  // Draw for first
  const draws=G.players.map((p,i)=>{const bi=~~(Math.random()*G.bag.length);return{pi:i,name:p.name,tile:G.bag[bi]};}).sort((a,b)=>b.tile.points-a.tile.points);
  G.ci=draws[0].pi;
  const drawHtml=draws.map(d=>`<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2a2f36;font-size:13px"><span>${d.name}</span><span style="color:#c9a227;font-weight:bold">${d.tile.symbol||"BLANK"} (${d.tile.points}pts)</span></div>`).join("")+`<div style="text-align:center;margin-top:10px;color:#3fae3f;font-weight:bold">${draws[0].name} goes first!</div>`;
  showInfo("Draw for First Player",drawHtml,"Start!",()=>{
    document.getElementById("ovSetup").classList.remove("show");
    buildUI();renderAll();
    if(G.players[G.ci].isAI)aiTurn();
  });
}

// ─── BUILD UI ─────────────────────────────────────────────────
function buildUI(){
  const app=document.getElementById("app");
  app.innerHTML=`
    <div class="topbar">
      <div class="brand">JEREMI</div>
      <div class="turn-pill" id="turnPill">Turn 1</div>
      <div class="topbar-actions">
        <button onclick="showHist()">📜 History</button>
        <button onclick="saveGame()">💾 Save</button>
        <button onclick="showInsights()">🧠 AI</button>
      </div>
    </div>
    <div class="main-layout">
      <div class="scoreboard" id="sb"></div>
      <div class="board-outer">
        <div class="jeremi-side">JEREMI</div>
        <div class="board" id="board"></div>
        <div class="tile-ref" id="tileRef"></div>
      </div>
      <div class="word-log" id="wlog"><h3>Word Log</h3><div id="logEntries"></div></div>
    </div>
    <div class="rack-area">
      <div class="rack-label" id="rackLbl">Your Rack</div>
      <div class="rack" id="rack" ondragover="event.preventDefault()" ondrop="dropToRack(event)"></div>
      <div class="action-row">
        <button class="btn primary" onclick="confirmPlay()">✓ Done</button>
        <button class="btn" onclick="undoLast()">↩ Undo</button>
        <button class="btn" onclick="placeBoundary()"># Bnd</button>
        <button class="btn" onclick="doPass()">Pass</button>
        <button class="btn" onclick="openReplace()">Replace</button>
        <button class="btn" onclick="showHint()" style="color:#c9a227">💡 Hint</button>
      </div>
    </div>`;
  buildTileRef();
}

// ─── TILE REFERENCE PANEL ────────────────────────────────────
function buildTileRef(){
  const el=document.getElementById("tileRef");
  if(!el)return;
  const cons=Object.entries(T).filter(([,i])=>i.t==="C");
  const vows=Object.entries(T).filter(([,i])=>i.t==="V");
  const dias=Object.entries(T).filter(([,i])=>i.t==="D");

  const cs=`border:1px solid #4a8a96;padding:0 4px;text-align:center;font-size:9px;color:#0a1a22;background:#bfe3ea;line-height:12px;`;
  const title=`color:#7a1f3d;font-family:Georgia,serif;font-weight:bold;font-size:11px;margin:4px 0 2px`;

  // Consonants in 2 columns
  const half=Math.ceil(cons.length/2);
  const L=cons.slice(0,half),R=cons.slice(half);
  let rows="";
  for(let i=0;i<half;i++){
    const [ls,li]=L[i]||["",""];
    const [rs,ri]=R[i]||["",""];
    rows+=`<tr><td class="sym" style="${cs}font-weight:bold">${ls}</td><td style="${cs}">${li.c||""}</td>${rs?`<td class="sym" style="${cs}font-weight:bold">${rs}</td><td style="${cs}">${ri.c||""}</td>`:`<td style="${cs}"></td><td style="${cs}"></td>`}</tr>`;
  }

  // Vowels single row
  let vrow=`<tr>${vows.map(([s,i])=>`<td class="sym" style="${cs}font-weight:bold">${s}</td><td style="${cs}">${i.c}</td>`).join("")}</tr>`;

  // Diacritics 4 per row
  let drows="";
  for(let i=0;i<dias.length;i+=4){
    drows+=`<tr>${dias.slice(i,i+4).map(([s,info])=>`<td class="sym" style="${cs}font-weight:bold">${s}</td><td style="${cs}">${info.c}</td>`).join("")}</tr>`;
  }

  el.innerHTML=`
    <div class="ref-title" style="${title}">CONSONANTS</div>
    <table>${rows}</table>
    <div class="ref-title" style="${title}">VOWELS</div>
    <table><tr>${vows.map(([s,i])=>`<td class="sym" style="${cs}font-weight:bold">${s}</td><td style="${cs}">${i.c}</td>`).join("")}</tr></table>
    <div class="ref-title" style="${title}">DIACRITICS</div>
    <table>${drows}</table>`;

  // Size to match board height
  const boardH=15*32;
  el.style.height=boardH+"px";
}

// ─── RENDER ──────────────────────────────────────────────────
function renderAll(){
  if(!G.board)return;
  renderBoard();renderRack();renderSB();renderLog();
  const p=G.players[G.ci];
  const pl=document.getElementById("turnPill");
  if(pl)pl.textContent=`Turn ${G.tn} — ${p.name}`;
  const rl=document.getElementById("rackLbl");
  if(rl)rl.textContent=`${p.name}'s Rack`;
}

function renderBoard(){
  const el=document.getElementById("board");if(!el)return;el.innerHTML="";
  const selTile=G.si>=0?G.players[G.ci].hand[G.si]:null;
  const pset=new Set(G.placed.filter(p=>!p.isDiac&&!p.isBnd).map(p=>`${p.row},${p.col}`));

  for(let r=0;r<15;r++)for(let c=0;c<15;c++){
    const div=document.createElement("div");
    div.className="cell";
    const bc=G.board[r][c];
    const isStart=r===SR&&c===SC;

    if(bc?.symbol){
      div.classList.add("placed");
      if(pset.has(`${r},${c}`))div.classList.add("placed-now");
      const bt=document.createElement("div");
      bt.className="board-tile locked";bt.textContent=bc.symbol;
      const pb=document.createElement("span");pb.className="pb";pb.textContent=bc.points;
      bt.appendChild(pb);div.appendChild(bt);
    } else if(isStart){
      div.classList.add("start");
      div.style.background=`conic-gradient(from 315deg at 50% 50%,#3fae3f 0deg 90deg,#4d8fd1 90deg 180deg,#d4c736 180deg 270deg,#9b4fb0 270deg 360deg)`;
    } else {
      const cc=cellClass(r,c);
      if(cc)div.classList.add(cc);
      if(cc)div.textContent=cc.split("-")[0]; // show bonus label
      // Drop highlights
      if(selTile){
        if(selTile.type!=="D"&&(!bc||!bc.symbol))div.classList.add("drop-ok");
        if(selTile.type==="D"&&bc?.symbol)div.classList.add("drop-diac");
      }
    }

    div.addEventListener("click",()=>onCell(r,c));
    div.addEventListener("dragover",e=>{
      e.preventDefault();e.stopPropagation();
      const st=G.dragIdx>=0?G.players[G.ci].hand[G.dragIdx]:null;
      if(st){
        const bc=G.board[r][c];
        if(st.type==="D"&&bc&&bc.symbol)div.classList.add("drop-diac");
        else if(st.type!=="D"&&!(bc&&bc.symbol))div.classList.add("drop-ok");
      }
    });
    div.addEventListener("dragleave",e=>{
      if(!div.contains(e.relatedTarget))div.classList.remove("drop-ok","drop-diac");
    });
    div.addEventListener("drop",e=>{
      e.preventDefault();
      div.classList.remove("drop-ok","drop-diac");
      if(G.dragIdx>=0){G.si=G.dragIdx;onCell(r,c);G.dragIdx=-1;}
    });
    el.appendChild(div);
  }
}

function renderRack(){
  const el=document.getElementById("rack");if(!el)return;el.innerHTML="";
  const hand=G.players[G.ci].hand;
  const myTurn=!G.players[G.ci].isAI;
  for(let i=0;i<hand.length;i++){
    const tile=hand[i];
    const div=document.createElement("div");
    div.className="rack-tile";
    if(tile.type==="D")div.classList.add("diac");
    if(tile.type==="blank")div.classList.add("blank");
    if(i===G.si)div.classList.add("sel");
    div.textContent=tile.symbol||"?";
    const pb=document.createElement("span");pb.className="pb";pb.textContent=tile.points;
    div.appendChild(pb);
    if(myTurn){
      div.draggable=true;
      div.addEventListener("dragstart",e=>{
        G.dragIdx=i;G.si=i;div.classList.add("drag");
        e.dataTransfer.effectAllowed="move";
        e.dataTransfer.setData("text/plain",String(i));
      });
      div.addEventListener("dragend",()=>{
        div.classList.remove("drag");
        document.querySelectorAll(".drop-ok,.drop-diac").forEach(el=>el.classList.remove("drop-ok","drop-diac"));
        G.dragIdx=-1;
      });
      div.addEventListener("click",()=>onTile(i));
    }
    el.appendChild(div);
  }
}

function renderSB(){
  const el=document.getElementById("sb");if(!el)return;
  el.innerHTML=`<h3>Scores</h3>`+G.players.map((p,i)=>`
    <div class="score-row ${i===G.ci?"active":""}">
      <span>${p.name}${p.isAI?" 🤖":""}</span>
      <span class="pts">${p.score}</span>
    </div>`).join("")+`<div class="bag-info">🎴 ${G.bag.length} in bag</div>`;
}

function renderLog(){
  const el=document.getElementById("logEntries");if(!el)return;
  const entries=[...G.hist].reverse().slice(0,15);
  el.innerHTML=entries.length?entries.map(h=>`
    <div class="log-entry">
      <div class="log-word">/${h.word}/</div>
      <div class="log-meta">${h.player} · T${h.tn}${h.score?" · +"+h.score+"pts":""}</div>
    </div>`).join(""):`<div style="color:var(--muted);font-size:11px;padding:6px">No words yet</div>`;
}

// ─── INTERACTION ─────────────────────────────────────────────
function onTile(idx){
  if(G.players[G.ci].isAI)return;
  if(G.si===idx){G.si=-1;renderBoard();renderRack();return;}
  const tile=G.players[G.ci].hand[idx];
  if(!tile)return;
  if(tile.type==="blank"&&!tile.symbol){G.si=idx;G.blankIdx=idx;openBlank();return;}
  G.si=idx;renderBoard();renderRack();
}

function onCell(r,c){
  if(G.players[G.ci].isAI)return;
  if(G.si<0){showToast("Select a tile first.","err");return;}
  const hand=G.players[G.ci].hand;
  const tile=hand[G.si];if(!tile)return;
  const bc=G.board[r][c];

  // DIACRITIC
  if(tile.type==="D"){
    if(!bc?.symbol){showToast("Tap an existing tile.","err");return;}
    const envErr=diacEnv(tile.symbol,r,c);
    if(envErr){showToast(envErr,"err");return;}
    const prev={sym:bc.symbol,pts:bc.points};
    G.board[r][c]={...bc,symbol:bc.symbol+tile.symbol,points:bc.points+tile.points,diac:tile.symbol};
    G.placed.push({row:r,col:c,isDiac:true,isBnd:false,prevSym:prev.sym,prevPts:prev.pts,tile:{...tile},hi:G.si});
    hand.splice(G.si,1);G.si=-1;
    showToast(`Applied → ${bc.symbol}${tile.symbol}`,"ok");
    renderAll();return;
  }

  // BASE TILE
  if(bc?.symbol){showToast("Square occupied.","err");return;}
  const rp=G.placed.filter(p=>!p.isDiac&&!p.isBnd);
  if(!G.bht&&rp.length===0&&r!==SR){showToast("First tile must be on row 8 (★).","err");return;}
  if(rp.length>=1){
    const rows=rp.map(p=>p.row),cols=rp.map(p=>p.col);
    if(rp.length===1){if(r!==rows[0]&&c!==cols[0]){showToast("Tiles must be in a line.","err");return;}}
    else{
      const sR=rows.every(v=>v===rows[0]),sC=cols.every(v=>v===cols[0]);
      if(sR&&r!==rows[0]){showToast(`All on row ${rows[0]+1}.`,"err");return;}
      if(sC&&c!==cols[0]){showToast(`All on col ${cols[0]+1}.`,"err");return;}
    }
  }
  G.board[r][c]={symbol:tile.symbol,points:tile.points,type:tile.type};
  G.placed.push({row:r,col:c,isDiac:false,isBnd:false,tile:{...tile},hi:G.si});
  hand.splice(G.si,1);G.si=-1;renderAll();
}

function dropToRack(e){e.preventDefault();if(G.dragIdx>=0){undoLast();G.dragIdx=-1;}}

function undoLast(){
  if(!G.placed.length){showToast("Nothing to undo.");return;}
  const last=G.placed.pop();
  const hand=G.players[G.ci].hand;
  if(last.isDiac){
    G.board[last.row][last.col].symbol=last.prevSym;
    G.board[last.row][last.col].points=last.prevPts;
    delete G.board[last.row][last.col].diac;
    hand.splice(last.hi,0,last.tile);
  }else if(!last.isBnd){G.board[last.row][last.col]=null;hand.splice(last.hi,0,last.tile);}
  else G.board[last.row][last.col]=null;
  G.si=-1;renderAll();
}

// ─── HINT SYSTEM ─────────────────────────────────────────────
function showHint(){
  if(G.players[G.ci].isAI)return;
  showToast("Finding a move...","info");
  setTimeout(()=>{
    const p=G.players[G.ci];
    const move=findMove({...p,difficulty:"medium"});
    if(!move){showToast("No valid moves found. Try replacing tiles.","info");return;}
    const ws=move.word.join("");
    showInfo("💡 Hint",`<div style="font-size:14px;line-height:1.8">
      <div>Try playing: <b style="color:#c9a227">/${ws}/</b></div>
      <div>Position: Row ${move.sr+1}, Col ${move.sc+1} going ${move.dir==="h"?"→ horizontal":"↓ vertical"}</div>
      <div>Estimated score: <b style="color:#c9a227">+${move.score} pts</b></div>
      <div style="color:#8b9099;font-size:12px;margin-top:8px">This is a suggestion — you can play anything valid!</div>
    </div>`,"OK",null);
  },400);
}

// ─── CONFIRM PLAY ─────────────────────────────────────────────
function confirmPlay(){
  if(G.players[G.ci].isAI)return;
  const rp=G.placed.filter(p=>!p.isDiac&&!p.isBnd);
  if(!rp.length){showToast("Place at least one tile.","err");return;}

  if(!G.bht&&!rp.some(p=>p.row===SR&&p.col===SC)){showToast("First word must cover ★ (R8 C1).","err");return;}

  if(G.bht){
    const ps=new Set(rp.map(p=>`${p.row},${p.col}`));
    let con=false;
    for(const p of rp){for(const[dr,dc]of[[-1,0],[1,0],[0,-1],[0,1]]){const nr=p.row+dr,nc=p.col+dc;if(nr>=0&&nr<15&&nc>=0&&nc<15&&!ps.has(`${nr},${nc}`)&&G.board[nr][nc]?.symbol){con=true;break;}}if(con)break;}
    if(!con){showToast("Word must connect to existing tiles.","err");return;}
  }

  if(rp.length>1){
    const rows=rp.map(p=>p.row),cols=rp.map(p=>p.col);
    if(new Set(rows).size===1){for(let c2=Math.min(...cols);c2<=Math.max(...cols);c2++){if(!G.board[rows[0]][c2]){showToast("Gap between tiles.","err");return;}}}
    else{for(let r2=Math.min(...rows);r2<=Math.max(...rows);r2++){if(!G.board[r2][cols[0]]){showToast("Gap between tiles.","err");return;}}}
  }

  const words=getAllWords(rp);
  if(!words.length){showToast("No word formed.","err");return;}
  for(const wt of words){const res=validateWord(wt);if(!res.ok){rollback();showToast(`❌ ${res.r}`,"err");return;}}

  const pset=new Set(rp.map(p=>`${p.row},${p.col}`));
  let total=words.reduce((s,wt)=>s+scoreTiles(wt,pset),0);
  if(rp.length===9)total+=30;
  const ws=words[0].filter(t=>t.type!=="boundary").map(t=>t.symbol).join("");
  const ni=(G.ci+1)%G.players.length;

  if(G.players[ni].isAI){finalise(ws,total,pset);return;}

  showInfo("Challenge?",`
    <div style="text-align:center;font-size:22px;font-weight:bold;color:#c9a227;padding:8px 0">/${ws}/</div>
    <div style="text-align:center;font-size:26px;font-weight:bold">${total} pts${rp.length===9?" (+30)":""}</div>
    <p style="color:#8b9099;font-size:12px;margin-top:6px">${G.players[ni].name}: challenge or accept?</p>`,
    null,null);
  document.getElementById("infoBtns").innerHTML=`
    <button class="btn" style="background:#a33;color:#fff" onclick="doChallenge(true)">✗ Challenge</button>
    <button class="btn primary" onclick="doChallenge(false)">✓ Accept</button>`;
  window._pp={ws,total,pset};
}

function doChallenge(ch){
  document.getElementById("ovInfo").classList.remove("show");
  if(ch){rollback();showToast("Challenge upheld — word withdrawn.","info");}
  else{const{ws,total,pset}=window._pp;finalise(ws,total,pset);}
}

function finalise(ws,total,pset){
  if(MP.active&&socket){
    socket.emit("submit_word",{room_id:MP.roomId,player_index:MP.playerIndex});
    G.placed=[];
    return;
  }
  G.players[G.ci].score+=total;G.bht=true;
  G.hist.push({tn:G.tn,player:G.players[G.ci].name,word:ws,score:total});
  const needed=9-G.players[G.ci].hand.length;
  if(needed>0)G.players[G.ci].hand.push(...drawTiles(needed));
  G.placed=[];showToast(`+${total} pts ✓`,"ok");advanceTurn();
}

function rollback(){
  for(let i=G.placed.length-1;i>=0;i--){
    const p=G.placed[i];
    if(p.isDiac){G.board[p.row][p.col].symbol=p.prevSym;G.board[p.row][p.col].points=p.prevPts;delete G.board[p.row][p.col].diac;G.players[G.ci].hand.push(p.tile);}
    else if(!p.isBnd){G.board[p.row][p.col]=null;G.players[G.ci].hand.push(p.tile);}
    else G.board[p.row][p.col]=null;
  }
  G.placed=[];
}

function doPass(){
  if(G.players[G.ci].isAI)return;
  if(G.placed.length){showToast("Undo tiles first.","err");return;}
  if(MP.active&&socket){
    socket.emit("pass_turn",{room_id:MP.roomId,player_index:MP.playerIndex});
    return;
  }
  G.hist.push({tn:G.tn,player:G.players[G.ci].name,word:"pass",score:""});
  advanceTurn();
}

function openReplace(){
  if(G.players[G.ci].isAI)return;
  if(G.placed.length){showToast("Undo tiles first.","err");return;}
  G.repSel=[];
  const hand=G.players[G.ci].hand;
  const rackHtml=`<div style="display:flex;gap:6px;flex-wrap:wrap;margin:8px 0">${hand.map((t,i)=>`<div id="rt${i}" class="rack-tile${t.type==="D"?" diac":""}${t.type==="blank"?" blank":""}" onclick="togRep(${i})" style="cursor:pointer">${t.symbol||"?"}<span class="pb">${t.points}</span></div>`).join("")}</div>`;
  showInfo("Replace Tiles","<p style='color:var(--muted);font-size:12px'>Tap tiles to select.</p>"+rackHtml,null,null);
  document.getElementById("infoBtns").innerHTML=`
    <button class="btn primary" onclick="confReplace()">Replace</button>
    <button class="btn" onclick="document.getElementById('ovInfo').classList.remove('show')">Cancel</button>`;
}

function togRep(i){
  const el=document.getElementById(`rt${i}`);
  if(G.repSel.includes(i)){G.repSel=G.repSel.filter(x=>x!==i);el.classList.remove("sel");}
  else{G.repSel.push(i);el.classList.add("sel");}
}

function confReplace(){
  if(!G.repSel.length){showToast("Select tiles.","err");return;}
  document.getElementById("ovInfo").classList.remove("show");
  const hand=G.players[G.ci].hand;
  const idxs=[...G.repSel].sort((a,b)=>b-a);
  const removed=idxs.map(i=>hand.splice(i,1)[0]);
  hand.push(...drawTiles(removed.length));
  G.bag.push(...removed);shuffle(G.bag);
  G.hist.push({tn:G.tn,player:G.players[G.ci].name,word:"replaced",score:""});
  advanceTurn();
}

function placeBoundary(){
  if(G.players[G.ci].isAI)return;
  const r=+prompt("Boundary [#] at row (1-15):")-1;
  const c=+prompt("Boundary [#] at col (1-15):")-1;
  if(isNaN(r)||isNaN(c)||r<0||r>14||c<0||c>14){showToast("Invalid.","err");return;}
  if(G.board[r][c]){showToast("Occupied.","err");return;}
  G.board[r][c]={symbol:"#",points:0,type:"boundary"};
  G.placed.push({row:r,col:c,isDiac:false,isBnd:true,tile:{symbol:"#",points:0,type:"boundary"},hi:-1});
  renderAll();showToast(`[#] at R${r+1} C${c+1}`,"ok");
}

function advanceTurn(){
  G.placed=[];G.si=-1;G.tn++;
  let next=(G.ci+1)%G.players.length,att=0;
  while(G.players[next].skipNext&&att<G.players.length){G.players[next].skipNext=false;next=(next+1)%G.players.length;att++;}
  G.ci=next;
  if(checkEnd()){endGame();return;}
  renderAll();
  if(G.players[G.ci].isAI)aiTurn();
}

function checkEnd(){
  if(!G.bag.length&&G.players.some(p=>p.hand.length===0))return true;
  const recent=G.hist.slice(-G.players.length*2);
  if(recent.length>=G.players.length*2&&recent.every(h=>h.word==="pass"))return true;
  return false;
}

function endGame(){
  let fin=G.players.find(p=>p.hand.length===0)||null,lv=0;
  for(const p of G.players){if(p.hand.length){const l=p.hand.reduce((s,t)=>s+t.points,0);p.score-=l;lv+=l;}}
  if(fin)fin.score+=lv;
  const sorted=[...G.players].sort((a,b)=>b.score-a.score);
  showInfo(`🏆 ${sorted[0].name} Wins!`,
    sorted.map((p,i)=>`<div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #2a2f36;${i===0?"color:#c9a227;font-weight:bold":""}"><span>${i+1}. ${p.name}</span><span>${p.score}pts</span></div>`).join(""),
    "New Game",()=>location.reload());
}

// ─── BLANK ───────────────────────────────────────────────────
function openBlank(){
  const grid=document.getElementById("blankGrid");
  grid.innerHTML=Object.keys(T).map(s=>`<button onclick="declareBlank('${s}')">${s}</button>`).join("");
  document.getElementById("ovBlank").classList.add("show");
}
function declareBlank(sym){
  document.getElementById("ovBlank").classList.remove("show");
  const tile=G.players[G.ci].hand[G.blankIdx];
  if(tile){tile.symbol=sym;tile.type=T[sym].t;}
  G.si=G.blankIdx;renderRack();renderBoard();
}
function cancelBlank(){document.getElementById("ovBlank").classList.remove("show");G.si=-1;renderRack();}

// ─── HISTORY / INSIGHTS ──────────────────────────────────────
function showHist(){
  showInfo("Game History",G.hist.length?G.hist.map(h=>`
    <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2a2f36;font-size:12px">
      <div><span style="color:#c9a227;font-weight:bold">/${h.word}/</span><br><span style="color:#8b9099;font-size:10px">${h.player} · T${h.tn}</span></div>
      <span style="color:#c9a227">${h.score?"+"+h.score+"pts":""}</span></div>`).join(""):`<p>No moves yet.</p>`,"Close",null);
}
function showInsights(){
  const d=JSON.parse(localStorage.getItem("jeremi_ml")||"null");
  if(!d||d.total_turns<3){showInfo("AI Insights","<p style='color:var(--muted)'>Play more turns to generate insights.</p>","Close",null);return;}
  showInfo("🧠 AI Insights",`<div style="font-size:13px;line-height:1.9">
    <div>Turns observed: <b>${d.total_turns}</b></div>
    <div>Avg score/turn: <b>${d.avg_score}</b></div>
    <div>Preferred length: <b>${d.pref_len}</b></div>
    <div>Bonus usage: <b>${Math.round((d.bonus_rate||0)*100)}%</b></div>
  </div>`,"Close",null);
}

// ─── SAVE / LOAD ─────────────────────────────────────────────
function saveGame(){
  try{localStorage.setItem("jeremi_save",JSON.stringify({board:G.board,bag:G.bag,players:G.players,ci:G.ci,tn:G.tn,hist:G.hist,bht:G.bht}));showToast("Saved ✓","ok");}
  catch(e){showToast("Could not save.","err");}
}
function loadGame(){
  try{
    const raw=localStorage.getItem("jeremi_save");
    if(!raw){showToast("No saved game.","err");return;}
    const s=JSON.parse(raw);
    Object.assign(G,{board:s.board,bag:s.bag,players:s.players,ci:s.ci,tn:s.tn,hist:s.hist,bht:s.bht,placed:[],si:-1});
    document.getElementById("ovSetup").classList.remove("show");
    buildUI();renderAll();showToast("Loaded ✓","ok");
    if(G.players[G.ci].isAI)aiTurn();
  }catch(e){showToast("Could not load.","err");}
}

// ─── MODALS / TOAST ──────────────────────────────────────────
function showInfo(title,body,btnLabel,cb){
  document.getElementById("infoTitle").textContent=title;
  document.getElementById("infoBody").innerHTML=body;
  const btns=document.getElementById("infoBtns");
  if(btnLabel){btns.innerHTML=`<button class="btn primary" id="iob">${btnLabel}</button>`;document.getElementById("iob").onclick=()=>{document.getElementById("ovInfo").classList.remove("show");if(cb)cb();};}
  else if(btns.innerHTML==="")btns.innerHTML=`<button class="btn" onclick="document.getElementById('ovInfo').classList.remove('show')">Close</button>`;
  document.getElementById("ovInfo").classList.add("show");
}
let _tt;
function showToast(msg,type){
  const el=document.getElementById("toast");
  el.textContent=msg;el.className=`toast show${type?" "+type:""}`;
  clearTimeout(_tt);_tt=setTimeout(()=>el.className="toast",3000);
}
function shuffle(a){for(let i=a.length-1;i>0;i--){const j=~~(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}

// ─── INIT ────────────────────────────────────────────────────
updateFields();
window.addEventListener("resize",()=>{if(G.board)renderAll();});
