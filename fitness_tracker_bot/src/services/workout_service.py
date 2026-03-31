from utils import WorkoutConstants, DateConstants

from database import Repository

from datetime import datetime 


def build_confirmation_caption(workout_type: str, duration: int, 
                                intensity: int, note: str | None, dt: datetime) -> str:
    date_str = "{} {} {:02d}:{:02d}".format(
        dt.day, DateConstants.MONTHS.get(dt.month, 422), dt.hour, dt.minute
    )
    return (
        f'<b>Подтверждение Тренировки:</b>\n\n'
        f'🏹 <b>Тип:</b> {workout_type}\n'
        f'⌛ <b>Длительность:</b> {duration} мин\n'
        f'<b>Интенсивность:</b> ⚡️{intensity}/{WorkoutConstants.MAX_INTENSITY}\n\n'
        f'<b>Заметка:</b>\n{note or "—"}\n\n'
        f'📅 <b>Дата:</b>\n{date_str}'
    )


async def save_workout(repo: Repository, user_id: int, data: dict) -> None:
    repo.workouts.save_workout(
        user_id,
        data.get('workout_type', 'Unknown'),
        data.get('duration', 0),
        data.get('intensity', 'Normal'),
        data.get('note'),
    )
