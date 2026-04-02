from datetime import datetime
from utils import WorkoutConstants, DateConstants
from .constants import DateConstants


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


def parse_ru_datetime(text: str) -> str | None:
    try:
        parts = text.strip().split()

        if len(parts) != 4:
            return None
        
        day = int(parts[0])
        month = DateConstants.MONTHS_INPUT.get(parts[1].lower())
        year = int(parts[2])
        hour, minute = map(int, parts[3].split(':'))

        if not month:
            return None
        
        dt = datetime(year, month, day, hour, minute)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    
    except (ValueError, AttributeError):
        return None
    

def format_ru_date(date_str: str) -> str | None:
    try:
        fmt = '%Y-%m-%d %H:%M:%S' if len(date_str) > 10 else '%Y-%m-%d'
        dt = datetime.strptime(date_str.strip(), fmt)

        month_name = DateConstants.MONTHS.get(dt.month)
        if not month_name:
            return None

        return f'{dt.day} {month_name} {dt.year}'

    except (ValueError, AttributeError):
        return None
    

def progress_bar(percent: int) -> str:
    filled = percent // 10
    empty = 10 - filled
    bar = '█' * filled + '░' * empty
    return f'[{bar}] {percent}%'