# TeamFinder

Платформа для поиска участников в командные IT-проекты. Пользователи публикуют проекты, вступают в чужие команды и указывают навыки в профиле.

## Функциональность

- Регистрация и авторизация по email
- Создание, редактирование и закрытие проектов
- Вступление/выход из проекта
- Личный профиль: аватар, контакты, ссылка на GitHub, описание
- Навыки пользователя: добавление с автодополнением, удаление
- Фильтрация участников по навыкам
- Пагинация списков проектов и участников

## Стек технологий

- Python 3.11+
- Django 5.2
- PostgreSQL
- Pillow (генерация аватаров)
- python-decouple (настройки через .env)
- Docker / docker-compose (база данных)

## Развёртывание

### 1. Клонировать репозиторий

```bash
git clone https://github.com/q1ota/team-finder-ad.git
cd team-finder-ad
```

### 2. Создать виртуальное окружение и установить зависимости

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Создать файл `.env` в корне проекта

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=teamfinder
DB_USER=teamfinder
DB_PASSWORD=teamfinder
DB_HOST=localhost
DB_PORT=5432
```

### 4. Запустить PostgreSQL через Docker

```bash
docker-compose up -d
```

### 5. Применить миграции и запустить сервер

```bash
python manage.py migrate
python manage.py runserver
```

### 6. (Опционально) Заполнить тестовыми данными

```bash
python manage.py seed_data
```

## Переменные окружения

| Переменная              | Описание                              | По умолчанию           |
|-------------------------|---------------------------------------|------------------------|
| `DJANGO_SECRET_KEY`     | Секретный ключ Django                 | обязательно            |
| `DJANGO_DEBUG`          | Режим отладки                         | `False`                |
| `DJANGO_ALLOWED_HOSTS`  | Разрешённые хосты через запятую       | `localhost,127.0.0.1`  |
| `DB_NAME`               | Имя базы данных                       | `teamfinder`           |
| `DB_USER`               | Пользователь БД                       | `teamfinder`           |
| `DB_PASSWORD`           | Пароль БД                             | `teamfinder`           |
| `DB_HOST`               | Хост БД                               | `localhost`            |
| `DB_PORT`               | Порт БД                               | `5432`                 |

## Автор

Разработчик: [q1ota](https://github.com/q1ota)  
Контакт: jonpork2027@gmail.com
