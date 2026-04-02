from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states import WorkoutForm

from keyboards import get_workout_type_keyboard, skip_note_keyboard, verify_workout_keyboard, close_add_workout
from services import build_confirmation_caption, save_workout, process_text_message

from database import Repository
from utils import WorkoutConstants, safe_delete_messages, validate_duration, validate_intensity

from .test import process_audio, confirm_workout_from_voice

import asyncio


router = Router()


@router.callback_query(F.data == 'add_workout')
async def add_workout(callback: types.CallbackQuery, state: FSMContext, repo: Repository):

    photo_id = repo.users.paste_decoration_id('info_message')
    text = (
        f"<b>Добавление Тренировки:</b>\n\n"
        f"<blockquote>📝 🎙 <b>Отправь голосовое или текстовое сообщение с:</b>\n"
        f"— типом тренировки (силовая/кардио/растяжка)\n"
        f"— длительностью (от {WorkoutConstants.MIN_DURATION} до {WorkoutConstants.MAX_DURATION} минут)\n"
        f"— интенсивностью (от {WorkoutConstants.MIN_INTENSITY} до {WorkoutConstants.MAX_INTENSITY})</blockquote>"
    )

    sent = await callback.message.answer_photo(photo=photo_id, caption=text,
                                                reply_markup=close_add_workout(), parse_mode='HTML')

    await state.set_state(WorkoutForm.info_message)
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()


@router.callback_query(WorkoutForm.info_message, F.data == 'cancel_add_workout')
async def cancel_add_workout(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await state.clear()
    await callback.answer()


@router.message(WorkoutForm.info_message, F.voice)
async def handle_audio(message: types.Message, bot, state: FSMContext, repo: Repository) -> None:
    data = await state.get_data()

    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
    await process_audio(message, bot, message.voice.file_id, state, repo)

    await message.delete()
    await state.set_state(WorkoutForm.verify)


@router.message(WorkoutForm.info_message)
async def handle_text_new_workout(message: types.Message, state: FSMContext, repo: Repository):
    data = await state.get_data()
    
    await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
    await process_text(message, state, repo, message.text)

    await message.delete()
    await state.set_state(WorkoutForm.verify)


@router.callback_query(WorkoutForm.verify, F.data == 'confirm_workout')
async def confirm_workout(callback: types.CallbackQuery, state: FSMContext, repo: Repository) -> None:
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await save_workout(repo, callback.from_user.id, data)

    await callback.answer('✅ Запись тренировки сохранена!')
    await state.clear()


@router.callback_query(WorkoutForm.verify, F.data == 'cancel_workout')
async def cancel_workout(callback: types.CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

    await callback.answer('❌ Запись тренировки отменена')
    await state.clear()


async def process_text(message: types.Message, state: FSMContext,
                        repo: Repository, raw_text: str):
    status = await message.reply("🔍 Распознаю текст...")
    await asyncio.sleep(3)
    await status.edit_text("🤖 Обрабатываю данные тренировки...")
    workout_data = await asyncio.to_thread(process_text_message, raw_text)

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










# async def confirm_workout_data(message: types.Message, state: FSMContext,
#                                 note: str | None, repo: Repository) -> None:
#     data = await state.get_data()

#     workout_type = WorkoutConstants.TYPES.get(data.get('type', 'Unknown'), data.get('type', 'Unknown'))
#     duration = data.get('duration', 0)
#     intensity = data.get('intensity', None)

#     dt = datetime.now()

#     photo_id = repo.users.paste_decoration_id('workout_saved')




#     caption = build_confirmation_caption(workout_type, duration, 
#                                 intensity, note, dt) 

#     sent = await message.answer_photo(
#         photo=photo_id,
#         caption=caption,
#         reply_markup=verify_workout_keyboard(),
#         parse_mode='HTML'
#     )

#     await state.update_data(note=note, messages_to_delete=[sent.message_id])


# @router.callback_query(F.data == 'add_workout')
# async def add_workout(callback: types.CallbackQuery, state: FSMContext):
#     sent = await callback.message.answer(
#         '<b>Выбери тип тренировки:</b>',
#         reply_markup=get_workout_type_keyboard(),
#         parse_mode='HTML'
#     )

#     await state.set_state(WorkoutForm.type)
#     await state.update_data(messages_to_delete=[sent.message_id])
#     await callback.answer()


# @router.callback_query(WorkoutForm.type, F.data.startswith('type_'))
# async def choose_type(callback: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()

#     await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

#     workout_type = callback.data.replace('type_', '')
#     await state.update_data(type=workout_type)

#     sent = await callback.message.answer(
#         '⌛<b>Укажи длительность тренировки в минутах:</b>',
#         parse_mode='HTML'
#     )

#     await state.set_state(WorkoutForm.duration)
#     await state.update_data(messages_to_delete=[sent.message_id])
#     await callback.answer()


# @router.message(WorkoutForm.duration)
# async def choose_duration(message: types.Message, state: FSMContext):
#     data = await state.get_data()

#     await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
#     await message.delete()

#     if not validate_duration(message.text):
#         sent = await message.answer('Введи число от 1 до 245 минут: ')
#         await state.update_data(messages_to_delete=[sent.message_id])
#         return

#     await state.update_data(duration=int(message.text))

#     sent = await message.answer(
#         '<b>⚡️Укажи интенсивность тренировки от 1 до 5:</b>',
#         parse_mode='HTML'
#     )

#     await state.set_state(WorkoutForm.intensity)
#     await state.update_data(messages_to_delete=[sent.message_id])


# @router.message(WorkoutForm.intensity)
# async def choose_intensity(message: types.Message, state: FSMContext):
#     data = await state.get_data()

#     await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
#     await message.delete()

#     if not validate_intensity(message.text):
#         sent = await message.answer('Введи число от 1 до 5: ')
#         await state.update_data(messages_to_delete=[sent.message_id])
#         return

#     await state.update_data(intensity=int(message.text))

#     sent = await message.answer(
#         '<b>📝 Заметка (полезно для статистики):</b>',
#         reply_markup=skip_note_keyboard(),
#         parse_mode='HTML'
#     )

#     await state.set_state(WorkoutForm.note)
#     await state.update_data(messages_to_delete=[sent.message_id])


# @router.message(WorkoutForm.note, F.text)
# async def handle_note_input(message: types.Message, state: FSMContext, repo: Repository):
#     data = await state.get_data()

#     await safe_delete_messages(message.bot, message.chat.id, data['messages_to_delete'])
#     await message.delete()

#     await confirm_workout_data(message, state, message.text, repo)
#     await state.set_state(WorkoutForm.verify)


# @router.callback_query(WorkoutForm.note, F.data == 'skip_note')
# async def handle_skip_note(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
#     data = await state.get_data()

#     await safe_delete_messages(callback.bot, callback.message.chat.id, data['messages_to_delete'])

#     await confirm_workout_data(callback.message, state, None, repo)

#     await state.set_state(WorkoutForm.verify)
#     await callback.answer()
