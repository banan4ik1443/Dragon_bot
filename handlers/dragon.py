"""
Раздел «Драконы» — только вылупившиеся драконы (яйца теперь отдельно,
см. handlers/eggs.py). Можно покормить, потренировать, выбрать активным.
"""
import datetime as dt

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_data as gd
import game_logic as gl
from handlers import quests
from image_utils import get_dragon_image, render_card

router = Router()


def dragons_list_kb(dragons: list[dict]) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    for d in dragons:
        flag = "⚔️" if d["level"] >= gd.RARITIES[d["rarity"]]["min_duel_level"] else "🌱"
        kb.button(text=f"{flag} {d['name']} (ур. {d['level']})", callback_data=f"dragon:view:{d['dragon_id']}")
    kb.button(text="🥚 Открыть яйцо", callback_data="menu:eggs")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(1)
    return kb


async def render_dragons_list(user_id: int) -> tuple[str, InlineKeyboardBuilder]:
    dragons = await db.get_user_dragons(user_id)

    if not dragons:
        text = (
            "🐉 У тебя пока нет драконов.\n\n"
            "Сходи в «Локации» за яйцом и открой его в разделе «Открытие яиц» 🥚"
        )
    else:
        text = "🐉 <b>Твои драконы</b>\n⚔️ — готов к дуэлям · 🌱 — ещё растёт\n\nВыбери дракона:"
    return text, dragons_list_kb(dragons)


@router.message(Command("dragons"))
async def cmd_dragons(message: Message) -> None:
    text, kb = await render_dragons_list(message.from_user.id)
    await message.answer(text, reply_markup=kb.as_markup())


@router.callback_query(F.data == "menu:dragons")
async def cb_dragons(callback: CallbackQuery) -> None:
    text, kb = await render_dragons_list(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


# ── КАРТОЧКА ДРАКОНА ─────────────────────────────────────────────────────
def dragon_card_kb(dragon_id: int, is_active: bool) -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="🍖 Покормить", callback_data=f"dragon:feed:{dragon_id}")
    kb.button(text="🏋️ Тренировать", callback_data=f"dragon:train:{dragon_id}")
    kb.button(text="🛡 Броня", callback_data=f"dragon:armor:{dragon_id}")
    if not is_active:
        kb.button(text="✅ Сделать активным", callback_data=f"dragon:select:{dragon_id}")
    kb.button(text="⬅️ Назад", callback_data="menu:dragons")
    kb.adjust(2, 1, 1, 1)
    return kb


async def render_dragon_card(user_id: int, dragon_id: int) -> tuple[str, InlineKeyboardBuilder, object] | None:
    dragon = await db.get_dragon(dragon_id)
    if not dragon or dragon["owner_id"] != user_id:
        return None

    user = await db.get_user(user_id)
    stats = gl.effective_stats(dragon)
    species_name = gd.species_display_name(dragon["species_key"])
    rarity = gd.RARITIES[dragon["rarity"]]
    ability_name = gd.ABILITIES[dragon["ability_key"]]["name"]
    is_active = user["active_dragon_id"] == dragon_id

    min_level = rarity["min_duel_level"]
    can_duel = dragon["level"] >= min_level
    duel_line = "⚔️ Готов к дуэлям" if can_duel else f"🌱 Растёт · дуэли откроются на ур. {min_level}"

    # Стадия роста и таймер
    growth_stage = stats.get("growth_stage", "adult")
    stage_data = gd.GROWTH_STAGES.get(growth_stage, {})
    stage_emoji = stage_data.get("emoji", "🐉")
    stage_name = stage_data.get("name", "Взрослый")

    growth_line = ""
    if growth_stage != "adult":
        born_at_iso = dragon.get("born_at") or dragon.get("created_at")
        if born_at_iso:
            born_at = dt.datetime.fromisoformat(born_at_iso)
            hours_passed = (dt.datetime.utcnow() - born_at).total_seconds() / 3600
            # Считаем сколько часов до следующей стадии
            order = gd.GROWTH_ORDER
            idx = order.index(growth_stage) if growth_stage in order else 0
            total_needed = sum(gd.GROWTH_STAGES[s]["hatch_hours"] for s in order[:idx + 1])
            hours_left = max(0, total_needed - hours_passed)
            next_stage = order[idx + 1] if idx + 1 < len(order) else "adult"
            next_name = gd.GROWTH_STAGES.get(next_stage, {}).get("name", "Взрослый")
            if hours_left > 0:
                h = int(hours_left)
                m = int((hours_left - h) * 60)
                growth_line = f"\n⏳ До стадии «{next_name}»: {h}ч {m}м"
            else:
                growth_line = f"\n✅ Готов перейти в стадию «{next_name}»!"

    text = (
        f"{stage_emoji} <b>{dragon['name']}</b>\n"
        f"{rarity['emoji']} {species_name} · {rarity['name']} · {stage_name}\n\n"
        f"<blockquote>Уровень » {dragon['level']}\n"
        f"Опыт » {dragon['exp']}/{gd.exp_to_next_level(dragon['level'])}\n"
        f"⚔️ Сила » {stats['power']}\n"
        f"🛡 Защита » {stats['defense']}\n"
        f"💨 Скорость » {stats['speed']}\n"
        f"😮‍💨 Усталость » {stats['fatigue']}%\n"
        f"✨ Способность » {ability_name} (ур. {dragon['ability_level']})</blockquote>\n"
        f"{duel_line}"
        f"{growth_line}"
    )
    if stats["is_banned"]:
        text += "\n⚠️ Усталость 100% — дракону нужен отдых, действия недоступны."
    if is_active:
        text += "\n✅ Это твой активный дракон."

    image_path = get_dragon_image(dragon["species_key"], growth_stage)
    return text, dragon_card_kb(dragon_id, is_active), image_path


