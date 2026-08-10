# Что делать дальше

Авторизация написана и работает: регистрация, вход, `/me`, `/refresh`. Но она пока ни к чему не подключена — все ручки каталога и корзины анонимны, `get_current_user` никто не вызывает.

Ниже пять этапов по убыванию пользы. Порядок не случайный: каждый следующий опирается на предыдущий, и после каждого проект остаётся в рабочем состоянии.

| этап | зачем | сколько это |
|---|---|---|
| 1. Заказы | авторизация начинает работать по-настоящему | вечер |
| 2. Alembic | перестать удалять `shop.db` при каждой правке модели | час |
| 3. Логин на фронте | всё это можно потрогать мышкой | вечер |
| 4. Тесты | правки перестают ломать старое молча | час |
| 5. Дыры в авторизации | logout, брутфорс, коды ошибок | по вкусу |

---

## Этап 1. Заказы — и авторизация оживает

### Почему именно заказы, а не «докрутить авторизацию»

Сейчас `get_current_user` — красивая функция, которая никому не нужна. Каталог и так открыт всем, корзина лежит в браузере.

Заказ — первая вещь в проекте, которая **принадлежит человеку**. «Покажи мои заказы» невозможно выполнить, не зная, кто спрашивает. Вот тут авторизация из абстракции становится работающей деталью.

И, что важнее, только на живой задаче видно, чего в авторизации не хватает. Гадать заранее — пустая трата вечера.

### 1.1. Структура

Складываем так же, как `auth` — своей папкой:

```
backend/app/orders/
  __init__.py     # наружу: orders_router
  models.py       # Order, OrderItem
  schemas.py      # OrderCreate, OrderResponse, OrderItemResponse
  repository.py
  service.py
  routes.py
```

### 1.2. Модели

```python
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, default="new", nullable=False)
    total = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship("OrderItem", back_populates="order")
    user = relationship("User")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)   # цена НА МОМЕНТ ЗАКАЗА
```

**Главная мысль всего этапа — вот это поле `price` в `OrderItem`.**

Соблазн: цена же есть в `Product`, зачем дублировать? Затем, что завтра ты поднимешь цену товара — и все прошлые заказы задним числом «подорожают». Клиент платил 500, в истории теперь 700. Бухгалтерия сойдёт с ума.

Правило: **заказ — это снимок момента, а не ссылка на текущее состояние.** Что купили, по какой цене, тогда. То же самое касается названия товара, если товары могут переименовываться.

> `ForeignKey("users.id")` — вот ради чего мы переименовали таблицу в `users`. Если бы осталось `user`, тут был бы уже знакомый `NoReferencedTableError`.

### 1.3. Ручки

| метод | путь | кто может | что делает |
|---|---|---|---|
| POST | `/api/orders` | залогиненный | создать заказ из корзины |
| GET | `/api/orders` | залогиненный | список **своих** заказов |
| GET | `/api/orders/{id}` | залогиненный | один **свой** заказ |

```python
router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(data: OrderCreate,
                 user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    return OrderService(db).create(user.id, data.cart)


@router.get("", response_model=list[OrderResponse])
def my_orders(user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).list_for_user(user.id)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int,
              user: User = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return OrderService(db).get_for_user(order_id, user.id)
```

Обрати внимание: `user` приходит сам, ручка ничего не знает про JWT.

### 1.4. Самое опасное место — чужие заказы

Вот так писать **нельзя**:

```python
def get_for_user(self, order_id: int, user_id: int):
    return self.repo.get_by_id(order_id)      # ← дыра
```

Здесь любой залогиненный подставит `/api/orders/777` и прочитает чужой заказ. Токен-то у него настоящий, проверка прошла.

Правильно — фильтровать по владельцу **в самом запросе**:

```python
def get_for_user(self, order_id: int, user_id: int) -> OrderResponse:
    order = self.repo.get_owned(order_id, user_id)   # WHERE id = ? AND user_id = ?
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return OrderResponse.model_validate(order)
```

И **404, а не 403**. «Доступ запрещён» подтверждает, что заказ существует — по такому ответу перебором составляют картину чужих покупок. Пусть для чужака его просто нет.

Это разница между **аутентификацией** («кто ты» — её делает authx) и **авторизацией** («что тебе можно» — её делаешь ты, вот этими `WHERE user_id = ?`). Библиотека вторую половину за тебя не сделает никогда.

### 1.5. Создание заказа

Корзина у нас в браузере, поэтому клиент присылает её вместе с запросом — как в существующем `/api/cart`:

```python
class OrderCreate(BaseModel):
    cart: Dict[int, int]      # {product_id: quantity}
```

Сервис:

1. Корзина пустая → 400.
2. По каждому `product_id` найти товар. Нет товара → 404 с указанием, какого именно.
3. Сложить `OrderItem` с **текущей ценой из базы**, а не из того, что прислал клиент.
4. Посчитать `total` на сервере.
5. Сохранить, вернуть заказ.

