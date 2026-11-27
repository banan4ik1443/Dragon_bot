import balance from '../config/balance.js';
const clamp=(v,min,max)=>Math.max(min,Math.min(max,Number(v)||min));
export function simulateCombat(elemA,levelA,elemB,levelB){
 const E=balance.elements; if(!E[elemA]||!E[elemB])throw new Error('Unknown element');
 const make=(elem,level)=>{const e=E[elem],lv=clamp(level,1,balance.maxLevel),growth=1+(lv-1)*balance.levelStatPerLevel;return {elem,level:lv,hp:Math.round(e.hp*growth),maxHp:Math.round(e.hp*growth),attack:Math.round(e.attack*growth),defense:Math.round(e.defense*growth),speed:Math.round(e.speed*growth),bonus:e.damageBonus}};
 const a=make(elemA,levelA),b=make(elemB,levelB),log=[];
 const advantage=(att,def)=>E[att.elem].beats===def.elem?balance.elementalAdvantage:E[att.elem].weak===def.elem?balance.elementalDisadvantage:1;
 for(let round=1;round<=balance.maxRounds&&a.hp>0&&b.hp>0;round++){const order=a.speed>=b.speed?[['a',a,b],['b',b,a]]:[['b',b,a],['a',a,b]];for(const [who,att,def] of order){if(att.hp<=0||def.hp<=0)continue;const mult=advantage(att,def)*att.bonus;const dmg=Math.max(4,Math.round(att.attack*mult-def.defense*.32));def.hp=Math.max(0,def.hp-dmg);log.push({round,attacker:who,damage:dmg,targetHp:def.hp});}}
 let winner=a.hp===b.hp?(a.speed>=b.speed?'a':'b'):a.hp>b.hp?'a':'b';return {winner,rounds:log.length?log[log.length-1].round:0,remaining:{a:a.hp,b:b.hp},log,stats:{a,b}};
}
