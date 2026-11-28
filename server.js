import express from 'express';
import crypto from 'node:crypto';
import Database from 'better-sqlite3';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import balance from './balance.js';
dotenv.config();
const __dirname=path.dirname(fileURLToPath(import.meta.url));
const app=express(); app.use(express.json({limit:'32kb'}));
app.use(express.static(__dirname)); app.get('/',(_,res)=>res.sendFile(path.join(__dirname,'index.html')));
const db=new Database(process.env.DB_FILE||'dragon-pvp.sqlite'); db.pragma('journal_mode=WAL');
db.exec(`CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY, username TEXT, gold INTEGER DEFAULT 0, rating INTEGER DEFAULT 1000, wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, crystals INTEGER DEFAULT 0, tickets INTEGER DEFAULT 0);`);
function telegramUser(req){const raw=req.header('x-telegram-init-data')||'';if(!raw||!process.env.BOT_TOKEN)return null;const p=new URLSearchParams(raw),hash=p.get('hash');p.delete('hash');const check=[...p.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>`${k}=${v}`).join('\n');const secret=crypto.createHmac('sha256','WebAppData').update(process.env.BOT_TOKEN).digest();const calc=crypto.createHmac('sha256',secret).update(check).digest('hex');if(!hash||hash.length!==calc.length||!crypto.timingSafeEqual(Buffer.from(hash),Buffer.from(calc)))return null;const authDate=Number(p.get('auth_date'));if(!authDate||Date.now()/1000-authDate>86400)return null;try{return JSON.parse(p.get('user'))}catch{return null}}
function auth(req,res,next){const u=telegramUser(req);if(!u?.id)return res.status(401).json({error:'Telegram authentication required'});req.user=u;next()}
function player(u){db.prepare('INSERT OR IGNORE INTO players(id,username,gold,rating) VALUES(?,?,?,?)').run(u.id,u.username||u.first_name||'Player',balance.startingGold,1000);db.prepare('UPDATE players SET username=? WHERE id=?').run(u.username||u.first_name||'Player',u.id);return db.prepare('SELECT * FROM players WHERE id=?').get(u.id)}
app.get('/api/me',auth,(req,res)=>res.json(player(req.user)));
app.get('/api/top',auth,(req,res)=>res.json(db.prepare('SELECT username,rating,wins,losses FROM players ORDER BY rating DESC,wins DESC LIMIT 50').all()));
// Every authenticated player can claim test resources for their own account.
app.post('/api/test-resources',auth,(req,res)=>{player(req.user);db.prepare('UPDATE players SET gold=gold+?,crystals=crystals+?,tickets=tickets+? WHERE id=?').run(balance.testGold,balance.testResources.crystals,balance.testResources.tickets,req.user.id);res.json({ok:true,added:{gold:balance.testGold,crystals:balance.testResources.crystals,tickets:balance.testResources.tickets}})});
app.get('/health',(_,res)=>res.json({ok:true}));
app.use((req,res)=>{console.log('404:',req.method,req.path);res.status(404).send('Not found')});
const port=process.env.PORT||3000;app.listen(port,'0.0.0.0',()=>console.log(`HTTP server started on port ${port}`));
// Telegram command polling. Set BOT_TOKEN and WEBAPP_URL in environment.
let offset=0, polling=false;
async function tg(method,body){if(!process.env.BOT_TOKEN)return null;const r=await fetch(`https://api.telegram.org/bot${process.env.BOT_TOKEN}/${method}`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});return r.json()}
async function poll(){if(polling||!process.env.BOT_TOKEN)return;polling=true;try{await tg('deleteWebhook',{drop_pending_updates:false});const updates=await tg('getUpdates',{offset,timeout:20});if(updates?.ok)for(const u of updates.result||[]){offset=u.update_id+1;const m=u.message;if(!m?.text)continue;const chat=m.chat.id,txt=m.text.trim().split(/\s+/)[0];if(txt==='/start'){await tg('sendMessage',{chat_id:chat,text:'🐉 Добро пожаловать! Открой игру кнопкой ниже.\n/test — получить тестовые ресурсы\n/help — команды',reply_markup:{inline_keyboard:[[{text:'🎮 Открыть игру',web_app:{url:process.env.WEBAPP_URL||'https://example.com'}}]]}})}else if(txt==='/help'){await tg('sendMessage',{chat_id:chat,text:'/start — открыть игру\n/test — получить тестовые ресурсы\n/help — список команд'})}else if(txt==='/test'||txt==='/test_resources'){const id=m.from.id;player({id,username:m.from.username||m.from.first_name});db.prepare('UPDATE players SET gold=gold+?,crystals=crystals+?,tickets=tickets+? WHERE id=?').run(balance.testGold,balance.testResources.crystals,balance.testResources.tickets,id);await tg('sendMessage',{chat_id:chat,text:`🧪 Тестовые ресурсы выданы!\n💰 ${balance.testGold} золота\n💎 ${balance.testResources.crystals} кристаллов\n🎟 ${balance.testResources.tickets} билетов`})}}}catch(e){console.error('Telegram polling error:',e.message)}finally{polling=false;setTimeout(poll,1000)}}poll();
