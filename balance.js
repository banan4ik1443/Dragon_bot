// All game balance is configured here. Keep this file server-side only.
export default {
 startingGold:0, winGold:80, lossGold:20, winRating:25, lossRating:15,
 testGold:100000, testResources:{crystals:10000,tickets:1000}, matchTimeoutMs:120000,
 elements:{
  fire:{name:'Огонь',hp:95,attack:122,defense:78,speed:108,beats:'wind',weak:'water',damageBonus:1.12},
  water:{name:'Вода',hp:115,attack:90,defense:115,speed:85,beats:'fire',weak:'earth',damageBonus:1.0},
  earth:{name:'Земля',hp:135,attack:88,defense:125,speed:72,beats:'water',weak:'wind',damageBonus:0.96},
  wind:{name:'Ветер',hp:90,attack:105,defense:80,speed:132,beats:'earth',weak:'fire',damageBonus:1.04},
  light:{name:'Свет',hp:100,attack:115,defense:100,speed:100,beats:'dark',weak:'dark',damageBonus:1.06},
  dark:{name:'Тьма',hp:105,attack:120,defense:95,speed:95,beats:'light',weak:'light',damageBonus:1.08}
 },
 elementalAdvantage:1.18, elementalDisadvantage:0.84, levelStatPerLevel:0.035, maxLevel:50, maxRounds:30
};
