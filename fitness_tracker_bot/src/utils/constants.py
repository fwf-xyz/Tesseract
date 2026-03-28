class AgeConstants:
    MIN = 3
    MAX = 100
    CHILD_THRESHOLD = 12
    SENIOR_THRESHOLD = 80

class HeightConstants:
    MIN = 54
    MAX = 272

class WeightConstants:
    MIN = 20
    MAX = 635

class WorkoutConstants:
    MIN_DURATION = 1
    MAX_DURATION = 245
    MIN_INTENSITY = 1
    MAX_INTENSITY = 5
    TYPES = {
        'cardio':   '🏃 Кардио',
        'stretch':  '🧘 Растяжка',
        'strength': '💪 Силовая',
    }

class DateConstants:
        MONTHS = {
            1: 'января',  2: 'февраля', 3: 'марта',
            4: 'апреля',  5: 'мая',     6: 'июня',
            7: 'июля',    8: 'августа', 9: 'сентября',
            10: 'октября', 11: 'ноября', 12: 'декабря',
            422: 'техническая ошибка'
        }
        MONTHS_INPUT = {v: k for k, v in MONTHS.items()}

class ProfileConstants:
    GENDER_TYPES = {
        'man': 'Мужской',
        'woman': 'Женский'
    }

class GoalConstants:
    DEFAULT_STATUS = "in_progress"

    GOAL_STATUSES = {
        "in_progress": '⚡️ В процессе выполнения',
        "completed":  '🟢 Выполнена',
        "failed":   '🔴 НЕ выполнена',
        "partially_completed": '🟠 Выполнена частично'
    }






#нужно добавить сюда ITEMS_PER_PAGES из хендлера истории 