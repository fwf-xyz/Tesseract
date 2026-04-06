from datetime import datetime
from database import Repository

from utils import format_ru_date
import asyncio


async def check_deadlines(bot, repo: Repository):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = repo.goals.get_overdue_goals(now)

    for goal_id, user_id, goal, deadline, created_at in rows:
        try:
            text = (
                f"🔔 <b>Дедлайн по цели истёк!</b>\n\n"
                f'<b>Пора обновить статус своей цели:</b>\n'
                f'<blockquote>'
                f"🎯 <b>Цель:</b> {goal}\n\n"
                f"<b>Поставлена</b>: {format_ru_date(created_at)}\n"
                f"📅 <b>Дедлайн</b>: {format_ru_date(deadline)}"
                f'</blockquote>'
            )
            await bot.send_message(user_id, text=text, parse_mode='HTML')
            repo.goals.set_overdue_goal_statys(goal_id)

        except Exception as e:
            print(f"Ошибка отправки user_id={user_id}: {e}")


async def deadline_scheduler(bot, repo: Repository):
    while True:
        await check_deadlines(bot, repo)
        await asyncio.sleep(1800)
