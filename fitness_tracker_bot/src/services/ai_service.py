import asyncio
import json
import logging

from google import genai
from google.genai import types
from faster_whisper import WhisperModel
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
model = WhisperModel("medium", device="cpu", compute_type="int8")

GEMINI_MODEL = "gemini-3.1-flash-lite-preview"
GEMINI_CONFIG = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(
        include_thoughts=False,
        thinking_level="high"
    ),
    temperature=0.1,
    top_p=0.95,
)


async def get_ai_analysis(prompt: str) -> str:
    def _call():
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=GEMINI_CONFIG
            )
            if response.text:
                return response.text
            return "Ошибка: Модель вернула пустой ответ."

        except Exception as e:
            logging.error(f"Ошибка при запросе к Gemini: {e}")
            return "Произошла ошибка при анализе данных. Попробуйте позже."

    return await asyncio.to_thread(_call)


def transcribe_audio(file_path: str) -> str:
    segments, _ = model.transcribe(file_path, language="ru")
    return " ".join([seg.text for seg in segments])


def process_workout_text(raw_text: str) -> dict:
    prompt = f"""
Пользователь надиктовал данные о тренировке голосовым сообщением.
Текст мог быть распознан с ошибками — опечатки, пропущенные слова, неверные окончания.

Текст: "{raw_text}"

Задачи:
1. Исправь ошибки распознавания речи, восстанови смысл даже если текст частично нечитаем
2. Извлеки данные тренировки — старайся угадать по контексту если что-то не сказано явно
3. В поле notes напиши краткую выжимку по тренировке: что делал, сколько, как себя чувствовал (заполняй от первого лица, не нужно использовать данные там, которые уже будут использоваться в JSON)

Типы тренировок строго: силовая, кардио, растяжка.
Интенсивность: число от 1 до 5 (если не сказано явно — оцени по контексту, например "устал" → 4, "легко" → 1-2).
Длительность: если сказано "час" → 60, "полтора часа" → 90, "полчаса" → 30 (должно быть число от 1 до 245).

ВАЖНО: даже если текст очень плохого качества — не ставь null без крайней необходимости,
лучше сделай разумное предположение на основе контекста.

Ответь ТОЛЬКО в формате JSON без лишнего текста. в workout_type может быть только 3 вида тренировок, которые ты должен записать на английском в значении словаря (cardio, strength, stretch):
{{
    "corrected_text": "исправленный текст",
    "workout_type": "тип тренировки",
    "duration": число в минутах или null,
    "intensity": число от 1 до 5 или null,
    "notes": "краткая выжимка тренировки для будущей обработки"
}}
"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=GEMINI_CONFIG
        )
        clean = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)

    except Exception as e:
        logging.error(f"Ошибка при обработке текста тренировки: {e}")
        return {
            "corrected_text": raw_text,
            "workout_type": None,
            "duration": None,
            "intensity": None,
            "notes": None
        }
    


def process_text_message(raw_text: str) -> dict:
    prompt = f"""
        Пользователь прислал текстовое сообщение с данными о тренировке.
        В тексте могут быть опечатки, сленг, сокращения, ошибки автозамены (Т9) или отсутствовать знаки препинания.

        Текст: "{raw_text}"

        Задачи:
        1. Исправь опечатки и ошибки, расставь знаки препинания и восстанови смысл, даже если текст написан сумбурно.
        2. Извлеки данные тренировки — старайся сделать вывод по контексту, если что-то не указано явно.
        3. В поле notes напиши краткую выжимку по тренировке: что делал, сколько, как себя чувствовал (заполняй от первого лица; не дублируй точные данные, которые уже вынесены в отдельные ключи JSON).

        Типы тренировок строго: силовая, кардио, растяжка.
        Интенсивность: число от 1 до 5 (если не сказано явно — оцени по контексту, например "убился в хлам" → 5, "на расслабоне" → 1-2).
        Длительность: переведи в минуты (например, "час" → 60, "полтора часа" → 90, "полчаса" → 30). Должно быть число от 1 до 245.

        ВАЖНО: даже если текст очень короткий, скомканный или непонятный — не ставь null без крайней необходимости, лучше сделай разумное предположение на основе контекста.

        Ответь ТОЛЬКО в формате JSON без лишнего текста. В поле workout_type может быть только 3 вида тренировок, которые ты должен записать строго на английском (cardio, strength, stretch):
        {{
            "corrected_text": "исправленный и читаемый текст сообщения",
            "workout_type": "тип тренировки (только cardio, strength или stretch)",
            "duration": число в минутах или null,
            "intensity": число от 1 до 5 или null,
            "notes": "краткая выжимка тренировки от первого лица для будущей обработки"
        }}
"""
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=GEMINI_CONFIG
        )
        clean = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(clean)

    except Exception as e:
        logging.error(f"Ошибка при обработке текста тренировки: {e}")
        return {
            "corrected_text": raw_text,
            "workout_type": None,
            "duration": None,
            "intensity": None,
            "notes": None
        }