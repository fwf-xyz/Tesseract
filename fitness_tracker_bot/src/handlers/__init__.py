from aiogram import Router
from . import errors, get_design_id, history, start, menu, workout

router = Router()

router.include_routers(
                        start.router,
                        menu.router,
                        workout.router,
                        history.router,
                        get_design_id.router,
                        errors.router,
)
