# ТЗ: 4 новые фичи маркетплейса

Пишешь сам. Ниже — что должно получиться, а не как это набирать.

## Общие правила проекта (соблюдать во всех фичах)

- Структура модуля — как в `backend/app/orders/`: `models.py`, `schemas.py`, `repository.py`, `service.py`, `routes.py`, `__init__.py` с экспортом роутера.
- Слои: роутер не ходит в БД, сервис не знает про `Request`/`HTTPException`-детали HTTP больше необходимого, репозиторий не бросает `HTTPException` — возвращает `None`/список.
- Все ошибки — `HTTPException` из сервиса, `detail` на русском (как в `orders/service.py`).
- Pydantic v2: `class Config: from_attributes = True` в response-схемах.
- Роутер регистрируется в `backend/app/main.py` через `app.include_router(...)`.
- Авторизация — зависимости из `app.auth`: `get_current_user`, `require_seller`, `require_admin`.
- Префикс путей `/api/<ресурс>`, `tags=["<ресурс>"]`.
- Статусы — строковые константы в `models.py` рядом с моделью. Не Enum в БД (SQLite), но набор допустимых значений в коде должен быть явным (например `REVIEW_STATUSES = {...}` или `class ReviewStatus(str, Enum)` и хранение `.value`).
- Каждая новая таблица — миграция Alembic (`alembic revision --autogenerate -m "..."` в `backend/`), не полагаться на `init_db()`.
- Время — `datetime.utcnow` (как в остальных моделях), поле `created_at`.
- Деньги — `round(x, 2)` перед сохранением.

Порядок работы по каждой фиче: модель → миграция → схемы → репозиторий → сервис → роутер → регистрация в `main.py` → проверка через `/api/docs`.

---

## 1. Избранное (wishlist)

Самая простая, делай первой — разомнёшься на связке «модель + роутер + миграция» без статусной логики.

### Модель `Favorite` (`app/favorites/models.py`)

| поле | тип | ограничения |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK `users.id`, not null, index |
| `product_id` | Integer | FK `products.id`, not null, index |
| `created_at` | DateTime | default `datetime.utcnow` |

Обязательно: `UniqueConstraint("user_id", "product_id")` — один товар нельзя добавить в избранное дважды. Это проверка на уровне БД, а не только в сервисе.

Статусов нет.

### Схемы

- `FavoriteCreate`: `product_id: int`
- `FavoriteResponse`: `id`, `product_id`, `created_at`
- `FavoriteProductResponse`: `id`, `product_id`, `created_at`, `product: ProductResponse` (для списка — фронту нужны имя/цена/картинка, иначе он сделает N запросов)

### Ручки

| метод | путь | доступ | поведение |
|---|---|---|---|
| `GET` | `/api/favorites` | авторизован | список избранного текущего юзера, новые сверху, с вложенным товаром |
| `POST` | `/api/favorites` | авторизован | добавить; товара нет → 404; уже в избранном → 200/204 идемпотентно (не 500 от constraint) |
| `DELETE` | `/api/favorites/{product_id}` | авторизован | удалить; нет записи → 404; статус ответа 204 |

### Правила

- Пользователь видит и меняет **только своё** избранное. Никаких `user_id` в теле запроса — берётся из токена.
- Удаление товара продавцом не должно ронять выдачу избранного (или каскад в FK, или фильтрация «мертвых» записей — реши сам и оставь комментарий почему).

### Готово, когда

Добавил товар → он в `GET /api/favorites` с ценой и названием → повторный `POST` не ломается → `DELETE` убирает.

---

## 2. Отзывы на товар

### Модель `Review` (`app/reviews/models.py`)

| поле | тип | ограничения |
|---|---|---|
| `id` | Integer | PK |
| `user_id` | Integer | FK `users.id`, not null, index |
| `product_id` | Integer | FK `products.id`, not null, index |
| `rating` | Integer | not null, 1..5 |
| `text` | Text | nullable (оценка без текста — норм) |
| `status` | String | not null, default `pending` |
| `created_at` | DateTime | default `datetime.utcnow` |

`UniqueConstraint("user_id", "product_id")` — один отзыв на товар от пользователя.

### Статусы

```
pending   → approved   (админ одобрил, отзыв виден всем)
pending   → rejected   (админ отклонил, виден только автору)
approved  → rejected   (админ передумал / жалоба)
rejected  → approved   (админ передумал обратно)
```

Из `approved`/`rejected` в `pending` — нельзя. Переход в тот же статус — 400 или no-op, выбери одно и придерживайся.

Валидация перехода — отдельная функция/словарь в сервисе (`_ALLOWED = {"pending": {"approved", "rejected"}, ...}`), а не цепочка `if` в роутере. Эта же схема пригодится в фиче 4.

### Схемы

- `ReviewCreate`: `product_id: int`, `rating: int` (`Field(ge=1, le=5)`), `text: str | None` (`max_length=2000`)
- `ReviewUpdate`: `rating`, `text` — оба опциональны
- `ReviewResponse`: `id`, `product_id`, `user_id`, `rating`, `text`, `status`, `created_at`
- `ReviewModerate`: `status: str`
- `ProductRatingResponse`: `product_id`, `average: float | None`, `count: int`