@router.callback_query(F.data.startswith("dragon:view:"))
async def cb_dragon_view(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    result = await render_dragon_card(callback.from_user.id, dragon_id)
    if result is None:
        await callback.answer("Дракон не найден.", show_alert=True)
        return
    text, kb, image_path = result
    await render_card(callback, text, kb.as_markup(), image_path)
    await callback.answer()


@router.callback_query(F.data.startswith("dragon:select:"))
async def cb_dragon_select(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    await db.update_user_fields(callback.from_user.id, active_dragon_id=dragon_id)
    result = await render_dragon_card(callback.from_user.id, dragon_id)
    text, kb, image_path = result
    await render_card(callback, text, kb.as_markup(), image_path)
    await callback.answer("Теперь это твой активный дракон!")


@router.callback_query(F.data.startswith("dragon:feed:"))
async def cb_dragon_feed(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    dragon = await db.get_dragon(dragon_id)
    user = await db.get_user(callback.from_user.id)
    if not dragon or dragon["owner_id"] != callback.from_user.id:
        await callback.answer("Дракон не найден.", show_alert=True)
        return
    if user["meat"] < gd.FEED_MEAT_COST:
        await callback.answer(f"Не хватает мяса (нужно {gd.FEED_MEAT_COST}🍖).", show_alert=True)
        return

    fatigue_now = gl.current_fatigue(dragon["fatigue"], dragon["fatigue_updated_at"], dragon["is_resting"])
    new_level, new_exp = gl.add_dragon_exp(dragon, gd.FEED_EXP_GAIN)
    new_fatigue = max(0, fatigue_now + gd.FEED_FATIGUE_DELTA)

    await db.update_dragon_fields(
        dragon_id,
        level=new_level, exp=new_exp,
        fatigue=new_fatigue, fatigue_updated_at=dt.datetime.utcnow().isoformat(),
    )
    await db.update_user_fields(callback.from_user.id, meat=user["meat"] - gd.FEED_MEAT_COST)
    await quests.record_progress(callback.from_user.id, "feed")

    result = await render_dragon_card(callback.from_user.id, dragon_id)
    text, kb, image_path = result
    await render_card(callback, text, kb.as_markup(), image_path)
    await callback.answer(f"Дракон сыт и доволен 🍖 (−{gd.FEED_MEAT_COST} мяса)")


@router.callback_query(F.data.startswith("dragon:train:"))
async def cb_dragon_train(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    dragon = await db.get_dragon(dragon_id)
    user = await db.get_user(callback.from_user.id)
    if not dragon or dragon["owner_id"] != callback.from_user.id:
        await callback.answer("Дракон не найден.", show_alert=True)
        return

    fatigue_now = gl.current_fatigue(dragon["fatigue"], dragon["fatigue_updated_at"], dragon["is_resting"])
    if gl.is_banned_by_fatigue(fatigue_now):
        await callback.answer("Дракон слишком устал, дайте ему отдохнуть.", show_alert=True)
        return
    if user["coins"] < gd.TRAIN_COIN_COST or user["meat"] < gd.TRAIN_MEAT_COST:
        await callback.answer(
            f"Нужно {gd.TRAIN_COIN_COST}🪙 и {gd.TRAIN_MEAT_COST}🍖 для тренировки.", show_alert=True,
        )
        return

    new_level, new_exp = gl.add_dragon_exp(dragon, gd.TRAIN_EXP_GAIN)
    new_fatigue = min(100, fatigue_now + gd.TRAIN_FATIGUE_DELTA)

    await db.update_dragon_fields(
        dragon_id,
        level=new_level, exp=new_exp,
        fatigue=new_fatigue, fatigue_updated_at=dt.datetime.utcnow().isoformat(),
    )
    await db.update_user_fields(
        callback.from_user.id,
        coins=user["coins"] - gd.TRAIN_COIN_COST,
        meat=user["meat"] - gd.TRAIN_MEAT_COST,
    )
    await quests.record_progress(callback.from_user.id, "train")

    result = await render_dragon_card(callback.from_user.id, dragon_id)
    text, kb, image_path = result
    await render_card(callback, text, kb.as_markup(), image_path)
    await callback.answer(f"Тренировка прошла успешно 🏋️ (−{gd.TRAIN_COIN_COST}🪙 −{gd.TRAIN_MEAT_COST}🍖)")


@router.callback_query(F.data.startswith("dragon:armor:"))
async def cb_armor_menu(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    dragon = await db.get_dragon(dragon_id)
    if not dragon or dragon["owner_id"] != callback.from_user.id:
        await callback.answer("Дракон не найден.", show_alert=True)
        return

    user = await db.get_user(callback.from_user.id)
    current_armor = dragon.get("armor_key")
    current_name = gd.ARMOR_CATALOG[current_armor]["name"] if current_armor else "нет"

    kb = InlineKeyboardBuilder()
    for armor_key, armor in gd.ARMOR_CATALOG.items():
        equipped = " ✅" if armor_key == current_armor else ""
        kb.button(
            text=f"{armor['name']} (+{armor['defense_bonus']} защита) · {armor['price']}🪙{equipped}",
            callback_data=f"dragon:armor:equip:{dragon_id}:{armor_key}",
        )
    if current_armor:
        kb.button(text="❌ Снять броню", callback_data=f"dragon:armor:remove:{dragon_id}")
    kb.button(text="⬅️ Назад", callback_data=f"dragon:view:{dragon_id}")
    kb.adjust(1)

    text = (
        f"🛡 <b>Броня дракона</b>\n\n"
        f"Текущая: <b>{current_name}</b>\n\n"
        f"Выбери броню для надевания (цена снимается с баланса монет):\n"
        f"🪙 Твои монеты: {user['coins']}"
    )
    await callback.message.edit_text(text, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("dragon:armor:equip:"))
async def cb_armor_equip(callback: CallbackQuery) -> None:
    parts = callback.data.split(":")
    dragon_id = int(parts[3])
    armor_key = parts[4]

    dragon = await db.get_dragon(dragon_id)
    if not dragon or dragon["owner_id"] != callback.from_user.id:
        await callback.answer("Дракон не найден.", show_alert=True)
        return

    if dragon.get("armor_key") == armor_key:
        await callback.answer("Эта броня уже надета!", show_alert=True)
        return

    armor = gd.ARMOR_CATALOG[armor_key]
    user = await db.get_user(callback.from_user.id)

    if user["coins"] < armor["price"]:
        await callback.answer(f"Не хватает монет! Нужно {armor['price']} 🪙", show_alert=True)
        return

    await db.update_user_fields(callback.from_user.id, coins=user["coins"] - armor["price"])
    await db.update_dragon_fields(dragon_id, armor_key=armor_key)
    await callback.answer(f"✅ Надета броня «{armor['name']}»! -{armor['price']}🪙")

    result = await render_dragon_card(callback.from_user.id, dragon_id)
    if result:
        text, kb, image_path = result
        await render_card(callback, text, kb.as_markup(), image_path)


@router.callback_query(F.data.startswith("dragon:armor:remove:"))
async def cb_armor_remove(callback: CallbackQuery) -> None:
    dragon_id = int(callback.data.split(":")[-1])
    dragon = await db.get_dragon(dragon_id)
    if not dragon or dragon["owner_id"] != callback.from_user.id:
        await callback.answer("Дракон не найден.", show_alert=True)
        return

    await db.update_dragon_fields(dragon_id, armor_key=None)
    await callback.answer("Броня снята.")

    result = await render_dragon_card(callback.from_user.id, dragon_id)
    if result:
        text, kb, image_path = result
        await render_card(callback, text, kb.as_markup(), image_path)
