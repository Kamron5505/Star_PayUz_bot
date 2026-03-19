# Подготовка бота к хостингу

## Локальный запуск

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Создай `.env` файл (скопируй из `.env.example`):
```bash
cp .env.example .env
```

3. Заполни `.env` файл своими данными:
```
BOT_TOKEN=your_token_here
ADMIN_IDS=123456789
ADMIN_LOGIN=your_login
ADMIN_PASSWORD=your_password
```

4. Запусти бота:
```bash
python bot.py
```

## Развертывание на Heroku

1. Установи Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli

2. Логинись в Heroku:
```bash
heroku login
```

3. Создай приложение:
```bash
heroku create your-app-name
```

4. Установи переменные окружения:
```bash
heroku config:set BOT_TOKEN=your_token_here
heroku config:set ADMIN_IDS=123456789
heroku config:set ADMIN_LOGIN=your_login
heroku config:set ADMIN_PASSWORD=your_password
```

5. Загрузи код на Heroku:
```bash
git push heroku main
```

6. Проверь логи:
```bash
heroku logs --tail
```

## Развертывание на других хостингах

### VPS (Ubuntu/Debian)

1. Установи Python 3.11+:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

2. Клонируй репозиторий:
```bash
git clone your-repo-url
cd star_payuz_bot
```

3. Создай виртуальное окружение:
```bash
python3.11 -m venv venv
source venv/bin/activate
```

4. Установи зависимости:
```bash
pip install -r requirements.txt
```

5. Создай `.env` файл и заполни его

6. Запусти бота в фоне (используя systemd или screen):
```bash
# Используя screen
screen -S bot
python bot.py

# Или используя systemd (создай /etc/systemd/system/star-payuz.service)
```

### Docker

1. Создай `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

2. Создай `.dockerignore`:
```
__pycache__
*.pyc
.env
.git
.gitignore
*.db
```

3. Собери и запусти контейнер:
```bash
docker build -t star-payuz-bot .
docker run -e BOT_TOKEN=your_token -e ADMIN_IDS=123456789 star-payuz-bot
```

## Важные файлы

- `requirements.txt` - зависимости Python
- `.env.example` - пример переменных окружения
- `.gitignore` - файлы, которые не загружаются в Git
- `Procfile` - для Heroku
- `runtime.txt` - версия Python для Heroku

## Переменные окружения

Все чувствительные данные должны быть в переменных окружения:
- `BOT_TOKEN` - токен бота
- `ADMIN_IDS` - ID администраторов (через запятую)
- `ADMIN_LOGIN` - логин администратора
- `ADMIN_PASSWORD` - пароль администратора
- `CHANNEL_ID` - ID канала
- `CARD_NUMBER` - номер карты
- `CARD_OWNER` - владелец карты
- `CARD_PHONE` - телефон владельца

## Безопасность

1. Никогда не коммитьте `.env` файл
2. Используйте сильные пароли
3. Регулярно обновляйте зависимости
4. Используйте HTTPS для всех соединений
5. Ограничивайте доступ к базе данных

## Мониторинг

Рекомендуется использовать:
- Sentry для отслеживания ошибок
- Prometheus для метрик
- ELK Stack для логов
