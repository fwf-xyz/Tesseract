import os
import tempfile
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from services import transcribe_audio, process_workout_text

from datetime import datetime
from services import build_confirmation_caption
from keyboards import verify_workout_keyboard
from utils import WorkoutConstants

router = Router()


async def download_and_transcribe(bot, file_id: str, message: Message) -> str | None:
    """Скачивает аудио и возвращает сырой текст."""
    file = await bot.get_file(file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        await bot.download_file(file.file_path, destination=tmp_path)
        text = await asyncio.to_thread(transcribe_audio, tmp_path)
        return text or None

    except Exception as e:
        await message.reply(f"❌ Ошибка при транскрипции: {e}")
        return None

    finally:
        os.unlink(tmp_path)


@router.message(F.voice)
async def handle_voice(message: Message, bot) -> None:
    status = await message.reply("🎙 Распознаю речь...")

    raw_text = await download_and_transcribe(bot, message.voice.file_id, message)
    if not raw_text:
        await status.edit_text("❌ Не удалось распознать речь.")
        return

    await status.edit_text("🤖 Обрабатываю данные тренировки...")

    workout_data = await asyncio.to_thread(process_workout_text, raw_text)

    if not workout_data.get("workout_type"):
        await status.edit_text(
            f"❌ Не удалось извлечь данные тренировки.\n\n"
            f"📝 Распознанный текст:\n{raw_text}"
        )
        return

    await status.delete()

    # Маппим JSON от ИИ в формат confirm_workout_data
    await confirm_workout_from_voice(
        message=message,
        workout_type=workout_data["workout_type"],
        duration=workout_data["duration"] or 0,
        intensity=workout_data["intensity"],
        note=workout_data["notes"],
    )


@router.message(F.audio)
async def handle_audio(message: Message, bot) -> None:
    await handle_voice.__wrapped__(message, bot) \
        if hasattr(handle_voice, '__wrapped__') \
        else await _process_audio(message, bot, message.audio.file_id)


@router.message(F.video_note)
async def handle_video_note(message: Message, bot) -> None:
    await _process_audio(message, bot, message.video_note.file_id)


async def _process_audio(message: Message, bot, file_id: str) -> None:
    """Общий обработчик для audio и video_note."""
    status = await message.reply("🎙 Распознаю речь...")

    raw_text = await download_and_transcribe(bot, file_id, message)
    if not raw_text:
        await status.edit_text("❌ Не удалось распознать речь.")
        return

    await status.edit_text("🤖 Обрабатываю данные тренировки...")
    workout_data = await asyncio.to_thread(process_workout_text, raw_text)

    if not workout_data.get("workout_type"):
        await status.edit_text(
            f"❌ Не удалось извлечь данные тренировки.\n\n"
            f"📝 Распознанный текст:\n{raw_text}"
        )
        return

    await status.delete()
    await confirm_workout_from_voice(
        message=message,
        workout_type=workout_data["workout_type"],
        duration=workout_data["duration"] or 0,
        intensity=workout_data["intensity"],
        note=workout_data["notes"],
    )


async def confirm_workout_from_voice(
    message: Message,
    workout_type: str,
    duration: int,
    intensity: int | None,
    note: str | None,
) -> None:
    """Показывает карточку подтверждения тренировки из голосового сообщения."""
    dt = datetime.now()

    # Нормализуем тип через WorkoutConstants если есть маппинг
    display_type = WorkoutConstants.TYPES.get(workout_type, workout_type)

    caption = build_confirmation_caption(
        workout_type=display_type,
        duration=duration,
        intensity=intensity,
        note=note,
        dt=dt
    )

    await message.answer(
        text=caption,
        reply_markup=verify_workout_keyboard(),
        parse_mode='HTML'
    )