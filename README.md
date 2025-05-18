## Быстрый запуск (локально)

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

### 5. Запустите приложение

```bash
uvicorn src.api.main:app --reload 
```

---

### Доступ к API

После запуска сервер будет доступен по адресу:  
[http://127.0.0.1:8000](http://127.0.0.1:8000)

Документация Swagger UI:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