**Никогда не бери цену из запроса.** Клиент — это чужой компьютер, любые числа оттуда можно подменить. Из тела запроса берём только «что» и «сколько», всё остальное считаем сами. Это тот же принцип, по которому у тебя сейчас `/api/cart` считает сумму на сервере.

### 1.6. Проверить

```bash
TOKEN=$(curl -s -X POST localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"a@b.com","password":"qwerty123"}' | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# создать
curl -X POST localhost:8000/api/orders -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' -d '{"cart":{"1":2}}'

# свои заказы
curl localhost:8000/api/orders -H "Authorization: Bearer $TOKEN"

# без токена — 401
curl -i localhost:8000/api/orders
```

**Обязательно проверь главное:** заведи второго пользователя, залогинься под ним и попробуй открыть заказ первого. Должно быть 404. Если 200 — вернись к 1.4.

---

## Этап 2. Alembic — чтобы не удалять базу

### В чём проблема

`Base.metadata.create_all()` умеет ровно одно: создать таблицу, если её нет. **Менять существующую он не умеет.**

Добавишь завтра в `User` поле `phone` — в базе оно не появится, `create_all` промолчит, а приложение упадёт на первом же запросе. Единственный выход сейчас — удалить `shop.db` вместе со всеми данными. На учебном проекте терпимо, на реальном — конец.

Alembic ведёт **историю изменений схемы**: каждое изменение — отдельный файл-миграция, который умеет накатиться и откатиться. Это git, только для структуры базы.

### 2.1. Поставить и настроить

```bash
pip install alembic
cd backend
alembic init migrations
```

В `alembic.ini` строку `sqlalchemy.url` **оставь пустой** — URL подтянем из настроек, чтобы он не жил в двух местах.

В `migrations/env.py`:

```python
from app.config import settings
from app.database import Base
import app.models          # каталог
import app.auth            # пользователи
import app.orders          # заказы

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

**Импорты — ключевая строчка.** Alembic сравнивает то, что знает `Base.metadata`, с тем, что лежит в базе. Модель, которую никто не импортировал, в метаданных отсутствует — и alembic решит, что таблицу надо **удалить**. Те же грабли, что были с `create_all`, только с более неприятными последствиями.

### 2.2. Первая миграция

```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

**`--autogenerate` — это черновик, а не результат.** Всегда открывай получившийся файл в `migrations/versions/` и читай глазами. Alembic плохо распознаёт переименования: он видит «поля `crawled_at` больше нет, зато появилось `created_at`» и пишет `drop_column` + `add_column` — то есть молча выкидывает данные. Такое исправляют руками на `alter_column`.

Дальше цикл на каждое изменение модели:

```bash
alembic revision --autogenerate -m "add phone to user"
alembic upgrade head       # накатить
alembic downgrade -1       # откатить, если что-то не так
```

### 2.3. Убрать create_all

В `main.py` `init_db()` из старта убрать — теперь схемой управляет alembic. Иначе два механизма будут спорить за одну базу.

> Отдельно про SQLite: он **не умеет** менять и удалять колонки. Alembic обходит это через `batch_alter_table` (пересоздать таблицу и перелить данные), но включать это надо руками. Ещё один довод переехать на Postgres, когда надоест.

---

## Этап 3. Логин на фронте

Сейчас `frontend/src/api.js` шлёт запросы без токена, а формы входа нет вовсе.

### 3.1. Хранилище сессии

`frontend/src/auth.js` — по образцу `cart.js`:

```javascript
const state = reactive({
  token: localStorage.getItem('token') || '',
  user: null,
})

export function useAuth() {
  return {
    isAuthenticated: computed(() => Boolean(state.token)),
    user: computed(() => state.user),

    async login(email, password) {
      const data = await api.login(email, password)
      state.token = data.access_token
      localStorage.setItem('token', state.token)
      state.user = await api.me()
    },

    logout() {
      state.token = ''
      state.user = null
      localStorage.removeItem('token')
    },
  }
}
```

### 3.2. Токен во все запросы

В `api.js`, в функцию `request`:

```javascript
const token = localStorage.getItem('token')
const headers = { ...options?.headers }
if (token) headers.Authorization = `Bearer ${token}`
```

Плюс общая реакция на 401 — токен протух, чистим и отправляем на вход:

```javascript
if (res.status === 401) {
  localStorage.removeItem('token')
  router.push('/login')
}
```

Это должно жить **в одном месте**, в `request`. Если раскидать проверку 401 по компонентам — забудешь в половине и получишь страницы, которые молча показывают пустоту.

### 3.3. Что добавить в интерфейс

