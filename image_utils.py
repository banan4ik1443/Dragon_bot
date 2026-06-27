"""
Показ "карточек" (текст + клавиатура), которые могут сопровождаться фото
дракона — если файл есть на диске. Если файла нет, всё работает как раньше,
чисто текстом — поэтому это можно безопасно подключать ДО того, как
появятся реальные картинки.

СТРУКТУРА ПАПКИ С КАРТИНКАМИ:
    assets/dragons/{species_key}_{stage}.{jpg|jpeg|png|webp}

    Например: assets/dragons/fire_rare_baby.png
              assets/dragons/fire_rare_adult.jpg

Стадия "teen" (подросток) необязательна: если для неё нет файла, берётся
картинка взрослой стадии, а если и её нет — детской. Так можно начать
всего с 2 картинок на дракона (baby/adult) вместо 3.
"""
from pathlib import Path

from aiogram.types import CallbackQuery, Message, FSInputFile, InputMediaPhoto

ASSETS_DIR = Path(__file__).parent / "assets" / "dragons"
IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp")

STAGE_FALLBACK = {
    "baby": ["baby"],
    "teen": ["teen", "adult", "baby"],
    "adult": ["adult"],
}


def get_dragon_image(species_key: str, stage: str) -> Path | None:
    """Ищет файл картинки для вида+стадии с разумным фолбэком. None, если нет ни одной."""
    for candidate_stage in STAGE_FALLBACK.get(stage, [stage]):
        for ext in IMAGE_EXTENSIONS:
            path = ASSETS_DIR / f"{species_key}_{candidate_stage}.{ext}"
            if path.exists():
                return path
    return None


async def render_card(event: CallbackQuery | Message, text: str, kb, image_path: Path | None = None) -> None:
    """Показывает карточку, по возможности с фото. event — CallbackQuery (редактируем
    существующее сообщение) или Message (отвечаем новым). kb — уже собранная
    InlineKeyboardMarkup (kb.as_markup(), не сам builder)."""
    is_callback = isinstance(event, CallbackQuery)
    message = event.message if is_callback else event

    if image_path is None:
        if is_callback and message.photo:
            # переходим с фото на текст — Bot API не даёт превратить фото-сообщение
            # в текстовое через edit, поэтому шлём новое и удаляем старое
            await message.delete()
            await message.answer(text, reply_markup=kb)
        elif is_callback:
            await message.edit_text(text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)
        return

    photo = FSInputFile(image_path)
    if is_callback and message.photo:
        try:
            await message.edit_media(InputMediaPhoto(media=photo, caption=text), reply_markup=kb)
            return
        except Exception:
            pass  # на случай если медиа не изменилось — fallback ниже
    if is_callback:
        await message.delete()
        await message.answer_photo(photo, caption=text, reply_markup=kb)
    else:
        await message.answer_photo(photo, caption=text, reply_markup=kb)
