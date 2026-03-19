from aiogram import Router, F, types

from keyboards import get_help_keyboard


router = Router()


async def send_help_message(message: types.Message):
    await message.delete()

    text = (f'<b>Вопросы или предложения? Я здесь, чтобы помочь!</b>\n\n'
            f'📲 Написать разработчику бота: @solvthis\n\n'
            # f'Полезная информация ▼'
    )
    await message.answer(
        text=text,
        parse_mode='HTML',
        reply_markup=get_help_keyboard()
    )


@router.message(F.text == '💬Помощь')
async def show_menu(message: types.Message):
    await send_help_message(message)


@router.callback_query(F.data == 'delete_help')
async def cancle_help(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()