- `views/LoginView.vue` и `views/RegisterView.vue` — две формы.
- `views/OrdersView.vue` — «Мои заказы».
- В `AppHeader.vue` — «Войти» либо email пользователя и «Выйти».
- В `CartView.vue` кнопка «Оформить заказ» перестаёт быть `disabled`: гостя ведём на `/login`, залогиненного — `POST /api/orders`, после успеха чистим корзину и уходим на `/orders`.
- В `router.js` — защита приватных маршрутов:

```javascript
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
```

**Важно понимать, чем это является и чем не является.** Это удобство, а не безопасность. Пользователь может отредактировать `localStorage` в devtools и попасть на страницу «Мои заказы» — но данных он не получит, потому что настоящая проверка стоит на сервере. Фронт лишь избавляет от бессмысленного мигания пустой страницей. Никогда не переноси на фронт проверки, от которых зависит доступ к данным.

---

## Этап 4. Тесты

Сейчас всё проверялось руками. Значит, при следующей правке никто ничего не проверит.

### 4.1. Поставить

```bash
pip install pytest httpx2
```

`httpx2` — именно так, с двойкой: `TestClient` из starlette 1.6 требует его и сам об этом пишет в ошибке.

### 4.2. Отдельная база для тестов

`backend/tests/conftest.py`:

```python
@pytest.fixture
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    app.dependency_overrides[get_db] = lambda: TestingSession()
    yield TestClient(app)
    app.dependency_overrides.clear()
```

`dependency_overrides` — штука, ради которой стоило городить `Depends(get_db)`. Одна строка подменяет базу на временную, и **тесты не трогают твой `shop.db`**. Тест, который портит рабочие данные, перестают запускать через неделю.

### 4.3. С чего начать

Не гонись за покрытием. Достаточно того, что больно ломается:

```python
def test_register_then_login(client):
    r = client.post("/api/auth/register", json={"email": "a@b.com", "password": "qwerty123"})
    assert r.status_code == 201
    assert "hashed_password" not in r.json()      # пароль не утёк наружу

    r = client.post("/api/auth/login", json={"email": "a@b.com", "password": "qwerty123"})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_cannot_read_foreign_order(client):
    # user1 создаёт заказ, user2 пытается его открыть → 404
    ...
```

Последний — самый ценный в проекте. Он сторожит ровно ту дыру из пункта 1.4, которую легко открыть случайной правкой полгода спустя.

---

## Этап 5. Дыры в авторизации

Это то, что можно откладывать, пока проект учебный. Порядок — по соотношению «польза к возне».

### 5.1. Правильные коды ошибок (10 минут)

Битый токен сейчас отдаёт **422**, а фронт ждёт 401. Чинится обработчиком:

```python
@app.exception_handler(JWTDecodeError)
def jwt_error_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": "Недействительный токен"})
```

Пока этого нет, логика «поймал 401 → отправь на логин» из этапа 3.2 будет работать через раз.

### 5.2. Защита от перебора паролей (полчаса)

`/api/auth/login` можно дёргать бесконечно. Пароль из восьми цифр подбирается за вечер.

В authx есть `security.rate_limited(...)`. Ограничение вида «5 попыток в минуту с одного IP» закрывает вопрос для учебного проекта. Считать попытки в памяти процесса — нормально, пока процесс один; при нескольких воркерах понадобится Redis.

### 5.3. Настоящий logout (день + Redis)

Сейчас «выход» — это забыть токен в браузере. Сам токен остаётся действительным до истечения: если он утёк, кнопка «Выйти» вора не остановит.

Настоящий logout — блоклист (`security.set_token_blocklist`): при выходе `jti` токена кладётся в Redis до момента его истечения, и на каждом запросе проверяется.

Обрати внимание на цену: **каждый запрос теперь идёт в Redis.** Именно от этого JWT и уходил — от похода в хранилище на каждой проверке. Поэтому logout и не делают, пока он реально не нужен.

### 5.4. Ротация refresh-токенов (день)

Сейчас один refresh живёт 20 дней. Утёк — вор ходит 20 дней, и ты об этом не узнаешь.

Ротация: на каждый `/refresh` выдаётся **новый** refresh, старый гасится. Если старый предъявили повторно — значит, кто-то использует украденную копию, и правильная реакция — обнулить всю сессию. Требует того же блоклиста, что и 5.3.

### 5.5. Всё остальное

Смена пароля, восстановление через почту, подтверждение email, роли и права, вход через Google. Каждый пункт тянет за собой либо почтовый сервис, либо OAuth-регистрацию приложения, либо и то и другое.

Ничего из этого не нужно, пока некому пожаловаться, что оно не работает.

---

## Короткий вывод

Ближайшая цель — **этап 1**. Он превращает авторизацию из написанного кода в работающую часть системы и попутно показывает, чего в ней не хватает на самом деле.

Этап 2 сделай сразу после — чем позже поставишь alembic, тем больше данных потеряешь по дороге.

Этапы 3–5 дальше по вкусу, они друг от друга не зависят.