Валидацию диапазона рейтинга делает Pydantic — не дублируй её в сервисе.

### Ручки

| метод | путь | доступ | поведение |
|---|---|---|---|
| `GET` | `/api/products/{product_id}/reviews` | публично | только `approved`; своё `pending`/`rejected` автор видит, если авторизован |
| `GET` | `/api/products/{product_id}/rating` | публично | средний рейтинг и количество, **только по `approved`** |
| `POST` | `/api/reviews` | авторизован | создать в статусе `pending` |
| `PATCH` | `/api/reviews/{id}` | автор | правка своего; после правки статус сбрасывается в `pending` |
| `DELETE` | `/api/reviews/{id}` | автор или админ | 204 |
| `GET` | `/api/reviews/moderation` | `require_admin` | все `pending`, старые сверху |
| `PATCH` | `/api/reviews/{id}/status` | `require_admin` | смена статуса по правилам выше |

### Правила

- Отзыв можно оставить **только на купленный товар**: должен существовать `Order` этого юзера, содержащий `OrderItem` с этим `product_id`. Не купил → 403 с внятным `detail`. Это ключевое требование фичи, не пропускай.
- Средний рейтинг считать агрегатом в SQL (`func.avg`, `func.count`), не тянуть все отзывы в Python.
- Продавец **не** модерирует отзывы на свои товары — только админ. Иначе смысл модерации теряется.
- Товар без одобренных отзывов: `average = null`, `count = 0`, не 404 и не 0.0.

### Готово, когда

Купил товар → оставил отзыв → в публичном списке его нет → админ одобрил → появился, рейтинг товара пересчитался. Отзыв на некупленный товар → 403.

---

## 3. Промокоды

### Модель `Promo` (`app/promo/models.py`)

| поле | тип | ограничения |
|---|---|---|
| `id` | Integer | PK |
| `code` | String | unique, index, not null, хранить в **верхнем регистре** |
| `discount_percent` | Integer | not null, 1..100 |
| `expires_at` | DateTime | nullable (null = бессрочный) |
| `max_uses` | Integer | nullable (null = безлимит) |
| `used_count` | Integer | not null, default 0 |
| `is_active` | Boolean | not null, default `True` — ручное отключение админом |
| `created_at` | DateTime | default `datetime.utcnow` |

### Статусы

Статус **не хранится в БД** — он вычисляется. Хранимый статус здесь рассинхронизируется с `used_count` и временем, поэтому: свойство `status` на модели или функция в сервисе.

```
disabled   — is_active == False           (приоритет выше остальных)
expired    — expires_at и он в прошлом
exhausted  — max_uses и used_count >= max_uses
active     — всё остальное
```

Порядок проверок именно такой: отключённый просроченный промокод показывается как `disabled`.

### Связь с заказом

В `Order` добавить (миграция на существующую таблицу, поля nullable — старые заказы без промокода):
- `promo_id` — FK `promos.id`, nullable
- `discount` — Float, default 0

`total` в заказе хранится **уже со скидкой**. Плюс сохраняй сумму скидки в `discount`, чтобы можно было показать «вы сэкономили N» и не пересчитывать задним числом при изменении промокода.

### Схемы

- `PromoCreate`: `code`, `discount_percent` (`ge=1, le=100`), `expires_at?`, `max_uses?`
- `PromoResponse`: все поля + вычисленный `status`
- `PromoCheckRequest`: `code: str`, `cart: Dict[int, int]`
- `PromoCheckResponse`: `code`, `discount_percent`, `subtotal`, `discount`, `total`
- `OrderCreate` расширить: `promo_code: str | None`

### Ручки

| метод | путь | доступ | поведение |
|---|---|---|---|
| `POST` | `/api/promo/check` | авторизован | проверка + расчёт скидки, **без** списания использования |
| `GET` | `/api/promo` | `require_admin` | список всех |
| `POST` | `/api/promo` | `require_admin` | создать; дубль кода → 409 |
| `PATCH` | `/api/promo/{id}` | `require_admin` | менять `is_active`, `expires_at`, `max_uses`. `code` и `discount_percent` менять нельзя — уже применены к заказам |
| `DELETE` | `/api/promo/{id}` | `require_admin` | 409, если `used_count > 0` — вместо удаления пусть выключает `is_active` |

### Правила

- Код нечувствителен к регистру: нормализуй в `.upper().strip()` и на входе, и при сохранении.
- `used_count` увеличивается **только** при успешном создании заказа, в той же транзакции, что и заказ. Не при `/check`.
- Неактивный промокод при оформлении → 400, заказ не создаётся (не «молча без скидки»).
- Скидка считается от суммы корзины: `discount = round(subtotal * percent / 100, 2)`, `total = subtotal - discount`. `total` не может стать отрицательным.
- `/check` и оформление заказа должны считать скидку **одной и той же функцией**. Разъедутся — пользователь увидит на кнопке одну цену, в заказе другую.

### Готово, когда

