# Festival Schedule App

Приложение для отображения расписания музыкального фестиваля с бегущей строкой и масштабированием.

## Структура
- `templates/index.html`: HTML-страница с фронтендом.
- `static/style.css`: Стили (опционально).
- `credentials.json`: Учетные данные Google Sheets API.
- `festival_schedule_app.py`: Flask-бэкенд.
- `bot.py`: Telegram-бот.
- `requirements.txt`: Зависимости.

## Настройка
1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
2. Настройте Google Sheets API:
   - Создайте таблицу "Festival Schedule".
   - В Google Cloud Console включите Sheets API, создайте Service Account, скачайте `credentials.json`.
   - Поделитесь таблицей с email Service Account.
3. Создайте Telegram-бот через BotFather, обновите `bot.py` с токеном.
4. Запустите Flask:
   ```bash
   python festival_schedule_app.py
   ```
5. Запустите Telegram-бот:
   ```bash
   python bot.py
   ```

## Развертывание
- Хостинг на Render.com:
  - Создайте репозиторий GitHub.
  - Подключите к Render, добавьте `credentials.json` как секрет.
  - Укажите команду: `python festival_schedule_app.py`.
- Обновите `bot.py` с URL сервера.

## Формат Google Таблицы
```
| Time  | MAIN | SUN | WOODZ | NEON | DARK |
|-------|------|-----|-------|------|------|
| 19:00 | DJ1  | DJ2 | DJ3   | DJ4  | DJ5  |
```