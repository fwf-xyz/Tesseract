from google import genai
from google.genai import types
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

import logging

def get_ai_analysis(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(
                    include_thoughts=False,
                    thinking_level="high"
                ),
                temperature=0.1,
                top_p=0.95,
            )
        )
        if response.text:
            return response.text
        return "Ошибка: Модель вернула пустой ответ."
        
    except Exception as e:
        logging.error(f"Ошибка при запросе к Gemini: {e}")
        return "Произошла ошибка при анализе данных. Попробуйте позже."