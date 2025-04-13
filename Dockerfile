# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем пользователя без прав root
RUN useradd -m myuser

# Копируем код приложения
COPY . .
RUN chown -R myuser:myuser /app

# Переключаемся на пользователя без прав root
USER myuser

# Открываем порт
EXPOSE 8000

# Запускаем приложение
CMD ["gunicorn", "-c", "config/gunicorn.conf.py", "src.main:app"] 