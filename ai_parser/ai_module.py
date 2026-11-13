import json
import requests

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = "КЛЮЧ СЮДА"

SYSTEM_PROMPT = """Ты — аналитик новостного контента.
Твоя задача: проанализировать текст статьи и вернуть ответ СТРОГО в формате JSON.

Тебе нужно определить:
1. "reliability_score" — оценка достоверности от 0 до 10 (0 = фейк/кликбейт, 10 = полностью достоверно)
2. "is_clickbait" — true/false, является ли заголовок кликбейтом
3. "is_fake" — true/false, содержит ли статья признаки фейка
4. "category" — тематическая рубрика из списка: Технологии, Здоровье, Политика, Экономика, Спорт, Культура, Наука, Общество, Криминал, Другое
5. "summary" — краткий пересказ статьи (2-3 предложения)
6. "explanation" — короткое объяснение оценки достоверности (1-2 предложения)

Отвечай ТОЛЬКО JSON-объектом, без лишнего текста, без markdown-форматирования."""


def analyze_article(article_path: str = "article.json") -> dict | None:
    """
    Читает статью из файла, отправляет в DeepSeek API, возвращает словарь с анализом.
    Возвращает None при ошибке.
    """
    try:
        with open(article_path, "r", encoding="utf-8") as f:
            article_text = f.read().strip()
    except FileNotFoundError:
        print(f"[AI] Файл {article_path} не найден.")
        return None
    except Exception as e:
        print(f"[AI] Ошибка чтения файла: {e}")
        return None

    if not article_text:
        print("[AI] Файл статьи пуст.")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }

    payload = {
        "model": "deepseek-chat",
        "max_tokens": 1000,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Проанализируй следующую статью:\n\n{article_text[:8000]}"}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("[AI] Таймаут при обращении к API.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[AI] Ошибка запроса к API: {e}")
        return None

    # Парсим ответ (формат OpenAI-совместимый)
    try:
        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()
        # Убираем возможные markdown-обёртки ```json ... ```
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()
        result = json.loads(raw_text)
        return result
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"[AI] Ошибка парсинга ответа API: {e}")
        return None


def format_report(analysis: dict, url: str) -> str:
    """
    Форматирует результат анализа в читаемое сообщение для VK-бота.
    """
    if analysis is None:
        return f"⚠️ Не удалось проанализировать статью.\nСсылка: {url}"

    score = analysis.get("reliability_score", "?")
    is_fake = analysis.get("is_fake", False)
    is_clickbait = analysis.get("is_clickbait", False)
    category = analysis.get("category", "Другое")
    summary = analysis.get("summary", "Пересказ недоступен.")
    explanation = analysis.get("explanation", "")

    if isinstance(score, (int, float)):
        if score >= 7:
            reliability_emoji = "✅"
        elif score >= 4:
            reliability_emoji = "⚠️"
        else:
            reliability_emoji = "❌"
    else:
        reliability_emoji = "❓"

    fake_line = "🚨 Признаки фейка обнаружены" if is_fake else "✔️ Признаков фейка не обнаружено"
    clickbait_line = "🎣 Кликбейтный заголовок" if is_clickbait else "✔️ Заголовок не кликбейт"

    report = (
        f"📰 Рубрика: {category}\n"
        f"{reliability_emoji} Достоверность: {score}/10\n"
        f"{fake_line}\n"
        f"{clickbait_line}\n\n"
        f"📝 Краткий пересказ:\n{summary}\n\n"
        f"💬 Комментарий: {explanation}\n\n"
        f"🔗 {url}"
    )
    return report
