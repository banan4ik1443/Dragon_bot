"""
Локации с боссами. Игрок раз в 30 минут идёт в локацию, встречает
случайного босса и сражается с ним. Победа = награда, поражение = утешительный приз.
"""
import datetime as dt
import random

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
import game_logic as gl
from handlers import quests

router = Router()

EXPLORE_COOLDOWN_MIN = 30

LOCATIONS = {
    "forest":    "🌲 Тёмный лес",
    "mountains": "⛰️ Драконьи горы",
    "caves":     "🕳️ Подземные пещеры",
}


def locations_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for key, name in LOCATIONS.items():
        kb.button(text=name, callback_data=f"explore:go:{key}")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1)
    return kb


@router.message(Command("explore"))
async def cmd_explore(message: Message) -> None:
    await message.answer("🗺️ Куда отправить дракона?", reply_markup=locations_kb().as_markup())


@router.callback_query(F.data == "menu:explore")
async def cb_explore_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🗺️ Куда отправить дракона?", reply_markup=locations_kb().as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("explore:go:"))
async def cb_explore_go(callback: CallbackQuery) -> None:
    location_key = callback.data.split(":")[-1]
    user = await db.get_user(callback.from_user.id)
    if user is None:
        await callback.answer("Сначала напиши /start.", show_alert=True)
        return

    # Кулдаун
    if user["last_explore_at"]:
        last = dt.datetime.fromisoformat(user["last_explore_at"])
        elapsed_min = (dt.datetime.utcnow() - last).total_seconds() / 60
        if elapsed_min < EXPLORE_COOLDOWN_MIN:
            left = round(EXPLORE_COOLDOWN_MIN - elapsed_min)
            await callback.answer(f"Дракон ещё отдыхает. Подожди ~{left} мин.", show_alert=True)
            return

    if not user["active_dragon_id"]:
        await callback.answer("Нужен активный дракон для похода!", show_alert=True)
        return

    dragon = await db.get_dragon(user["active_dragon_id"])
    stats = gl.effective_stats(dragon)

    # Выбираем случайного босса
    boss = random.choice(gd.LOCATION_BOSSES[location_key])

    # Боевая формула
    player_power = stats["power"] + stats["defense"] * 0.5 + stats["speed"] * 0.3
    boss_power = boss["base_power"] + boss["base_defense"] * 0.5 + boss["base_speed"] * 0.3
    total = player_power + boss_power
    win_chance = player_power / total if total > 0 else 0.5
    won = random.random() < win_chance

    await db.update_user_fields(callback.from_user.id, last_explore_at=dt.datetime.utcnow().isoformat())
    await quests.record_progress(callback.from_user.id, "explore")

    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ К локациям", callback_data="menu:explore")

    loc_name = LOCATIONS[location_key]

    if won:
        reward_meat = boss["reward_meat"]
        reward_coins = boss["reward_coins"]
        await db.update_user_fields(
            callback.from_user.id,
            meat=user["meat"] + reward_meat,
            coins=user["coins"] + reward_coins,
        )
        # Шанс на яйцо
        egg_text = ""
        if random.random() < boss["egg_chance"]:
            rarity = gl.roll_egg_rarity()
            await db.add_egg(callback.from_user.id, rarity)
            egg_text = f"\n🥚 Трофей: яйцо «{gd.RARITIES[rarity]['name']}»!"

        text = (
            f"{loc_name}\n\n"
            f"{boss['emoji']} <b>{boss['name']}</b> встал на пути!\n\n"
            f"⚔️ Твой {dragon['name']} сразился и <b>победил</b>!\n\n"
            f"<blockquote>🍖 +{reward_meat} мяса\n"
            f"🪙 +{reward_coins} монет{egg_text}</blockquote>"
        )
    else:
        # Утешительный приз
        consolation_meat = random.randint(5, 15)
        await db.update_user_fields(callback.from_user.id, meat=user["meat"] + consolation_meat)
        text = (
            f"{loc_name}\n\n"
            f"{boss['emoji']} <b>{boss['name']}</b> оказался слишком силён!\n\n"
            f"💀 Твой {dragon['name']} <b>потерпел поражение</b>.\n\n"
            f"<blockquote>🍖 +{consolation_meat} мяса (остатки с поля боя)</blockquote>\n"
            f"Прокачай дракона и возвращайся!"
        )

    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()
