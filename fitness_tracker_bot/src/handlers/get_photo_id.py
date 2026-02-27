from aiogram import types, Router, F

start = False


if start == True:
    router = Router()
else:
    pass


@router.message(F.photo)
async def get_photo_id(message: types.Message):
    file_id = message.photo[-1].file_id
    await message.answer(f'file_id: {file_id}')