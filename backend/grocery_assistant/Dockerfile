# Создать образ на основе базового слоя python (там будет ОС и интерпретатор Python)
FROM python:3.8-slim

# Создать директорию приложения app и выполнять из нее команды
WORKDIR /app

# Скопировать с локального компьютера файл зависимостей
# в директорию /app
COPY ./requirements.txt .

# Обновить pip
RUN pip install --upgrade pip

# Выполнить установку зависимостей внутри контейнера
RUN pip3 install -r ./requirements.txt --no-cache-dir

# Скопировать содержимое директории c локального компьютера
# в директорию /app.
COPY ./ .

# Выполнить запуск сервера разработки при старте контейнера
CMD ["gunicorn", "grocery_assistant.wsgi:application", "--bind", "0:8000" ]
