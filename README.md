# praktikum_new_diplom
## Foodgram-project-react (grocery_assistant)
![Foodgram-project-react](https://github.com/2artem/foodgram-project-react/actions/workflows/main.yml/badge.svg)


Адреса развернутого приложения:
```
http://158.160.9.55

http://158.160.9.55

```
### Описание проекта:
Проект Foodgram продуктовый помощник - платформа для публикации рецептов. 

### О проекте:
В этом сервисе пользователи могут публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления 
одного или нескольких выбранных блюд.

### Начало

1.Настройка сервера.


Подключаемся к виртуальной машине с линукс.
ssh admin@158.160.9.55

обновим индекс менеджера пакетов apt
sudo apt update

обновим установленные в системе пакеты
sudo apt upgrade -y

установим систему контроля версий, утилиту для создания виртуального окружения и менеджер пакетов
sudo apt install python3-pip python3-venv git -y

установим Docker и docker-compose
# Установка утилиты для скачивания файлов
sudo apt install curl
# Эта команда скачает скрипт для установки докера
sudo curl -fsSL https://get.docker.com -o get-docker.sh
# Эта команда запустит его
sudo sh get-docker.sh

sudo apt remove docker docker-engine docker.io containerd runc

# Обновить список пакетов
sudo apt update

# Установить необходимые пакеты для загрузки через https
sudo apt install \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg-agent \
  software-properties-common -y

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
# В консоли должно вывестись ОК 

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

sudo apt update 

sudo apt install docker-ce docker-compose -y

sudo systemctl status docker





дадим доступ к сервису GitHub нашему серверу
сгенерируем ssh-ключ
ssh-keygen (Enter, плюс ввод создание пароля для ключа)

вывод ключа
cat ~/.ssh/id_rsa.pub

GitHub-> Settings->SSH and GPG keys->Add SSH key->добавить ключ его название





Перенесем файлы из проекта docker-compose.yaml и nginx/default.conf на сервер,
в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно,
так как на основании них и будут собраны все настройки проекта.
На сервере:
pwd   # /home/admin
mkdir nginx

На рабочем компьютере, в папке infra/:
копируем yaml
scp docker-compose.yml admin@158.160.9.55:/home/admin
scp nginx.conf admin@158.160.9.55:/home/admin/nginx







2. DevOps (Development Operations) — это методика увеличения скорости, качества и безопасности разработки.
Continuous Integration (англ. «непрерывная интеграция», сокращенно CI) состоит в том, чтобы после внесения изменений в любую часть кода проводилось тестирование не только того модуля, который был изменён, но и всего проекта.
GitHub Actions — это облачный сервис, инструмент для автоматизации процессов тестирования и деплоя проектов.
Для подключения GitHub Actions создана директория .github/workflows, а в ней — yml-файл.
В файле .yml декларативно описывается workflow, процесс автоматизации: пошаговые команды и условия их выполнения. 

Запушены докер-образы на DockerHub (по Dockerfile).
sudo docker build -t avchasovskikh/foodgram_frontend:latest .
sudo docker build -t avchasovskikh/foodgram_backend:latest .
sudo docker login -u avchasovskikh (пароль)
sudo docker push avchasovskikh/foodgram_frontend:latest
sudo docker push avchasovskikh/foodgram_backend:latest

Добавлены переменные окружения на GitHub Actions.
2artem/foodgram-project-react -> Settings -> Secrets -> Actions -> New repositiry secret:

* DOCKER_PASSWORD # пароль от DockerHub
* DOCKER_USERNAME # имя пользователя на DockerHub
* DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
* DB_NAME = postgres # имя базы данных
* POSTGRES_USER = postgres # логин для подключения к базе данных
* POSTGRES_PASSWORD = postgres # пароль для подключения к БД (установите свой)
* DB_HOST = db # название сервиса (контейнера)
* DB_PORT = 5432 # порт для подключения к БД 
* TELEGRAM_TO # id своего телеграм-аккаунта (@userinfobot)
* TELEGRAM_TOKEN - токен бота (@BotFather)
* HOST # ip-адрес сервера
* PASSPHRASE = # пароль от ssh-ключа, на сервере 
* USER = # логин пользователя на сервере, от ssh-ключа
* SSH_KEY # приватный ssh ключ (публичный должен быть на сервере)(cat ~/.ssh/id_rsa)














ПРоекту нужен суперюзер,
Рецепту нужны ингредиенты и теги, нужно их внести в БД либо загрузить фикстуры:

МОжете загрузить фиктсуры, что внутри, три юзера

superuser@mail.ru
adminuser@mail.ru
user@mail.ru

общий пароль
"allTestUsersPASS$!"











### Авторы

* **Фронтенд - Яндекс.Практикум**

* **Бекенд - Часовских Артем** [achasovskikh.ru](http://achasovskikh.ru)
