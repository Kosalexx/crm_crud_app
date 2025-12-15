CRM CRUD API

Простое приложение на FastAPI для работы с CRM (CRUD).

# CRM CRUD API

<p style="text-align:center"> 
	<kbd>
		<image src="src/core/static/logo.png" alt="logo" width="140"/>
	</kbd>
</p>

API на FastAPI для работы с CRM-системой: управление клиентами, заказами и платежами, интеграция с внешними CRM (например RetailCRM).

---

## Содержание

- [Технологии](#технологии)
- [Описание](#описание)
- [Установка и запуск](#установка-и-запуск)
- [Тестирование](#тестирование)
- [Основные моменты реализации](#основные-моменты-реализации)
- [Трудности](#трудности)
- [Авторы](#авторы)


---

## Технологии

**Язык и библиотеки:**

[![Python](https://img.shields.io/badge/-python_3.13^-464646?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/-FastAPI-464646?logo=fastapi)](https://fastapi.tiangolo.com/)
[![httpx](https://img.shields.io/badge/-httpx-464646?logo=python)](https://www.python-httpx.org/)
[![pydantic](https://img.shields.io/badge/-pydantic-464646?logo=pydantic)](https://docs.pydantic.dev/)
[![uvicorn](https://img.shields.io/badge/-uvicorn-464646?logo=uvicorn)](https://www.uvicorn.org/)
[![colorlog](https://img.shields.io/badge/-colorlog-464646?logo=python)](https://pypi.org/project/colorlog/)

**Инструменты для тестирования:**

[![pytest](https://img.shields.io/badge/-pytest-464646?logo=pytest)](https://docs.pytest.org/)
[![pytest-asyncio](https://img.shields.io/badge/-pytest_asyncio-464646?logo=pytest)](https://github.com/pytest-dev/pytest-asyncio)
[![respx](https://img.shields.io/badge/-respx-464646?logo=python)](https://github.com/lundberg/respx)

**Контейнеризация:**

[![Docker](https://img.shields.io/badge/-Docker-464646?logo=docker)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-464646?logo=docker)](https://docs.docker.com/compose/)

---

## Описание

Это REST API, реализованное на FastAPI, предназначенное для взаимодействия с CRM-системой. Основные возможности:

- Получение и фильтрация списка клиентов;
- Создание клиента в CRM;
- Получение и создание заказов;
- Создание оплат по заказам;

Документация OpenAPI доступна по пути `/docs` при запуске сервера.

---

## Установка и запуск

<details><summary>Требования</summary>

Для локального запуска рекомендуется установить Docker и Docker Compose. Если вы используете `uv` — используйте его для управления зависимостями. Также необходим Python 3.13+.

Проверить установку:

```bash
docker --version && docker-compose --version
```

Так же должен быть выполнен подготовительный этап регистрации в RetailCRM
- Зарегистрируйте тестовую систему RetailCRM
- Войдите в систему и создайте API ключ для интеграции:
- Перейдите в меню Настройки → Интеграция → Добавить.
- Сгенерируйте новый API ключ, который будет использоваться для аутентификации запросов.
</details>

### Локальный запуск (рекомендуем для разработки)

1. Клонируйте репозиторий и перейдите в директорию проекта:

```bash
git clone <REPO_URL>
cd crm_crud_app
```

2. Установите зависимости:

Используя `uv`:

```bash
uv sync --dev

```

3. Создайте файл окружения `.env` и заполните необходимые переменные (см. `env.example`):

Обязательные переменные для интеграции RetailCRM:

- `RETAIL_CRM_API_KEY` — ваш API-ключ;
- `RETAIL_CRM_API_PREFIX` — префикс API (например по умолчанию `/api/v5`);
- `RETAIL_CRM_URL` — базовый URL RetailCRM (опционально для тестов).

4. Запуск приложения в режиме разработки:

```bash
python3 main.py
```

API будет доступен по адресу `http://127.0.0.1:8081/` (порт 8081 - по умолчанию).

### Запуск через Docker Compose

```bash
docker-compose up -d --build
```

Приложение будет доступно на `http://localhost:8081/`. Остановить и удалить контейнеры:

```bash
docker-compose down
# добавить -v для удаления томов: docker-compose down -v
```

---

## Тестирование

- Тесты используют `pytest`, `pytest-asyncio` и `respx` для моков HTTP. Файл `env.test` содержит значения окружения, которые используются при тестировании (загрузка настраивается через `pytest.ini` и плагин `pytest-dotenv`).
- Запуск тестов:

```bash
pytest -q
```

-- Запуск отдельного файла:

```bash
pytest tests/test_retailcrm_service.py -q
```


---

## Основные моменты реализации

- Проект разделён на модули: `api` (роуты FastAPI), `services.integrations` (абстрактный `BaseCRMService` и конкретные реализации, например `RetailCRMService`), `schemas` (pydantic-модели для валидации входных и выходных данных) и `core` (настройки, логирование).
- `BaseCRMService` содержит общую логику HTTP-запросов (`_make_request`) и объявляет абстрактные методы для подготовки параметров, тела и заголовков. Это позволяет легко добавлять новые интеграции.
- `RetailCRMService` реализует поведение для RetailCRM: добавление `apiKey` в параметры запроса, преобразование DTO-фильтров в формат RetailCRM, установку `Content-Type: application/x-www-form-urlencoded` для POST-запросов и валидацию ответов по полю `success`.
- Для DTO/валидации используется `pydantic` (модели в `src/schemas`), в тестах проверяются как парсинг полей (например телефонов), так и поведение сервисов.
- Тесты написаны с использованием `pytest`, `pytest-asyncio` и `respx` для мокирования HTTP. Конфигурация тестов и переменные окружения (файл `env.test`) описаны в `pytest.ini`.

---

## Трудности

При интеграции с RetailCRM пришлось решить несколько нестандартных и тонких мест:

- Специфичный формат передачи фильтров: RetailCRM ожидает GET-параметры в виде вложенных ключей с PHP-подобной нотацией, например:

```text
filter[name]=John
filter[phones][][number]=123
filter[address][city]=Minsk
```

Чтобы сделать это удобно для использования в коде, реализована функция преобразования, которая рекурсивно «сплющивает» вложенные словари и списки в такую нотацию.

- Формат тела POST-запросов: RetailCRM часто ожидает данные в виде form-urlencoded, где значение поля (например `customer`) — это JSON-строка. Поэтому для создания клиента/заказа мы отправляем `data={'customer': json.dumps(customer_data)}` с заголовком `Content-Type: application/x-www-form-urlencoded`.

---

## Авторы

- Aliaksei Kastsiuchonak — основная реализация и тесты (https://github.com/Kosalexx)

---

