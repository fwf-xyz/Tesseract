# from aiogram import types, F, Router
# from aiogram.fsm.context import FSMContext


# from database import Repository


# @router.callback_query(F.data == 'history')
# async def set_distance_of_history(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
#     sent = await callback.message.answer(
#         '📅 Введи временной период всех тренировок в днях:'
#     )
    


#     await state.set_state(WorkoutHistoryForm.history)



# @router.message(WorkoutHistoryForm.history)





# @router.callback_query(WorkoutHistoryForm.viewing, F.data.startswith('page_history:'))










# # from aiogram.utils.keyboard import InlineKeyboardBuilder
# # from aiogram.types import InlineKeyboardButton




# # @router.callback_query(F.data == 'history')
# # async def set_distance_of_history(callback: types.CallbackQuery, state: FSMContext):
# #     day_distance = callback.from_user.date






# #     sent = await callback.message.answer(
# #         '📅 Введи временной период всех тренировок в днях:',
# #     )

# #     await state.set_state(WorkoutHistoryForm.history)
# #     await state.update_data(type_message_id=sent.message_id)
# #     await callback.answer()



# # @router.message(WorkoutHistoryForm.history)
# # async def handle_history_input(message: types.Message, state: FSMContext,
# #                                 repo: Repository):
# #     data = await state.get_data()

# #     await message.bot.delete_message(
# #         chat_id=message.chat.id,
# #         message_id=data['type_message_id']
# #     )

# #     await message.delete()

# #     user_id = message.from_user.id
# #     days = int(message.text)


# #     history = repo.workouts.get_history(user_id, days)

# #     if not history:
# #         await message.answer('За указанный период нет данных о тренировках.')
# #         await state.clear()
# #         return


# #     caption = '📅 <b>История тренировок за последние {} дней:</b>\n\n'.format(days)
# #     for number, workout in enumerate(history, start=1):

# #         dt = datetime.strptime(workout['created_at'], "%Y-%m-%d %H:%M:%S")
# #         date_str = "{} {} {:02d}:{:02d}".format(dt.day, 
# #                                                 MONTHS.get(dt.month), 
# #                                                 dt.hour, 
# #                                                 dt.minute
# #                                                 )

# #         caption += '<b>{}: {} - {} мин</b> \n<i>[{}]</i> \n<b>Дата:</b> {}\n\n'.format(
# #             number,
# #             WORKOUT_TYPES.get(workout['workout_type'], workout['workout_type']),
# #             str(workout['duration']),
# #             INTENSITY_LEVELS.get(workout['intensity'], workout['intensity']),
# #             date_str
# #         )


# #     photo_id = repo.users.paste_decoration_id('history')
# #     await message.answer_photo(photo=photo_id,
# #                             caption=caption ,
# #                             reply_markup=history_keyboard(),
# #                             parse_mode='HTML'
# #                             )


# #     await state.clear()





















# # def history_keyboard(page: int, page_count: int):
# #     builder = InlineKeyboardBuilder()
# #     limit = 5
# #     end = page * limit

# #     nav_buttons = []

# #     if page > 1:
# #         nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_history:{page-1}"))
    
# #     if end < page_count:
# #         nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"page_history:{page+1}"))

# #     builder.row(*nav_buttons)
# #     return builder.as_markup()




# # limit = 5

# # start_page = (page-1) * limit
# # end_page = page * limit


# # #caption = '📜 <b>Ваша История Тренировок За Последние {} Дней:</b>\n\n'.format(days)
# #     for number, workout in enumerate(history[start_page:end_page], start=start_page+1):

# #         dt = datetime.strptime(workout['created_at'], "%Y-%m-%d %H:%M:%S")
# #         date_str = "{} {} {:02d}:{:02d}".format(dt.day, 
# #                                                 MONTHS.get(dt.month), 
# #                                                 dt.hour, 
# #                                                 dt.minute
# #                                                 )

# #         caption += '<b>{}: {} - {} мин</b> \n<i>[{}]</i> \n<b>Дата:</b> {}\n\n'.format(
# #             number,
# #             WORKOUT_TYPES.get(workout['workout_type'], workout['workout_type']),
# #             str(workout['duration']),
# #             INTENSITY_LEVELS.get(workout['intensity'], workout['intensity']),
# #             date_str
# #         )







# # @router.callback_query(F.data.startswith("page_history:"))
# # async def paginate_history(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
# #     page = int(callback.data.split(":")[1])
# #     data = await state.get_data()
# #     days = data.get('history_days', 7)

# #     history = repo.workouts.get_history(callback.from_user.id, days)
# #     page_count = (len(history) + limit - 1) // limit

# #     if not history:
# #         await callback.message.edit_text('За указанный период нет данных о тренировках.')
# #         return

# #     caption = '📜 <b>Ваша История Тренировок За Последние {} Дней:</b>\n\n'.format(days)
# #     for number, workout in enumerate(history[(page-1)*limit:page*limit], start=(page-1)*limit+1):

# #         dt = datetime.strptime(workout['created_at'], "%Y-%m-%d %H:%M:%S")
# #         date_str = "{} {} {:02d}:{:02d}".format(dt.day, 
# #                                                 MONTHS.get(dt.month), 
# #                                                 dt.hour, 
# #                                                 dt.minute
# #                                                 )

# #         caption += '<b>{}: {} - {} мин</b> \n<i>[{}]</i> \n<b>Дата:</b> {}\n\n'.format(
# #             number,
# #             WORKOUT_TYPES.get(workout['workout_type'], workout['workout_type']),
# #             str(workout['duration']),
# #             INTENSITY_LEVELS.get(workout['intensity'], workout['intensity']),
# #             date_str
# #         )

# #     await callback.message.edit_text(caption, reply_markup=history_keyboard(page, page_count), parse_mode='HTML')









# # #    builder.add(InlineKeyboardButton(text="✏️ Редактировать",
# # #                                    callback_data="edit_history"
# # #                                    ))