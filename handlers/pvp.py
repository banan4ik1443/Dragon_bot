"""
Дуэли. Если соперника нет — бой с ботом похожего уровня.
Ранги влияют на количество клыков за победу/поражение.
"""
import datetime as dt
import random

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
import game_logic as gl
from handlers import quests

router = Router()

DUEL_FATIGUE_DELTA = 15
BOT_WAIT_SECONDS = 5  # секунд ждём живого игрока перед боем с ботом

_queue: list[tuple[int, int, dt.datetime]] = []


def _is_weekend() -> bool:
    return dt.datetime.utcnow().weekday() >= 5


def _generate_bot_dragon(player_dragon: dict, player_stats: dict) -> dict:
    """Создаём виртуального дракона-бота близкого к уровню игрока."""
    level = player_dragon["level"]
    # Слегка рандомизируем силу бота (±15%)
    mult = random.uniform(0.85, 1.15)
    return {
        "name": random.choice(["Дракон Стражей", "Древний Вирм", "Теневой Боец", "Горный Зверь", "Огненный Охотник"]),
        "power": round(player_stats["power"] * mult),
        "defense": round(player_stats["defense"] * mult),
        "speed": round(player_stats["speed"] * mult),
        "is_bot": True,
        "level": level,
    }


async def _resolve_duel_vs_bot(bot: Bot, uid: int, dragon_id: int) -> None:
    user = await db.get_user(uid)
    dragon = await db.get_dragon(dragon_id)
    stats = gl.effective_stats(dragon)
    bot_dragon = _generate_bot_dragon(dragon, stats)

    player_power = stats["power"] + stats["defense"] * 0.5 + stats["speed"] * 0.3
    bot_power = bot_dragon["power"] + bot_dragon["defense"] * 0.5 + bot_dragon["speed"] * 0.3
    total = player_power + bot_power
    win_chance = player_power / total if total > 0 else 0.5
    won = random.random() < win_chance

    rank_info = gd.get_rank(user["fangs"])
    rank = rank_info["rank"]
    fangs_change = rank["fangs_gain"] if won else rank["fangs_loss"]

    if won:
        new_fangs = user["fangs"] + fangs_change
        result_text = (
            f"🏆 <b>Победа!</b> Твой {dragon['name']} одолел {bot_dragon['name']} (бот ур.{bot_dragon['level']}).\n"
            f"🦷 +{fangs_change} клыков."
        )
    else:
        new_fangs = max(0, user["fangs"] - fangs_change)
        result_text = (
            f"💀 <b>Поражение.</b> {bot_dragon['name']} (бот ур.{bot_dragon['level']}) оказался сильнее.\n"
            f"🦷 -{fangs_change} клыков."
        )

    await db.update_user_fields(uid, fangs=new_fangs)
    fatigue_now = gl.current_fatigue(dragon["fatigue"], dragon["fatigue_updated_at"], dragon["is_resting"])
    await db.update_dragon_fields(
        dragon_id,
        fatigue=min(100, fatigue_now + DUEL_FATIGUE_DELTA),
        fatigue_updated_at=dt.datetime.utcnow().isoformat(),
    )
    await quests.record_progress(uid, "duel_play")

    new_rank_info = gd.get_rank(new_fangs)
    rank_up = new_rank_info["rank_idx"] > rank_info["rank_idx"]
    rank_line = f"\n🎖️ Новый ранг: {new_rank_info['rank']['emoji']} {new_rank_info['rank']['name']}!" if rank_up else ""

    try:
        await bot.send_message(uid, result_text + rank_line)
    except Exception:
        pass


