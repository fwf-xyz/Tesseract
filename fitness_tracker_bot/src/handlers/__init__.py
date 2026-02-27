from aiogram import Router
from . import start, menu, workout, get_photo_id

router = Router()

router.include_routers(
                        start.router,
                        menu.router,
                        workout.router,
                        get_photo_id.router
)
