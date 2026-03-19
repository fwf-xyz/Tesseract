from config import MAX_INTENSITY_LEVEL
from utils import MONTHS

from database import Repository

from datetime import datetime 






def build_confirmation_caption(workout_type: str, duration: int, 
                                intensity: int, note: str | None, dt: datetime) -> str:
    date_str = "{} {} {:02d}:{:02d}".format(
        dt.day, MONTHS.get(dt.month), dt.hour, dt.minute
    )
    return (
        f'<b>Подтверждение Тренировки:</b>\n\n'
        f'🏹 <b>Тип:</b> {workout_type}\n'
        f'⌛ <b>Длительность:</b> {duration} мин\n'
        f'⚡️ <b>Интенсивность:</b> {intensity}/{MAX_INTENSITY_LEVEL}\n\n'
        f'<b>Заметка:</b> {note or "—"}\n\n'
        f'📅 <b>Дата:</b>\n{date_str}'
    )

def validate_duration(text: str) -> bool:
    return text.isdigit() and 1 <= int(text) <= 245

def validate_intensity(text: str) -> bool:
    return text.isdigit() and 1 <= int(text) <= 5


async def save_workout(repo: Repository, user_id: int, data: dict) -> None:
    repo.workouts.save_workout(
        user_id,
        data.get('type', 'Unknown'),
        data.get('duration', 0),
        data.get('intensity', 'Normal'),
        data.get('note'),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )