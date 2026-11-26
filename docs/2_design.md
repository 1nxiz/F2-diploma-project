# РОЗДІЛ 2. ПРОЄКТУВАННЯ АРХІТЕКТУРИ СИСТЕМИ

Архітектуру спроєктовано за методологією C4 Model (Simon Brown) на основі контракту вимог [SRS](srs.md) за принципом Diagrams-as-Code: діаграми описано мовою Mermaid.js і рендеряться безпосередньо інтерфейсом GitHub. Ключові компроміси зафіксовано в [ADR](adr/README.md).

## 2.1 Контекстне та контейнерне моделювання системи (C4 Model)

<a id="diagram-level1"></a>
### 2.1.1 Рівень 1. System Context Diagram

```mermaid
C4Context
  title Рівень 1. System Context — CoWork Booking System

  Person(resident, "Резидент", "Шукає та бронює робочі місця, накопичує й використовує бонусні бали")
  Person(admin, "Адміністратор коворкінгу", "Керує каталогом зон і місць та бронюваннями")
  System(cws, "CoWork Booking System", "Бронювання робочих місць без перетину інтервалів, денний ліміт 5 год, бонусна програма лояльності")
  System_Ext(smtp, "Email Service", "Зовнішній SMTP-relay для доставки листів")

  Rel(resident, cws, "Бронює місця, переглядає бонусний рахунок", "HTTPS / REST JSON")
  Rel(admin, cws, "Керує каталогом і бронюваннями", "HTTPS / REST JSON")
  Rel(cws, smtp, "Передає листи-сповіщення", "SMTP + STARTTLS :587")
  Rel(smtp, resident, "Доставляє лист про 100 балів", "Email")

  UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="1")
```

**Опис вузлів і зв'язків (Рівень 1):**

