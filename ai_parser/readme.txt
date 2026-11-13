pip install:

beautifulsoup4
selenium
vk_api
requests

--- НАСТРОЙКА ИИ-МОДУЛЯ (DeepSeek) ---
1. Зарегистрируйтесь на platform.deepseek.com
2. Перейдите в API Keys → Create new API key
3. Вставьте ключ в ai_module.py:
   DEEPSEEK_API_KEY = "sk-ваш_ключ_здесь"

--- СТРУКТУРА ---
bot.py          — VK-бот, точка входа
parse.py        — парсер Дзена
ai_module.py    — ИИ-анализ статей (DeepSeek API): достоверность, кликбейт, рубрика, пересказ
func_stop.py    — флаг остановки мониторинга
parsed_example.json — пример спарсированной статьи

--- КАК РАБОТАЕТ ИИ-МОДУЛЬ ---
После парсинга каждой статьи:
1. Текст из article.json отправляется в DeepSeek (deepseek-chat)
2. DeepSeek возвращает JSON с полями:
   - reliability_score (0-10)
   - is_clickbait (true/false)
   - is_fake (true/false)
   - category (рубрика)
   - summary (краткий пересказ)
   - explanation (комментарий)
3. Отчёт отправляется пользователю в VK

Нужен Chrome
Запуск через терминал (в папке со всеми файлами): python bot.py