Создал промокод на 10% с `max_uses=1` → `/check` показывает скидку → заказ создался с уменьшенным `total` и `discount` → второй `/check` отдаёт `exhausted` → второй заказ с этим кодом → 400.

---

## 4. Возвраты

Самая сложная: настоящая стейт-машина поверх готовых заказов. Делай последней.

### Модель `Return` (`app/returns/models.py`)

| поле | тип | ограничения |
|---|---|---|
| `id` | Integer | PK |
| `order_id` | Integer | FK `orders.id`, not null, index |
| `user_id` | Integer | FK `users.id`, not null, index (денормализация ради простых запросов — ок) |
| `reason` | Text | not null |
| `status` | String | not null, default `requested` |
| `comment` | Text | nullable — комментарий админа при отклонении |
| `amount` | Float | nullable — сумма к возврату, проставляется при `approved` |
| `created_at` | DateTime | default `datetime.utcnow` |
| `updated_at` | DateTime | default `utcnow`, обновляется при каждой смене статуса |

Один активный возврат на заказ. Уникальный индекс тут не поможет (после `rejected` заявку можно подать снова), поэтому проверка в сервисе: нельзя создать возврат, если по заказу уже есть возврат в статусе из `{requested, approved, shipped_back}`.

### Статусы

```
requested ──► approved ──► shipped_back ──► refunded  (терминальный)
    │            │
    └──► rejected ◄┘                       (терминальный)
```

| статус | смысл | кто переводит дальше |
|---|---|---|
| `requested` | заявка подана | админ → `approved` / `rejected` |
| `approved` | одобрено, ждём товар назад | покупатель → `shipped_back` |
| `shipped_back` | покупатель отправил товар | админ → `refunded` / `rejected` |
| `refunded` | деньги вернули | — терминальный |
| `rejected` | отказ | — терминальный |

Из терминальных статусов переходов нет вообще. Отдельно: покупатель может отменить свою заявку в статусе `requested` (`DELETE`), дальше — нет.

Переходы описать словарём `_TRANSITIONS: dict[str, set[str]]` + отдельно «кто имеет право» на каждый переход. Не размазывай по роутеру.

### Схемы

- `ReturnCreate`: `order_id: int`, `reason: str` (`min_length=10`)
- `ReturnResponse`: все поля + `order: OrderResponse` (опционально, для админского списка)
- `ReturnStatusUpdate`: `status: str`, `comment: str | None`

### Ручки

| метод | путь | доступ | поведение |
|---|---|---|---|
| `POST` | `/api/returns` | авторизован | создать заявку по своему заказу |
| `GET` | `/api/returns` | авторизован | свои заявки, новые сверху |
| `GET` | `/api/returns/{id}` | автор или админ | одна заявка |
| `DELETE` | `/api/returns/{id}` | автор | отменить, только из `requested`, иначе 409 |
| `GET` | `/api/returns/admin` | `require_admin` | все, фильтр `?status=` |
| `PATCH` | `/api/returns/{id}/status` | `require_admin` | переходы админа |
| `PATCH` | `/api/returns/{id}/shipped` | автор | `approved → shipped_back` |

### Правила

- Возврат можно оформить **только на свой** заказ (`Order.user_id == user.id`), иначе 404 (не 403 — не подтверждай существование чужого заказа).
- Заказ должен быть в подходящем статусе. Сейчас у заказов только `new` по умолчанию — заведи явный набор статусов заказа (`new / paid / shipped / delivered / cancelled`) и разреши возврат из `delivered` (или из `paid`/`shipped` — реши и запиши в комментарии). Это доработка фичи заказов, она входит в объём.
- Возврат недоступен, если с момента `created_at` заказа прошло больше 14 дней — константа в модуле, не магическое число в коде.
- `amount` при `approved` = `order.total`. Частичный возврат — вне объёма, но поле оставь nullable, чтобы потом не мигрировать.
- Смена статуса всегда пишет `updated_at`. При `rejected` `comment` обязателен — 400 без него.
- Неразрешённый переход → 409 с `detail`, где видно текущий и запрошенный статус.

### Готово, когда

Заказ `delivered` → заявка `requested` → админ `approved` → покупатель `shipped_back` → админ `refunded`. Попытка `requested → refunded` напрямую → 409. Заявка на чужой заказ → 404. Вторая заявка по тому же заказу при активной первой → 409.

---

## Проверка (одна на все фичи)

`backend/tests/` или `test_*.py` рядом с модулем — на выбор. Минимум, что должно быть покрыто:

1. Валидатор переходов отзыва: разрешённый переход проходит, `approved → pending` падает.
2. Расчёт скидки: 10% от 100.0 → `discount=10.0`, `total=90.0`; скидка не делает `total` отрицательным.
3. Валидатор переходов возврата: полный happy path проходит, прыжок через статус падает.

Без фикстур и моков БД — это чистые функции, если ты правильно вынес логику из сервиса. Если протестировать не получается без поднятия базы — логика сидит не там, где надо.

## Порядок сдачи

1 (избранное) → 3 (промокоды) → 2 (отзывы) → 4 (возвраты). Каждая фича — отдельный коммит, работающий сам по себе.
