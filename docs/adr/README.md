# Architecture Decision Records

Журнал архітектурних рішень за шаблоном Michael Nygard (Title, Status, Context, Alternatives, Decision, Consequences).

| ID | Рішення | Статус | Дата |
| --- | --- | --- | --- |
| [ADR-001](0001-choice-of-technology.md) | Механізм запобігання подвійному бронюванню: PostgreSQL `EXCLUDE USING gist` + Redis hold | Approved | 11.11.2026 |
| [ADR-002](0002-bonus-wallet-model.md) | Модель бонусного рахунку: баланс з `CHECK` + журнал транзакцій з `UNIQUE` | Approved | 11.11.2026 |
| ADR-003 | Модульний моноліт + окремий Scheduler Worker | Planned | — |
| ADR-004 | Стратегія idempotency (`Idempotency-Key` у Redis, TTL 24 год) | Planned | — |
