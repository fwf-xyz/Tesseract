from aiogram import Router
from . import errors, get_design_id, start, menu, workout

router = Router()

router.include_routers(
                        errors.router,
                        start.router,
                        menu.router,
                        workout.router,
                        get_design_id.router
)
