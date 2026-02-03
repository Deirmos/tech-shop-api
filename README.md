# In Russian

# 🛒 TechShop E-Commerce API

[RU] Асинхронный бэкенд интернет-магазина техники. Проект реализует полный цикл работы магазина: каталог, корзина, заказы, оплата, уведомления по email.

## 🌟 Ключевые особенности

- **Async First**: FastAPI + SQLAlchemy 2.0 Async + aiosmtplib.
- **Order Logic**: валидация остатков, транзакционное создание заказа, возврат остатков при отмене.
- **Security**: JWT-аутентификация, хеширование паролей (bcrypt), роли User/Admin.
- **Soft Delete**: мягкое удаление категорий и товаров.
- **Email Engine**: HTML-письма через Jinja2.
- **RabbitMQ**: асинхронная отправка email через очередь, retry и DLQ.

## 🏗 Архитектура

Слойная архитектура (Service Layer):
- `routers/` — HTTP эндпоинты.
- `services/` — бизнес-логика.
- `models/` — модели БД (SQLAlchemy).
- `schemas/` — валидация данных (Pydantic).
- `worker/` — консюмер RabbitMQ для отправки email.

## 🧪 Тестирование

Тесты используют `pytest` и мокают отправку email.

Запуск:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -v
```

Важно: для тестов требуется `RABBITMQ_URL` в окружении (можно фиктивный), иначе `Settings()` не инициализируется.

## 🧰 Технологический стек

- FastAPI
- PostgreSQL + SQLAlchemy (Async)
- Alembic
- RabbitMQ (aio-pika)
- Jinja2
- Pydantic v2

## 📖 API Документация

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

## 🚀 Быстрый старт (локально)

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## 🐳 Docker

### 1. Подготовьте `.env.docker`

Пример:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ecommerce_db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/test_db
SECRET_KEY=change_me

MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_FROM=info@tech-shop.com
MAIL_PORT=2525
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

RABBITMQ_URL=amqp://rabbit:rabbit@rabbitmq:5672/
RABBITMQ_EMAIL_QUEUE=email.order_confirmation
RABBITMQ_EMAIL_EXCHANGE=email.exchange
RABBITMQ_RETRY_EXCHANGE=email.retry.exchange
RABBITMQ_DLQ_EXCHANGE=email.dlq.exchange
RABBITMQ_RETRY_QUEUE=email.order_confirmation.retry
RABBITMQ_DLQ_QUEUE=email.order_confirmation.dlq
RABBITMQ_RETRY_DELAY_SECONDS=30
RABBITMQ_MAX_RETRIES=5

DEBUG=True
```

### 2. Запуск

```bash
docker compose up --build
```

Будут подняты сервисы:
- `app` — API
- `db` — PostgreSQL
- `rabbitmq` — брокер + UI
- `worker` — консюмер RabbitMQ

RabbitMQ UI: http://localhost:15672 (логин/пароль: `rabbit` / `rabbit`).

## 🛣 Roadmap

- [x] Docker & Docker Compose
- [ ] Redis для кеширования
- [ ] CI/CD (GitHub Actions)

---

# In English

# 🛒 TechShop E-Commerce API

[EN] Modern asynchronous backend for a tech e-commerce store. It covers the full lifecycle: catalog, cart, orders, and email notifications.

## 🌟 Key Features

- **Async First**: FastAPI + SQLAlchemy 2.0 Async + aiosmtplib.
- **Order Logic**: transactional order creation with stock validation and restock on cancel.
- **Security**: JWT auth, bcrypt password hashing, User/Admin roles.
- **Soft Delete**: products/categories keep history intact.
- **Email Engine**: Jinja2 HTML templates.
- **RabbitMQ**: async email delivery with retry and DLQ.

## 🏗 Architecture

Service Layer pattern:
- `routers/` — HTTP endpoints.
- `services/` — business logic.
- `models/` — DB models (SQLAlchemy).
- `schemas/` — validation (Pydantic).
- `worker/` — RabbitMQ consumer for email.

## 🧪 Testing

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest -v
```

Note: tests expect `RABBITMQ_URL` in env (can be dummy) to initialize settings.

## 🧰 Tech Stack

- FastAPI
- PostgreSQL + SQLAlchemy (Async)
- Alembic
- RabbitMQ (aio-pika)
- Jinja2
- Pydantic v2

## 📖 API Docs

Swagger UI: http://127.0.0.1:8000/docs
ReDoc: http://127.0.0.1:8000/redoc

## 🚀 Quick Start (local)

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

## 🐳 Docker

### 1. Create `.env.docker`

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ecommerce_db
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/test_db
SECRET_KEY=change_me

MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_FROM=info@tech-shop.com
MAIL_PORT=2525
MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

RABBITMQ_URL=amqp://rabbit:rabbit@rabbitmq:5672/
RABBITMQ_EMAIL_QUEUE=email.order_confirmation
RABBITMQ_EMAIL_EXCHANGE=email.exchange
RABBITMQ_RETRY_EXCHANGE=email.retry.exchange
RABBITMQ_DLQ_EXCHANGE=email.dlq.exchange
RABBITMQ_RETRY_QUEUE=email.order_confirmation.retry
RABBITMQ_DLQ_QUEUE=email.order_confirmation.dlq
RABBITMQ_RETRY_DELAY_SECONDS=30
RABBITMQ_MAX_RETRIES=5

DEBUG=True
```

### 2. Run

```bash
docker compose up --build
```

Services:
- `app` — API
- `db` — PostgreSQL
- `rabbitmq` — broker + UI
- `worker` — RabbitMQ consumer

RabbitMQ UI: http://localhost:15672 (user/pass: `rabbit` / `rabbit`).

## 🛣 Roadmap

- [x] Docker & Docker Compose
- [ ] Redis caching
- [ ] CI/CD (GitHub Actions)
