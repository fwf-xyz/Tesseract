# from datetime import datetime, timedelta

# from aiogram import types, F, Router

# from aiogram.fsm.context import FSMContext
# from states import WorkoutHistoryForm
# from keyboards import history_keyboard

# from database import Repository
# from utils import WORKOUT_TYPES, INTENSITY_LEVELS, MONTHS


# router = Router()


# @router.callback_query(F.data == 'history')
# async def show_history(callback: types.CallbackQuery, state: FSMContext):
#     sent = await callback.message.answer(
#         '📅 Введи временной период всех тренировок в днях:',
#     )

#     await state.set_state(WorkoutHistoryForm.history)
#     await state.update_data(type_message_id=sent.message_id)
#     await callback.answer()


# @router.message(WorkoutHistoryForm.history)
# async def handle_history_input(message: types.Message, state: FSMContext,
#                                 repo: Repository):
#     data = await state.get_data()

#     await message.bot.delete_message(
#         chat_id=message.chat.id,
#         message_id=data['type_message_id']
#     )

#     await message.delete()

#     user_id = message.from_user.id
#     days_count = int(message.text)
#     search_start_date = datetime.now() - timedelta(days=days_count)


#     history = repo.workouts.get_history(user_id, search_start_date)

#     if not history:
#         await message.answer('За указанный период нет данных о тренировках.')
#         await state.clear()
#         return


#     caption = '📅 <b>История тренировок за последние {} дней:</b>\n\n'.format(days_count)
#     for number, workout in enumerate(history, start=1):

#         dt = datetime.strptime(workout['created_at'], "%Y-%m-%d %H:%M:%S")
#         date_str = "{} {} {:02d}:{:02d}".format(dt.day, 
#                                                 MONTHS.get(dt.month), 
#                                                 dt.hour, 
#                                                 dt.minute
#                                                 )

#         caption += '<b>{}: {} - {} мин</b> \n<i>[{}]</i> \n<b>Дата:</b> {}\n\n'.format(
#             number,
#             WORKOUT_TYPES.get(workout['workout_type'], workout['workout_type']),
#             str(workout['duration']),
#             INTENSITY_LEVELS.get(workout['intensity'], workout['intensity']),
#             date_str
#         )


#     photo_id = repo.users.paste_decoration_id('history')
#     await message.answer_photo(photo=photo_id,
#                             caption=caption ,
#                             reply_markup=history_keyboard(),
#                             parse_mode='HTML'
#                             )


#     await state.clear()






