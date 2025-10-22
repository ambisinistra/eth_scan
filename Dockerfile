FROM python:3.11-slim

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
# Копируем код приложения
COPY app_input.py utils.py .env ./
COPY templates/ templates/

# Открываем порт
EXPOSE 5000

# Запускаем приложение
CMD ["python", "app_input.py"]
