from aiogram import Router
from . import start, menu, workout

router = Router()

router.include_routers(
                        start.router,
                        menu.router,
                        workout.router
)
