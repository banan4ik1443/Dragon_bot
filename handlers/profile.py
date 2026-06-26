"""
Профиль игрока с рангом, ником и полными статами.
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
import game_logic as gl
import game_data as gd

router = Router()


class NicknameForm(StatesGroup):
    waiting_for_nickname = State()


def profile_kb() -> InlineKeyboardBuilder:
    kb = InlineKeyboardBuilder()
    kb.button(text="⚙️ Настройки", callback_data="profile:settings")
    kb.button(text="🐉 Драконы", callback_data="menu:dragons")
    kb.button(text="🏅 Таблица рангов", callback_data="profile:ranks")
    kb.button(text="⬅️ Меню", callback_data="menu:main")
    kb.adjust(2, 1, 1)
    return kb


async def render_profile(user_id: int) -> str:
    user = await db.get_user(user_id)
    if user is None:
        return "Сначала напиши /start."

    rank_info = gd.get_rank(user["fangs"])
    rank = rank_info["rank"]
    next_rank = rank_info["next_rank"]
    progress_line = ""
    if next_rank:
        needed = next_rank["min_fangs"] - rank["min_fangs"]
        current = user["fangs"] - rank["min_fangs"]
        bar_len = 10
        filled = min(bar_len, round(current / needed * bar_len))
        bar = "█" * filled + "░" * (bar_len - filled)
        progress_line = f"\n[{bar}] до «{next_rank['name']}»"
    else:
        progress_line = "\n🏆 Максимальный ранг!"

    active = None
    if user["active_dragon_id"]:
        active = await db.get_dragon(user["active_dragon_id"])

    vip_line = f"💎 VIP: {user['vip_status']}\n" if user["vip_status"] else ""

    text = (
        f"👤 {user['nickname']}\n"
        f"{rank['emoji']} {rank['name']}{progress_line}\n\n"
        f"Ресурсы\n"
        f"<blockquote>"
        f"{vip_line}"
        f"🦷 Клыки » {user['fangs']}\n"
        f"🪙 Монеты » {user['coins']}\n"
        f"🍖 Мясо » {user['meat']}\n"
        f"✨ Опыт » {user['exp']}"
        f"</blockquote>"
    )

    if active:
        stats = gl.effective_stats(active)
        species_name = gd.SPECIES[active["species_key"]]["name"]
        rarity = gd.RARITIES[active["rarity"]]
        growth = stats.get("growth", {})
        stage_emoji = growth.get("emoji", "🐉")
        stage_name = growth.get("name", "Взрослый")
        growth_timer = ""
        if growth.get("hours_left", 0) > 0:
            h = int(growth["hours_left"])
            m = int((growth["hours_left"] - h) * 60)
            growth_timer = f"\n⏳ До стадии «{gd.GROWTH_STAGES.get(growth.get('next_stage','adult'),{}).get('name','')}»: {h}ч {m}м"

        text += (
            f"\n\nАктивный дракон\n"
            f"<blockquote>"
            f"{stage_emoji} {active['name']} {rarity['emoji']}\n"
            f"Вид » {species_name} · {rarity['name']}\n"
            f"Стадия » {stage_name}{growth_timer}\n"
            f"Уровень » {active['level']} · Опыт » {active['exp']}/{gd.exp_to_next_level(active['level'])}\n"
            f"⚔️ Сила » {stats['power']} · 🛡 Защита » {stats['defense']} · 💨 Скорость » {stats['speed']}\n"
            f"😮 Усталость » {stats['fatigue']}%"
            f"</blockquote>"
        )
        if stats["is_banned"]:
            text += "\n⚠️ Дракон обессилен — нужен отдых!"
    else:
        text += "\n\nНет активного дракона — открой яйцо 🥚"

    return text


def ranks_table_text() -> str:
    lines = ["🏅 <b>Таблица рангов</b>\n"]
    for i, r in enumerate(gd.RANKS):
        next_r = gd.RANKS[i + 1] if i + 1 < len(gd.RANKS) else None
        fangs_range = f"{r['min_fangs']}–{next_r['min_fangs']-1}" if next_r else f"{r['min_fangs']}+"
        lines.append(
            f"{r['emoji']} <b>{r['name']}</b> · {fangs_range} 🦷\n"
            f"   +{r['fangs_gain']} за победу · -{r['fangs_loss']} за поражение"
        )
    return "\n".join(lines)


@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    text = await render_profile(message.from_user.id)
    await message.answer(text, reply_markup=profile_kb().as_markup())


@router.callback_query(F.data == "menu:profile")
async def cb_profile(callback: CallbackQuery) -> None:
    text = await render_profile(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=profile_kb().as_markup())
    await callback.answer()


@router.callback_query(F.data == "profile:ranks")
async def cb_ranks(callback: CallbackQuery) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="menu:profile")
    await callback.message.edit_text(ranks_table_text(), reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "profile:settings")
async def cb_settings(callback: CallbackQuery) -> None:
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Сменить ник", callback_data="settings:nickname")
    kb.button(text="⬅️ Назад", callback_data="menu:profile")
    kb.adjust(1)
    await callback.message.edit_text("⚙️ Настройки профиля:", reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data == "settings:nickname")
async def cb_ask_nickname(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(NicknameForm.waiting_for_nickname)
    await callback.message.edit_text("Введи новый никнейм (2-20 символов):")
    await callback.answer()


@router.message(NicknameForm.waiting_for_nickname)
async def process_nickname(message: Message, state: FSMContext) -> None:
    nickname = message.text.strip()
    if not (2 <= len(nickname) <= 20):
        await message.answer("Никнейм должен быть от 2 до 20 символов. Попробуй ещё раз:")
        return
    await db.update_user_fields(message.from_user.id, nickname=nickname)
    await state.clear()
    await message.answer(f"Готово! Теперь ты — <b>{nickname}</b>.", reply_markup=profile_kb().as_markup())


@router.message(Command("nickname"))
async def cmd_nickname(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer("Использование: /nickname НовоеИмя")
        return
    nickname = command.args.strip()
    if not (2 <= len(nickname) <= 20):
        await message.answer("Никнейм должен быть от 2 до 20 символов.")
        return
    await db.update_user_fields(message.from_user.id, nickname=nickname)
    await message.answer(f"Готово! Теперь ты — <b>{nickname}</b>.")
