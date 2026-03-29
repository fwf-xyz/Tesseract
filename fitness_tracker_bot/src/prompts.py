from collections import defaultdict
from datetime import datetime


def _aggregate_workouts(workouts: list[dict]) -> str:
    if not workouts:
        return '  — тренировок не найдено'

    total = len(workouts)
    total_duration = sum(w['duration'] for w in workouts)
    avg_intensity = sum(w['intensity'] for w in workouts) / total

    by_week = defaultdict(lambda: {'count': 0, 'duration': 0, 'intensity': []})
    for w in workouts:
        dt = datetime.strptime(w['created_at'], '%Y-%m-%d %H:%M:%S')
        week_key = f'{dt.isocalendar()[0]}-W{dt.isocalendar()[1]:02d}'
        by_week[week_key]['count'] += 1
        by_week[week_key]['duration'] += w['duration']
        by_week[week_key]['intensity'].append(w['intensity'])

    weeks_text = '\n'.join([
        f'  • {week}: {v["count"]} тренировок | '
        f'{v["duration"]} мин | '
        f'интенсивность {sum(v["intensity"]) / v["count"]:.1f}'
        for week, v in sorted(by_week.items())
    ])

    by_type = defaultdict(lambda: {'count': 0, 'duration': 0, 'intensity': []})
    for w in workouts:
        t = w['workout_type']
        by_type[t]['count'] += 1
        by_type[t]['duration'] += w['duration']
        by_type[t]['intensity'].append(w['intensity'])

    by_type_text = '\n'.join([
        f'  • {t}: {v["count"]} раз | {v["duration"]} мин | '
        f'средняя интенсивность {sum(v["intensity"]) / v["count"]:.1f}'
        for t, v in by_type.items()
    ])

    notes = [w['notes'] for w in workouts if w['notes']]
    notes_text = '\n'.join(f'  — {n}' for n in notes[-10:]) or '  — заметок нет'

    return (
        f'Всего тренировок: {total}\n'
        f'Суммарное время: {total_duration} мин\n'
        f'Средняя интенсивность: {avg_intensity:.1f}\n\n'
        f'Динамика по неделям:\n{weeks_text}\n\n'
        f'По типам:\n{by_type_text}\n\n'
        f'Заметки пользователя:\n{notes_text}'
    )


def build_summary_prompt(
    profile: dict,
    goal: dict,
    workouts: list[dict],
    past_summaries: list[dict]
) -> str:

    workouts_text = _aggregate_workouts(workouts)

    past_summaries_text = ''
    if past_summaries:
        past_summaries_text = '\n\nПРЕДЫДУЩИЕ САММАРИ (учти динамику):\n' + '\n\n---\n'.join([
            f'[{s["created_at"]}]:\n{s["summary_text"]}'
            for s in past_summaries
        ])

    return (
        f'Ты — персональный фитнес-тренер с 10-летним опытом. '
        f'Ты профессионален, конкретен (и объективен, не нужно поддакивать человеку. оценивай с критической точки зрения), иногда с юмором, но никогда не теряешь суть. Отвечай от первого лица '
        f'Ты анализируешь реальные данные.\n\n'

        f'═══ ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ═══\n'
        f'Возраст: {profile.get("age")} лет\n'
        f'Пол: {profile.get("gender")}\n'
        f'Рост: {profile.get("height")} см\n'
        f'Вес: {profile.get("weight")} кг\n'
        f'Физиологические особенности: {profile.get("health_params") or "—"}\n\n'

        f'═══ ЦЕЛЬ И ДЕДЛАЙН ═══\n'
        f'Цель: {goal["goal"]}\n'
        f'Дата создания: {goal["created_at"]}\n'
        f'Дедлайн: {goal["deadline"]}\n\n'

        f'═══ ТРЕНИРОВКИ С ДАТЫ СОЗДАНИЯ ЦЕЛИ ═══\n'
        f'{workouts_text}'

        f'{past_summaries_text}\n\n'

        f'═══ СТРУКТУРА ОТВЕТА ═══\n'
        f'Ответь строго по этим пунктам, без отступлений:\n\n'
        f'1. 📊 ОБЩАЯ ОЦЕНКА ПЕРИОДА\n'
        f'   Коротко о том, как прошёл период в целом.\n\n'
        f'2. 💪 ЧТО ПОЛУЧАЕТСЯ ХОРОШО\n'
        f'   Конкретные сильные стороны на основе данных — без воды.\n\n'
        f'3. ⚠️ ЧТО НУЖНО УЛУЧШИТЬ\n'
        f'   Конкретные слабые места. Только то, что видно из данных.\n\n'
        f'4. 🎯 ПРОГРЕСС К ЦЕЛИ\n'
        f'   Насколько пользователь близок к своей цели и почему.\n\n'
        f'5. 🔥 ПЛАН НА СЛЕДУЮЩИЙ ПЕРИОД\n'
        f'   3-5 конкретных действия. Цифры, типы, частота.\n\n'
        f'6. 🥩 ПИТАНИЕ\n'
        f'   Можешь дать рекомендации по питанию, учитывая профиль пользователя.\n\n'
        f'7. 😄 ТРЕНЕРСКАЯ РЕМАРКА\n'
        f'   Одна фраза — лёгкий юмор или мотивация.\n\n'

        f'Правила: отвечай только на русском, используй только разметку HTML (все остальные лишние символы убери, Telegram поддерживает только <b>, <i>, <code>, <pre>, <a>). Опирайся на цифры из данных (используй больше данных цифр для аргументации, твои главные показатели - цифры). '
        f'СТРОГО: Не придумывай того, чего нет в данных. Интенсивность в тренировках по шкале от 1 до 5 включительно (такие параметры), минимальная и максимальная длительность тренировок от 1 до 240 минут'
    )