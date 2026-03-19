from aiogram import Router
from . import errors, get_design_id, history, start, menu, workout, stats, help

router = Router()

router.include_routers(
                        start.router,
                        menu.router,
                        workout.router,
                        history.router,
                        stats.router,
                        get_design_id.router,
                        errors.router,
                        help.router
)
