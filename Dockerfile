FROM python:3.11-slim

WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app.py .
COPY result.txt .
COPY templates/ templates/

# Открываем порт
EXPOSE 5000

# Запускаем приложение
CMD ["python", "app.py"]