| Елемент | Тип | Опис | Вимоги |
| --- | --- | --- | --- |
| Резидент | Person | Користувач з роллю `user`: пошук, бронювання, бонусний рахунок | [SRS-FUN-09](srs.md#srs-fun-09)–[SRS-FUN-22](srs.md#srs-fun-22) |
| Адміністратор коворкінгу | Person | Користувач з роллю `admin`: каталог і всі бронювання | [SRS-FUN-06](srs.md#srs-fun-06)–[SRS-FUN-08](srs.md#srs-fun-08), [SRS-FUN-16](srs.md#srs-fun-16) |
| CoWork Booking System | System | Система, що розробляється | [SRS](srs.md) |
| Email Service | System_Ext | Зовнішній SMTP-relay; система не зберігає пошту | [SRS-FUN-24](srs.md#srs-fun-24) |

| Зв'язок | Протокол | Обґрунтування |
| --- | --- | --- |
| Резидент / Адміністратор → System | HTTPS (TLS 1.2+) / REST JSON | [SRS-NFR-SEC-03](srs.md#srs-nfr-sec-03) |
| System → Email Service | SMTP + STARTTLS, порт 587 | Шифрування каналу передачі листів |
| Email Service → Резидент | Email (доставка поштовою інфраструктурою) | Поза межами системи |

<a id="diagram-level2"></a>
### 2.1.2 Рівень 2. Container Diagram

```mermaid
C4Container
  title Рівень 2. Container — CoWork Booking System

  Person(resident, "Резидент", "Браузер")
  Person(admin, "Адміністратор", "Браузер")
  System_Ext(smtp, "Email Service", "SMTP relay")

  System_Boundary(sys, "CoWork Booking System") {
    Container(spa, "Web SPA", "React, TypeScript", "UI бронювання і бонусна шкала")
    Container(proxy, "Reverse Proxy", "Nginx 1.27", "TLS, статика, /api/v1")
    Container(api, "API Application", "FastAPI, Uvicorn", "REST API, stateless, 2+ репліки")
    Container(worker, "Scheduler Worker", "Python, APScheduler", "Завершення, бали, email")
    ContainerDb(db, "PostgreSQL", "PostgreSQL 17", "Бронювання, бонусні рахунки")
    ContainerDb(redis, "Redis", "Redis 7", "Hold, rate limit, idempotency")
    Container(prom, "Prometheus", "Prometheus 3", "Збір метрик")
    Container(grafana, "Grafana", "Grafana 11", "Дашборди")
  }

  Rel(resident, proxy, "Завантажує SPA", "HTTPS :443")
  Rel(admin, proxy, "Завантажує SPA", "HTTPS :443")
  Rel(spa, proxy, "Викликає /api/v1", "REST JSON / HTTPS")
  Rel(proxy, api, "Проксіює /api/v1", "HTTP/1.1 :8000, Docker network")
  Rel(api, db, "Транзакції бронювань і рахунків", "SQL / TCP :5432, asyncpg")
  Rel(api, redis, "Hold, rate limit, idempotency", "RESP / TCP :6379")
  Rel(worker, db, "Завершення, нарахування балів", "SQL / TCP :5432")
  Rel(worker, smtp, "Листи-сповіщення", "SMTP + STARTTLS :587")
  Rel(prom, api, "Scrape", "HTTP GET /metrics")
  Rel(prom, worker, "Scrape", "HTTP GET /metrics :9100")
  Rel(grafana, prom, "PromQL", "HTTP :9090")

  UpdateRelStyle(spa, proxy, $offsetX="-40", $offsetY="-30")
  UpdateRelStyle(api, db, $offsetX="-150", $offsetY="10")
  UpdateRelStyle(api, redis, $offsetX="20", $offsetY="-40")
  UpdateRelStyle(worker, db, $offsetX="0", $offsetY="25")
  UpdateRelStyle(worker, smtp, $offsetX="-70", $offsetY="-60")
  UpdateRelStyle(prom, api, $offsetX="-90", $offsetY="40")
  UpdateRelStyle(prom, worker, $offsetX="10", $offsetY="60")
  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

**Опис контейнерів (Рівень 2).** Кожен контейнер — окремий сервіс Docker Compose.

| Контейнер | Технологія | Відповідальність | Вимоги |
| --- | --- | --- | --- |
| Web SPA | React, TypeScript, Vite (статичний бандл) | Пошук місць, hold, бронювання, бонусна шкала 0–100 %, діалог `BONUS_CAP_REACHED` з діями «Використати зараз» / «Залишити» | [SRS-FUN-19](srs.md#srs-fun-19), [SRS-FUN-20](srs.md#srs-fun-20) |
| Reverse Proxy | Nginx 1.27 | Термінація TLS, HSTS, роздача статики SPA, проксіювання `/api/v1`, ліміт розміру тіла запиту | [SRS-NFR-SEC-03](srs.md#srs-nfr-sec-03) |
| API Application | Python 3.12, FastAPI, Uvicorn | REST API модулів Auth, Workspaces, Bookings, Bonus, Admin; stateless; 2+ репліки | [SRS-FUN-01](srs.md#srs-fun-01)–[SRS-FUN-16](srs.md#srs-fun-16), [SRS-FUN-19](srs.md#srs-fun-19)–[SRS-FUN-23](srs.md#srs-fun-23), [SRS-NFR-SCAL-01](srs.md#srs-nfr-scal-01) |
| Scheduler Worker | Python 3.12, APScheduler (та сама кодова база, інша точка входу) | Завершення бронювань, нарахування балів, email-сповіщення; запускається в одному екземплярі, захист від паралельних запусків — `FOR UPDATE SKIP LOCKED` | [SRS-FUN-17](srs.md#srs-fun-17), [SRS-FUN-18](srs.md#srs-fun-18), [SRS-FUN-24](srs.md#srs-fun-24), [SRS-NFR-REL-05](srs.md#srs-nfr-rel-05) |
| PostgreSQL | PostgreSQL 17 + `btree_gist` | Джерело істини: бронювання з `EXCLUDE USING gist`, бонусні рахунки з `CHECK`, журнал транзакцій з `UNIQUE` | [SRS-FUN-11](srs.md#srs-fun-11), [SRS-NFR-CONS-01](srs.md#srs-nfr-cons-01), [ADR-001](adr/0001-choice-of-technology.md), [ADR-002](adr/0002-bonus-wallet-model.md) |
| Redis | Redis 7 | Hold (`SET NX PX`), лічильники rate limit, ключі idempotency, кеш доступності; не є джерелом істини | [SRS-FUN-10](srs.md#srs-fun-10), [SRS-FUN-12](srs.md#srs-fun-12), [SRS-NFR-SCAL-02](srs.md#srs-nfr-scal-02), [ADR-001](adr/0001-choice-of-technology.md) |
| Prometheus | Prometheus 3 | Збір метрик з `/metrics` API і Worker | [SRS-NFR-OBS-02](srs.md#srs-nfr-obs-02) |
| Grafana | Grafana 11 | Дашборди RED і бізнес-метрик бонусної програми | [SRS-NFR-OBS-02](srs.md#srs-nfr-obs-02) |

**Специфікація зв'язків (Рівень 2):**

| Від → До | Протокол / порт | Призначення |
| --- | --- | --- |
| Резидент, Адміністратор → Reverse Proxy | HTTPS :443 | Завантаження SPA і виклики API |
| Web SPA → Reverse Proxy | REST JSON / HTTPS, `Authorization: Bearer <JWT>` | Виклики `/api/v1/*` |
| Reverse Proxy → API Application | HTTP/1.1 :8000 (внутрішня мережа Docker) | Проксіювання з заголовками `X-Request-ID`, `X-Forwarded-For` |
| API Application → PostgreSQL | SQL / TCP :5432 (asyncpg) | Транзакції бронювань і рахунків |
| API Application → Redis | RESP / TCP :6379 | Hold, rate limit, idempotency |
| Scheduler Worker → PostgreSQL | SQL / TCP :5432 | Завершення бронювань, нарахування балів |
| Scheduler Worker → Email Service | SMTP + STARTTLS :587 | Сповіщення про 100 балів |
| Prometheus → API Application, Scheduler Worker | HTTP GET `/metrics` (pull) | Збір метрик |
| Grafana → Prometheus | HTTP :9090, PromQL | Побудова дашбордів |

## 2.2 Компонентне моделювання критичного сервісу системи

<a id="diagram-level3"></a>
Для декомпозиції обрано контейнер **API Application**, оскільки він містить усю логіку конкурентного бронювання та бонусної програми. Внутрішня структура відповідає Clean Architecture: вхідний шар → прикладні сервіси → доменні політики, а інфраструктура підключається через порти (Dependency Inversion).

```mermaid
C4Component
  title Рівень 3. Component — API Application (FastAPI)

  Container(proxy, "Reverse Proxy", "Nginx 1.27")

  Container_Boundary(api, "API Application") {
    Component(mw, "Middleware Pipeline", "Starlette middleware", "RequestID, логи, метрики, rate limit")
    Component(ctrl, "Booking and Bonus Routers", "FastAPI APIRouter", "/holds, /bookings, /bonus")
    Component(dto, "DTO Schemas", "Pydantic v2", "Валідація вхідних даних")
    Component(guard, "Auth Guard", "FastAPI Depends, PyJWT", "JWT, RBAC, власник")
    Component(err, "Global Error Handler", "FastAPI exception handlers", "RFC 9457: 409, 422, 429")
    Component(bs, "BookingService", "Application service", "hold, create, cancel")
    Component(bonus, "BonusService", "Application service", "Рахунок, cap, безкоштовна година")
    Component(policy, "Domain Policies", "Pure Python", "Quota 5 год; 5 балів/год; cap 100")
    Component(ports, "Ports", "typing.Protocol", "Репозиторії, сховища, UnitOfWork")
    Component(root, "Composition Root", "dependencies.py", "Зв'язує порти з адаптерами")
    Component(sql, "SQLAlchemy Adapters", "SQLAlchemy 2.0 async", "Репозиторії, UoW, FOR UPDATE")
    Component(radapt, "Redis Adapters", "redis-py asyncio", "Hold, idempotency, rate limit")
  }

  Boundary(stores, "Сховища даних (зовнішні контейнери)") {
    ContainerDb(db, "PostgreSQL", "PostgreSQL 17")
    ContainerDb(redis, "Redis", "Redis 7")
  }

  Rel(proxy, mw, "HTTP-запит", "HTTP/1.1, ASGI")
  Rel(mw, ctrl, "Передає запит", "ASGI call chain")
  Rel(ctrl, dto, "Валідує тіло", "Pydantic model_validate")
  Rel(ctrl, guard, "Автентифікує", "Depends()")
  Rel(ctrl, bs, "Викликає use case", "Depends(), DI")
  Rel(ctrl, bonus, "Викликає use case", "Depends(), DI")
  Rel(ctrl, err, "Доменні винятки", "raise, exception_handler")
  Rel(bs, policy, "Перевіряє ліміт", "виклик функції")
  Rel(bonus, policy, "Рахує бали", "виклик функції")
  Rel(bs, ports, "Залежить від абстракцій", "DIP")
  Rel(bonus, ports, "Залежить від абстракцій", "DIP")
  Rel(root, sql, "Інстанціює", "factory")
  Rel(root, radapt, "Інстанціює", "factory")
  Rel(sql, ports, "Реалізує", "Protocol")
  Rel(radapt, ports, "Реалізує", "Protocol")
  Rel(sql, db, "SQL", "asyncpg / TCP :5432")
  Rel(radapt, redis, "Команди", "RESP / TCP :6379")
  Rel(mw, radapt, "INCR лічильника", "RateLimitStore")

  UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

**Опис компонентів (Рівень 3):**

| Шар | Компонент | Роль | Взаємодія | Вимоги |
| --- | --- | --- | --- | --- |
| Inbound | Middleware Pipeline | Генерація `request_id`, JSON-журналювання, метрики Prometheus, rate limit | Ланцюжок ASGI middleware; лічильник у Redis через `RateLimitStore` | [SRS-NFR-OBS-01](srs.md#srs-nfr-obs-01), [SRS-NFR-OBS-02](srs.md#srs-nfr-obs-02), [SRS-NFR-SCAL-02](srs.md#srs-nfr-scal-02) |
| Inbound | Booking and Bonus Routers | Ендпоїнти `POST /holds`, `POST /bookings`, `PATCH /bookings/{id}`, `GET /bonus/wallets/{coworking_id}`, `POST /bonus/redemptions` | Отримують сервіси та guard через `Depends()`; не мають доступу до БД | [SRS-FUN-10](srs.md#srs-fun-10)–[SRS-FUN-15](srs.md#srs-fun-15), [SRS-FUN-19](srs.md#srs-fun-19)–[SRS-FUN-22](srs.md#srs-fun-22) |
| Inbound | DTO Schemas | Валідація: тривалість 1–5 год, початок кратний 30 хв, ISO 8601; модель відповіді з полем `warnings` | `model_validate` до виклику сервісу; помилка → 422 | [SRS-FUN-13](srs.md#srs-fun-13), [SRS-FUN-20](srs.md#srs-fun-20), [SRS-FUN-21](srs.md#srs-fun-21) |
| Inbound | Auth Guard | Перевірка підпису та `exp` JWT, ролі (`user`/`admin`) і власника ресурсу | Залежність FastAPI `Depends(current_user)` | [SRS-FUN-04](srs.md#srs-fun-04), [SRS-NFR-SEC-01](srs.md#srs-nfr-sec-01), [SRS-NFR-SEC-04](srs.md#srs-nfr-sec-04) |
| Inbound | Global Error Handler | Мапінг доменних винятків у RFC 9457 Problem Details: `BookingConflict` → 409, `DailyLimitExceeded` → 422, `RateLimited` → 429 | `app.add_exception_handler`; приховує стек викликів | [SRS-FUN-11](srs.md#srs-fun-11), [SRS-FUN-14](srs.md#srs-fun-14) |
| Core | BookingService | Use cases hold / create / cancel; відкриває UnitOfWork, блокує рядок рахунку, перевіряє ліміт | Залежить лише від портів і політик | [SRS-FUN-10](srs.md#srs-fun-10)–[SRS-FUN-15](srs.md#srs-fun-15), [ADR-001](adr/0001-choice-of-technology.md) |
| Core | BonusService | Стан рахунку, попередження `BONUS_CAP_REACHED` / `BONUS_CAP_PARTIAL`, активація безкоштовної години, відновлення балансу | Залежить лише від портів і політик | [SRS-FUN-19](srs.md#srs-fun-19)–[SRS-FUN-23](srs.md#srs-fun-23), [ADR-002](adr/0002-bonus-wallet-model.md) |
| Core | Domain Policies | Чисті функції: `QuotaPolicy` (≤ 5 год/добу, [SRS-BR-02](srs.md#srs-br-02)), `BonusPolicy` (`min(5h, 100 − b)`, [SRS-BR-03](srs.md#srs-br-03), [SRS-BR-04](srs.md#srs-br-04)) | Виклик функції без I/O; покриття тестами ≥ 90 % | [SRS-NFR-MAINT-01](srs.md#srs-nfr-maint-01) |
| Core | Ports | Інтерфейси `BookingRepository`, `WalletRepository`, `HoldStore`, `IdempotencyStore`, `RateLimitStore`, `UnitOfWork` | `typing.Protocol`; реалізуються адаптерами | — |
| Wiring | Composition Root | Створення адаптерів і передача їх сервісам | Фабрики FastAPI-залежностей (`dependencies.py`) | — |
| Outbound | SQLAlchemy Adapters | Репозиторії, UnitOfWork (AsyncSession), `SELECT … FOR UPDATE`, мапінг SQLSTATE `23P01` → `BookingConflict` | SQL / asyncpg → PostgreSQL | [SRS-FUN-11](srs.md#srs-fun-11), [SRS-NFR-CONS-01](srs.md#srs-nfr-cons-01), [SRS-NFR-CONS-02](srs.md#srs-nfr-cons-02) |
| Outbound | Redis Adapters | `HoldStore` (`SET NX PX`, Lua-зняття з перевіркою токена), `IdempotencyStore` (TTL 24 год), `RateLimitStore` | RESP → Redis; за недоступності — `HoldUnavailable` → 503 | [SRS-FUN-10](srs.md#srs-fun-10), [SRS-FUN-12](srs.md#srs-fun-12), [SRS-NFR-REL-02](srs.md#srs-nfr-rel-02) |

**Потік `POST /api/v1/bookings`:** Middleware (request_id, rate limit) → Router → DTO-валідація → Auth Guard → `BookingService.create` → `IdempotencyStore.get` → UnitOfWork: блокування рядка `bonus_wallets` → `QuotaPolicy.check` → `BookingRepository.add` (обмеження `EXCLUDE`) → COMMIT → `HoldStore.release` → `BonusService.cap_warnings` → відповідь 201 з `warnings[]`.

## 2.3 Документування архітектурних рішень (Architecture Decision Records)

| ID | Рішення | Статус | Вимоги |
| --- | --- | --- | --- |
| [ADR-001](adr/0001-choice-of-technology.md) | Механізм запобігання подвійному бронюванню: PostgreSQL `EXCLUDE USING gist` + Redis hold | Approved | [SRS-FUN-10](srs.md#srs-fun-10), [SRS-FUN-11](srs.md#srs-fun-11), [SRS-NFR-CONS-01](srs.md#srs-nfr-cons-01), [SRS-NFR-PERF-02](srs.md#srs-nfr-perf-02), [SRS-NFR-REL-02](srs.md#srs-nfr-rel-02) |
| [ADR-002](adr/0002-bonus-wallet-model.md) | Модель бонусного рахунку: баланс з `CHECK` + журнал транзакцій з `UNIQUE` | Approved | [SRS-FUN-14](srs.md#srs-fun-14), [SRS-FUN-18](srs.md#srs-fun-18)–[SRS-FUN-23](srs.md#srs-fun-23), [SRS-NFR-CONS-02](srs.md#srs-nfr-cons-02)–[SRS-NFR-CONS-04](srs.md#srs-nfr-cons-04) |

## 2.4 Матриця трасування вимог в архітектуру

| Вимоги | Контейнер ([L2](#diagram-level2)) | Компоненти ([L3](#diagram-level3)) | Рішення | Верифікація |
| --- | --- | --- | --- | --- |
| [SRS-FUN-01](srs.md#srs-fun-01)–[SRS-FUN-05](srs.md#srs-fun-05) | API Application | Routers, Auth Guard, SQLAlchemy Adapters | — | Pytest + HTTPX |
| [SRS-FUN-06](srs.md#srs-fun-06)–[SRS-FUN-09](srs.md#srs-fun-09) | API Application, PostgreSQL | Routers, DTO Schemas, SQLAlchemy Adapters | — | Pytest + HTTPX |
| [SRS-FUN-10](srs.md#srs-fun-10), [SRS-FUN-12](srs.md#srs-fun-12) | API Application, Redis | BookingService, Redis Adapters | [ADR-001](adr/0001-choice-of-technology.md) | Pytest, fault injection |
| [SRS-FUN-11](srs.md#srs-fun-11) | API Application, PostgreSQL | BookingService, SQLAlchemy Adapters, Global Error Handler | [ADR-001](adr/0001-choice-of-technology.md) | k6 (100 VU) + SQL |
| [SRS-FUN-13](srs.md#srs-fun-13), [SRS-FUN-14](srs.md#srs-fun-14) | API Application, PostgreSQL | DTO Schemas, Domain Policies, BookingService | [ADR-002](adr/0002-bonus-wallet-model.md) | Pytest, Hypothesis |
| [SRS-FUN-15](srs.md#srs-fun-15), [SRS-FUN-16](srs.md#srs-fun-16) | API Application | Routers, Auth Guard, BookingService | — | Pytest + HTTPX |
| [SRS-FUN-17](srs.md#srs-fun-17), [SRS-FUN-18](srs.md#srs-fun-18), [SRS-FUN-24](srs.md#srs-fun-24) | Scheduler Worker, PostgreSQL, Email Service | Domain Policies (спільний модуль) | [ADR-002](adr/0002-bonus-wallet-model.md) | Pytest + freezegun, Mailpit |
| [SRS-FUN-19](srs.md#srs-fun-19)–[SRS-FUN-23](srs.md#srs-fun-23) | Web SPA, API Application, PostgreSQL | BonusService, Domain Policies, SQLAlchemy Adapters | [ADR-002](adr/0002-bonus-wallet-model.md) | Pytest, asyncio.gather |
| [SRS-NFR-PERF-01](srs.md#srs-nfr-perf-01)–[SRS-NFR-PERF-03](srs.md#srs-nfr-perf-03), [SRS-NFR-SCAL-01](srs.md#srs-nfr-scal-01) | Reverse Proxy, API Application | Middleware Pipeline | [ADR-001](adr/0001-choice-of-technology.md) | k6 |
| [SRS-NFR-SEC-01](srs.md#srs-nfr-sec-01)–[SRS-NFR-SEC-06](srs.md#srs-nfr-sec-06) | Reverse Proxy, API Application | Auth Guard, Middleware Pipeline | — | OWASP ZAP, Trivy, Bandit, gitleaks |
| [SRS-NFR-OBS-01](srs.md#srs-nfr-obs-01), [SRS-NFR-OBS-02](srs.md#srs-nfr-obs-02) | API Application, Scheduler Worker, Prometheus, Grafana | Middleware Pipeline | — | Pytest, `/metrics` |
