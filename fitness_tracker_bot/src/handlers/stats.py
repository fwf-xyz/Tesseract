from aiogram import types, Router, F

from aiogram.fsm.context import FSMContext
from states import StatsForm

from services import get_ai_analysis
from keyboards import get_stats_keyboard, save_ai_summary_keyboard
from utils import safe_delete_messages

from database import Repository

from utils import WorkoutConstants


router = Router()


@router.callback_query(F.data == "stats")
async def start_cmd(callback: types.CallbackQuery, state: FSMContext, repo: Repository):
    history = repo.workouts.get_history(callback.from_user.id, 7)

    quantity_workouts = len(history)
    avg_intensivity = round(
        sum(int(row['intensity']) for row in history) / quantity_workouts,
        1
    )

    avg_workouts_duration = round(
        sum(int(row['duration']) for row in history) / quantity_workouts,
        1
    )


    photo_id = repo.users.paste_decoration_id('stats')
    caption = ( 
                f'<b>🔽 Статистика За 7 Дней</b>\n\n'
                f'<b>Кол-во тренировок:</b> 🏌️‍♀️{quantity_workouts}\n\n'
                f'<b>📊Средние значения:</b>\n'
                f'<b>Интенсивность:</b> ⚡️{avg_intensivity}/{WorkoutConstants.MAX_INTENSITY}\n'
                f'<b>Длительность:</b> ⏳{avg_workouts_duration} (мин.)'
    )

    sent = await callback.message.answer_photo(
        photo=photo_id,
        caption=caption,
        reply_markup=get_stats_keyboard(),
        parse_mode='HTML'    
    )

    await state.set_state(StatsForm.weekly_stats)
    await state.update_data(messages_to_delete=[sent.message_id])
    await callback.answer()



