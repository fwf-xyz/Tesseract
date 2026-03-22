from datetime import datetime
from utils import WorkoutConstants, DateConstants


def build_confirmation_caption(workout_type: str, duration: int,
                                intensity: int, note: str | None, dt: datetime) -> str:
    date_str = "{} {} {:02d}:{:02d}".format(
        dt.day, DateConstants.MONTHS.get(dt.month), dt.hour, dt.minute
    )
    return (
        f'<b>Подтверждение Тренировки:</b>\n\n'
        f'🏹 <b>Тип:</b> {workout_type}\n'
        f'⌛ <b>Длительность:</b> {duration} мин\n'
        f'⚡️ <b>Интенсивность:</b> {intensity}/{WorkoutConstants.MAX_INTENSITY}\n\n'
        f'<b>Заметка:</b> {note or "—"}\n\n'
        f'📅 <b>Дата:</b>\n{date_str}'
    )