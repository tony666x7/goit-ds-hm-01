# Використовуємо офіційний образ Python версії 3.9
FROM python:3.12-slim

# Встановлюємо необхідні залежності через pipenv
RUN pip install pipenv
COPY . /app
WORKDIR /app
RUN pipenv install --deploy --system

# Вказуємо команду для запуску додатку
CMD ["python", "Assistant_BotV2.2.py"]
