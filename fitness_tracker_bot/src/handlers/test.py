import os
import tempfile
import asyncio
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from datetime import datetime
from services import transcribe_audio, process_workout_text, build_confirmation_caption
from keyboards import verify_workout_keyboard
from utils import WorkoutConstants
from states import WorkoutForm
from database import Repository

router = Router()


async def download_and_transcribe(bot, file_id: str, message: Message) -> str | None:
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


async def process_audio(message: Message, bot, file_id: str,
                            state: FSMContext, repo: Repository) -> None:
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
    await state.update_data(workout_type=workout_data["workout_type"], duration=workout_data["duration"] or 0,
                                intensity=workout_data["intensity"], note=workout_data["notes"])
    await confirm_workout_from_voice(
        message=message,
        workout_type=workout_data["workout_type"],
        state=state,
        repo=repo,
        duration=workout_data["duration"] or 0,
        intensity=workout_data["intensity"],
        note=workout_data["notes"],
    )


async def confirm_workout_from_voice(message: Message, workout_type: str,
                                        duration: int, intensity: int | None,
                                            note: str | None, state: FSMContext,
                                                repo: Repository) -> None:
    dt = datetime.now()
    display_type = WorkoutConstants.TYPES.get(workout_type, "Unknown")
    photo_id = repo.users.paste_decoration_id("workout_saved")

    caption = build_confirmation_caption(
        workout_type=display_type,
        duration=duration,
        intensity=intensity,
        note=note,
        dt=dt,
    )

    sent = await message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=verify_workout_keyboard(),
        parse_mode="HTML",
    )

    await state.update_data(note=note, messages_to_delete=[sent.message_id])
