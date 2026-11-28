import express from 'express';
import crypto from 'node:crypto';
import Database from 'better-sqlite3';
import dotenv from 'dotenv';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import balance from '../Config/balance.js';
dotenv.config();
const __filename=fileURLToPath(import.meta.url);
const __dirname=path.dirname(__filename);
const app=express(); app.use(express.json({limit:'32kb'}));
app.use(express.static(path.resolve(__dirname,'../frontend')));
app.get('/',(_,res)=>res.sendFile(path.resolve(__dirname,'../frontend/index.html')));
const db=new Database(process.env.DB_FILE||'dragon-pvp.sqlite'); db.pragma('journal_mode=WAL');
db.exec(`CREATE TABLE IF NOT EXISTS players(id INTEGER PRIMARY KEY, username TEXT, gold INTEGER DEFAULT 0, rating INTEGER DEFAULT 1000, wins INTEGER DEFAULT 0, losses INTEGER DEFAULT 0, crystals INTEGER DEFAULT 0, tickets INTEGER DEFAULT 0);`);
const admins=new Set((process.env.ADMIN_IDS||'').split(',').map(x=>Number(x.trim())).filter(Boolean));
function telegramUser(req){const raw=req.header('x-telegram-init-data')||'';if(!raw||!process.env.BOT_TOKEN)return null;const p=new URLSearchParams(raw),hash=p.get('hash');p.delete('hash');const check=[...p.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([k,v])=>`${k}=${v}`).join('\n');const secret=crypto.createHmac('sha256','WebAppData').update(process.env.BOT_TOKEN).digest();const calc=crypto.createHmac('sha256',secret).update(check).digest('hex');if(!hash||hash.length!==calc.length||!crypto.timingSafeEqual(Buffer.from(hash),Buffer.from(calc)))return null;const auth=Number(p.get('auth_date'));if(!auth||Date.now()/1000-auth>86400)return null;try{return JSON.parse(p.get('user'))}catch{return null}}
function auth(req,res,next){const u=telegramUser(req);if(!u?.id)return res.status(401).json({error:'Telegram authentication required'});req.user=u;next()}
function player(u){db.prepare('INSERT OR IGNORE INTO players(id,username,gold,rating) VALUES(?,?,?,?)').run(u.id,u.username||u.first_name||'Player',balance.startingGold,1000);db.prepare('UPDATE players SET username=? WHERE id=?').run(u.username||u.first_name||'Player',u.id);return db.prepare('SELECT * FROM players WHERE id=?').get(u.id)}
async function notify(id,msg){if(!process.env.BOT_TOKEN)return;try{await fetch(`https://api.telegram.org/bot${process.env.BOT_TOKEN}/sendMessage`,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({chat_id:id,text:msg})})}catch(e){console.error('Telegram notification:',e.message)}}
app.get('/api/me',auth,(req,res)=>res.json(player(req.user)));
app.get('/api/top',auth,(req,res)=>res.json(db.prepare('SELECT username,rating,wins,losses FROM players ORDER BY rating DESC,wins DESC LIMIT 50').all()));
app.post('/api/admin/test-resources',auth,(req,res)=>{if(!admins.has(req.user.id))return res.status(403).json({error:'Admin only'});const target=Number(req.body.userId||req.user.id);player({id:target,username:'Player'});db.prepare('UPDATE players SET gold=gold+?,crystals=crystals+?,tickets=tickets+? WHERE id=?').run(balance.testGold,balance.testResources.crystals,balance.testResources.tickets,target);res.json({ok:true,target})});
app.get('/health',(_,res)=>res.json({ok:true}));const port=process.env.PORT||3000;app.listen(port,'0.0.0.0',()=>console.log(`Dragon PvP running on ${port}`));
