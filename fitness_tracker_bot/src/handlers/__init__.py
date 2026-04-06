from aiogram import Router
from . import errors, get_design_id, history, profile, start, menu, workout, stats, help, goals, friends, test

router = Router()

router.include_routers(
                        start.router,
                        menu.router,
                        friends.router,
                        workout.router,
                        goals.router,
                        history.router,
                        stats.router,
                        get_design_id.router,
                        profile.router,
                        errors.router,
                        help.router,
                        test.router
)