async def _resolve_duel(bot: Bot, uid1: int, did1: int, uid2: int, did2: int) -> None:
    user1, user2 = await db.get_user(uid1), await db.get_user(uid2)
    dragon1, dragon2 = await db.get_dragon(did1), await db.get_dragon(did2)
    stats1, stats2 = gl.effective_stats(dragon1), gl.effective_stats(dragon2)

    power1 = stats1["power"] + stats1["defense"] * 0.5 + stats1["speed"] * 0.3
    power2 = stats2["power"] + stats2["defense"] * 0.5 + stats2["speed"] * 0.3
    total = power1 + power2
    winner_is_1 = random.random() < (power1 / total if total > 0 else 0.5)

    winner_uid, winner_did = (uid1, did1) if winner_is_1 else (uid2, did2)
    loser_uid, loser_did = (uid2, did2) if winner_is_1 else (uid1, did1)
    winner_user, loser_user = (user1, user2) if winner_is_1 else (user2, user1)

    winner_rank = gd.get_rank(winner_user["fangs"])
    loser_rank = gd.get_rank(loser_user["fangs"])
    fangs_gain = winner_rank["rank"]["fangs_gain"]
    fangs_loss = loser_rank["rank"]["fangs_loss"]

    new_winner_fangs = winner_user["fangs"] + fangs_gain
    new_loser_fangs = max(0, loser_user["fangs"] - fangs_loss)

    await db.update_user_fields(winner_uid, fangs=new_winner_fangs)
    await db.update_user_fields(loser_uid, fangs=new_loser_fangs)

    for did in (did1, did2):
        d = await db.get_dragon(did)
        f = gl.current_fatigue(d["fatigue"], d["fatigue_updated_at"], d["is_resting"])
        await db.update_dragon_fields(did, fatigue=min(100, f + DUEL_FATIGUE_DELTA),
                                      fatigue_updated_at=dt.datetime.utcnow().isoformat())

    await quests.record_progress(uid1, "duel_play")
    await quests.record_progress(uid2, "duel_play")

    winner_dragon = await db.get_dragon(winner_did)
    loser_dragon = await db.get_dragon(loser_did)

    new_winner_rank = gd.get_rank(new_winner_fangs)
    rank_up = new_winner_rank["rank_idx"] > winner_rank["rank_idx"]
    rank_line = f"\n🎖️ Новый ранг: {new_winner_rank['rank']['emoji']} {new_winner_rank['rank']['name']}!" if rank_up else ""

    try:
        await bot.send_message(winner_uid,
            f"🏆 <b>Победа!</b> Твой {winner_dragon['name']} одолел {loser_dragon['name']}.\n"
            f"🦷 +{fangs_gain} клыков.{rank_line}")
    except Exception:
        pass
    try:
        await bot.send_message(loser_uid,
            f"💀 <b>Поражение.</b> Твой {loser_dragon['name']} проиграл {winner_dragon['name']}.\n"
            f"🦷 -{fangs_loss} клыков.")
    except Exception:
        pass


@router.message(Command("duel"))
async def cmd_duel(message: Message, bot: Bot) -> None:
    user = await db.get_user(message.from_user.id)
    if user is None:
        await message.answer("Сначала напиши /start.")
        return
    if not user["active_dragon_id"]:
        await message.answer("У тебя нет активного дракона.")
        return

    dragon = await db.get_dragon(user["active_dragon_id"])
    stats = gl.effective_stats(dragon)
    if stats["is_banned"]:
        await message.answer("Твой дракон обессилен — дай ему отдохнуть.")
        return

    min_level = gd.RARITIES[dragon["rarity"]]["min_duel_level"]
    if dragon["level"] < min_level:
        await message.answer(f"Дракону нужен уровень {min_level} для дуэлей (сейчас {dragon['level']}).")
        return

    if any(uid == message.from_user.id for uid, _, _ in _queue):
        await message.answer("Ты уже в очереди ⏳")
        return

    _queue.append((message.from_user.id, dragon["dragon_id"], dt.datetime.utcnow()))
    await message.answer("🔍 Ищем соперника... (если не найдём за 5 сек — бой с ботом)")

    # Проверяем очередь
    import asyncio
    await asyncio.sleep(BOT_WAIT_SECONDS)

    # Проверяем жив ли наш запрос в очереди
    our_entry = next((e for e in _queue if e[0] == message.from_user.id), None)
    if our_entry is None:
        return  # уже был матч с живым игроком

    # Есть ли другой игрок?
    other = next((e for e in _queue if e[0] != message.from_user.id), None)
    if other:
        _queue.remove(our_entry)
        _queue.remove(other)
        await _resolve_duel(bot, message.from_user.id, dragon["dragon_id"], other[0], other[1])
    else:
        _queue.remove(our_entry)
        await message.answer("Живых соперников нет — бой с ботом! 🤖")
        await _resolve_duel_vs_bot(bot, message.from_user.id, dragon["dragon_id"])
