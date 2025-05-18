## Инструкция по запуску

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/abdulxakimbay/library-api.git
cd library-api
```

### 2. Создайте виртуальное окружение и активируйте его

```bash
python -m venv venv
source venv/bin/activate       # для Linux/Mac
venv\Scripts\activate          # для Windows
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Создайте .env файл в корне проекта и заполните его

Переменные из .env.example:
```bash
SECRET_KEY=put_here_your_secret_key
DB_LINK=postgresql+asyncpg://YOUR_DB_USERNAME:YOUR_DB_PASSWORD@localhost:5432/YOUR_DB_NAME
TEST_DB_LINK=sqlite+aiosqlite:///./YOUR_TEST_DB_NAME.db
```

### 5. Запустите тесты

```bash
pytest tests
```

### 6. Запустите приложение

```bash
uvicorn src.api.main:app --reload 
```

---

### Доступ к API

После запуска сервер будет доступен по адресу:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Документация Swagger UI:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



## Структура проекта

```
library-api/
├── src/
│   ├── api/                      # Основное FastAPI-приложение
│   │   ├── main.py               # Точка входа для запуска FastAPI
│   │   ├── auth.py               # Аутентификация и авторизация
│   │   ├── books.py              # Эндпоинты, связанные с книгами
│   │   ├── borrowed_books.py     # Эндпоинты, связанные с выданными книгами
│   │   ├── readers.py            # Эндпоинты, связанные c читателями
│   │   └── oauth_scheme.py       # OAuth2
│
│   ├── migrations/               # Alembic миграции базы данных
│   │   ├── versions/             # Версии миграций
│   │   ├── env.py                # Конфигурация Alembic
│   │   └── script.py.mako        # Шаблон для миграций
│
│   ├── config.py                 # Конфигурация приложения
│   ├── db.py                     # Подключение к базе данных
│   ├── models.py                 # SQLAlchemy модели
│   └── serializers.py            # Pydantic-схемы
│
├── tests/                        # Тесты проекта
│
├── .env                          # Переменные окружения
├── .env.example                  # Пример .env файла
├── requirements.txt              # Список зависимостей pip
├── alembic.ini                   # Конфигурация Alembic
└── README.md                     # Документация проекта
```



## Объяснение бизнес логики

### Первое

Требование: Книгу можно выдать, только если есть доступные экземпляры (количество экземпляров > 0). При выдаче количество экземпляров уменьшается на 1.

Решение: При обращении POST-запросом в `/borrowed_books`, запрашивается у БД книга по его ID. В случае поле quantity <= 0: `HTTPException(status_code=400, detail="Book is out of stock.")`, иначе добавляется новая информация в borrowed_books, а в поле quantity у объекта book отнимается единица. 

### Второе

Требование: Один читатель не может взять более 3-х книг одновременно.

Решение: При обращении POST-запросом в `/borrowed_books`, у таблицы borrowed_books запрашиваются все объекты у которых return_date не указан или указан, но оно ещё не наступило. В случае если таких объектов окажется больше или равно трём: 
```
HTTPException(
            status_code=400,
            detail="The reader has already taken the maximum number of books (3) and has not returned them.",
        )
```

### Третье

Требование: Нельзя вернуть книгу, которая не была выдана этому читателю или уже возвращена.

Решение: Книга считается возвращенной, в случае если указан return_date и оно наступило. return_date указывается через PUT запрос к `/borrowed_books`. Таким образом, невозможно изменить return_date у объекта borrowed_book, которого нет. 



## Описание реализации аутентификации

При регистрации `/auth/sign-up` и при логине `/auth/sign-in` выдаются два токена: Refresh Token (длительность: 3 дня) и Access Token (длительность: 30 минут). При истечении Access Token нужно обратиться к `/auth/token` передав Refresh Token в JSON формате и получить новый Access Token. Во всех последующих запросах на любые эндпоинты (кроме первых трёх описанных ранее) нужно передавать Access Token в заголовке Authorization через Bearer.
Для создания и проверки токенов используется библиотека pyjwt (за простоту в использовании), а в качестве алгоритма шифрования: HS256.



## Творческая часть

Стоит добавить новую таблицу `reserved_books` с полями: id, reader_id, book_id, reservation_date. При попытке взять книгу, если экземпляров нет - создается запись в reserved_books и при возврате этой книги другим читателем, проверяется наличие резерва. Если резерв есть, то книга забронируется новым читателем.