@router.callback_query(StatsForm.weekly_stats, F.data == 'close_stats')
async def cancel_history(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    safe_delete_messages(callback.bot,
                        callback.message.chat.id,
                        data['messages_to_delete'])
    await state.clear()






JSON = """Вот данные тренировок пользователя (формат: агрегаты + CSV)

Портрет пользователя:
пол: мужской
рост: 178
вес: 81
возраст: 19

физиологические особенности: --

цель: похудеть на 5 кг за 1 месяц

Период: 2026-03-03 — 2026-03-07
Всего записей: 21 (1 аномалия исключена: duration=666)
Тренировок в анализе: 20

Средняя длительность: 49.7 мин
Средняя интенсивность: 3.0/5

По типам:
- Силовые: 9 сессий, avg 45.9 мин, интенс. 3.0
- Растяжка: 7 сессий, avg 56.6 мин, интенс. 3.1
- Кардио: 4 сессий, avg 46.3 мин, интенс. 2.8

Детальные записи (CSV):
workout_type,duration,intensity,date
strength,50,2,2026-03-03
cardio,15,1,2026-03-03
strength,50,5,2026-03-03
strength,60,4,2026-03-03
cardio,56,1,2026-03-03
strength,80,3,2026-03-03
strength,12,3,2026-03-03
stretch,56,4,2026-03-03
strength,15,1,2026-03-03
stretch,67,4,2026-03-03
stretch,90,2,2026-03-03
stretch,20,2,2026-03-03
stretch,78,3,2026-03-07
cardio,46,4,2026-03-07
strength,89,5,2026-03-07
strength,56,3,2026-03-07
stretch,45,3,2026-03-07
stretch,40,4,2026-03-07
cardio,68,5,2026-03-07
strength,1,1,2026-03-07

Задача: выяви паттерны и дисбаланс нагрузки, дай 3 конкретные рекомендации.
"""

prompt = f"""Ты — высококвалифицированный персональный фитнес-тренер с 10-летним стажем. Твоя специализация — доказательный фитнес и работа с данными (Data-Driven Coaching).

ЗДЕСЬ СОЗДАЙ ПРОЦЕНТНУЮ ДОРОЖКУ ДОСТИЖЕНИЯ ЦЕЛИ ЧЕРЕЗ СИМВОЛЫ, которые легко различить глазом (возможный максимум - 100%). Символы должны быть логично подобраны (если процентов 0, следовательно и я заполнения тоже ноль. НЕ ИСПОЛЬЗУЙ КРУГЛЫЕ ЭМОДЗИ). Назови заголовок: 'Процент достижения цели', добавь двоеточие и после него: новая строка: 🎯 + поставленную цель (бери из прикрепленного JSON). Каких-то дополнительных комментариев не нужно. Отдели символами от остального анализа ниже, но чтобы было удобно читать на телефоне + если текст будет длинным, то лучше перенеси его на новую строку (для более удобного чтения на телефоне), для отделения используй с таким количеством символов: '---------------------------'

# СИТУАЦИЯ И КОНТЕКСТ
У пользователя есть история тренировок за прошлый период в формате JSON. Цель пользователя: достичь значимого прогресса за 1 месяц.
Входные данные: {JSON}

# ЗАДАЧА
Проанализируй текущие показатели пользователя, выяви скрытые закономерности и разработай конкретный план действий на ближайшие 4 недели.

# ПРАВИЛА И ОГРАНИЧЕНИЯ
1. Честность превыше всего: если цель нереалистична за 30 дней, прямо укажи на это и предложи выполнимый срок.
2. Объективность: строй выводы только на цифрах из предоставленного файла (длительность, частота, веса), избегай общих советов.
3. Формат "Actionable": план должен содержать конкретные дни недели и параметры нагрузки.
4. Стиль: профессиональный, ясный, но при этом дружелюбный и мотивирующий. 
5. Техническое: без вступлений и приветствий. Не используй символы разметки (* # _), используй только эмодзи для структуры.

# ПРИМЕР ОЖИДАЕМОГО СТИЛЯ АНАЛИЗА
📊 Анализ: Средняя длительность тренировки 42 мин. Наблюдается спад интенсивности по средам (на 15% ниже среднего).
⚠️ Ошибки: 1. Избыток кардио (65% времени) при цели "рост мышц". 2. Пропуск тренировок ног (всего 1 сессия за 2 недели).

# СТРУКТУРА ОТВЕТА
📊 Анализ (аномалии, разброс длительности, дисбаланс типов нагрузки)
⚠️ Главные ошибки (2 пункта с конкретными цифрами)
🏁 Реалистичная цель (с обоснованием сроков)
📅 План по дням:
Пн/Ср/Пт: [тип + длительность + фокус]
Вт/Чт: [тип + длительность]
Сб: [тип]
Вс: отдых

📈 Прогрессия (как меняется нагрузка от 1-й к 4-й неделе)
💪 Силовые (сплит + подходы/повторения)
🥩 Питание (калораж, белок, 1 ключевой совет)

ВАЖНО: твой ответ не должен отличаться при повторных запросах с тем же JSON. Выдели итоговые заголовки HTML разметкой (жирный текст). Если используешь иностранные выражения, пиши в скобках перевод на русский. Не используй сложные термины без объяснения. Если видишь, что данных недостаточно для конкретных рекомендаций, прямо скажи об этом и предложи, что нужно отслеживать дополнительно.

Весь текст до двоеточия должен быть выделен жирным текстом HTML ВСЕГДА.
"""



# stats_ai_text = get_ai_analysis(prompt)
# def put_promt_ai


@router.callback_query(F.data == "ai_summary")
async def show_stats(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('Генерирую аналитику... ⌛')

    stats_ai_text = get_ai_analysis(prompt)

    sent = await callback.message.answer(
        text=stats_ai_text,
        parse_mode='HTML'
        )

    sent2 = await callback.message.answer(
        text='Сохранить ИИ-саммари в историю?',
        reply_markup=save_ai_summary_keyboard(),
        parse_mode='HTML'
        )
    
    state.update_data(ai_summary_text=stats_ai_text)
    await state.update_data(
    ai_summary_text=stats_ai_text,
    messages_to_delete=[sent.message_id, sent2.message_id]
)

