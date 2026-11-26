# Документація кваліфікаційного проєкту

**Тема:** Проєктування та розробка вебсистеми бронювання робочих місць у коворкінгу

**Topic:** Design and Development of a Web-Based Coworking Workspace Reservation System

| Параметр | Значення |
| --- | --- |
| Студент | Клевач Василь Романович |
| Науковий керівник | Когут Олег Васильович |
| Спеціальність | F2 (121) «Інженерія програмного забезпечення» |
| Архітектурний напрям | Розподілені системи та Cloud-Native архітектури |
| Стек | FastAPI, PostgreSQL, Redis, React, Docker, GitHub Actions |
| Ключова функція | Конкурентне бронювання без перетинів + бонусна програма лояльності (5 балів/год, 100 балів → безкоштовна година) |

## Структура пояснювальної записки

| Файл | Розділ | Зміст | Статус |
| --- | --- | --- | --- |
| [0_intro.md](0_intro.md) | Вступ | Актуальність, об'єкт, предмет, мета, завдання | Done |
| [1_analysis.md](1_analysis.md) | Розділ 1 | Підходи, аналоги, модель As-Is, модель To-Be, FR і NFRs | Done |
| [2_design.md](2_design.md) | Розділ 2 | C4 Model L1–L3 (Mermaid), ADR, матриця трасування | In Progress |
| [3_implementation.md](3_implementation.md) | Розділ 3 | Інтерфейс, тестування, розгортання | To Do |
| [4_conclusions.md](4_conclusions.md) | Висновки | Загальні висновки | To Do |

## Архітектурна документація

| Артефакт | Опис |
| --- | --- |
| [srs.md](srs.md) | Специфікація вимог за ISO/IEC/IEEE 29148: System Context, 24 функціональні вимоги, 9 бізнес-правил бонусної програми, 25 NFR, критерії верифікації, глосарій |
| [2_design.md](2_design.md) | C4 Model: [Рівень 1 — System Context](2_design.md#diagram-level1), [Рівень 2 — Container](2_design.md#diagram-level2), [Рівень 3 — Component](2_design.md#diagram-level3); матриця трасування |
| [adr/](adr/README.md) | Architecture Decision Records: [ADR-001](adr/0001-choice-of-technology.md) (запобігання подвійному бронюванню), [ADR-002](adr/0002-bonus-wallet-model.md) (модель бонусного рахунку) |
| [proposal.md](proposal.md) | Thesis Proposal (ЛР №1, доповнено бонусною програмою) |

## Робочі документи в Google Drive

Папка (доступ «Коментатор» за посиланням): [F2 Diploma — Клевач В. Р.](https://drive.google.com/drive/folders/115YhKryqAKjlZWUPCCfmWvs2Hd2C5VQK)

| Документ | Зміст |
| --- | --- |
| [F2_Diploma_Chapter1_Клевач](https://docs.google.com/document/d/1NkcRoruu8kRjw5roId7ScxTO1OYbodlD8Ze9lwYWmXo/edit?usp=sharing) | Розділ 1 (ЛР №4) |
| [F2_Diploma_Chapter2_Клевач](https://docs.google.com/document/d/1VbMz8VFq-7GQ_ku0mwdI1BxQrhUOZyWELYJPcqnYDRU/edit?usp=sharing) | Розділ 2: C4 L1–L3 (рисунки), ADR-001, ADR-002, трасування (ЛР №5) |
| [F2_LR5_SRS_Клевач](https://docs.google.com/document/d/1zXwniSNlJfzpxBOHGjQvPUN3Z_G68jEFvcQCUbd2xPc/edit?usp=sharing) | SRS за ISO/IEC/IEEE 29148 (ЛР №5) |
| [F2_LR5_AI_Disclosure_Клевач](https://docs.google.com/document/d/1XpNeurhz12Y3wPVQ6K7uIQSZyWLdZMdQV5oevauwWHc/edit?usp=sharing) | Протокол роботи з ШІ-аудиторами (ЛР №5) |

## Робочий документ Розділу 1

Зведений монолітний документ Розділу 1 (підрозділи 1.1–1.5 і висновки, 14 сторінок):

- Google Docs (доступ «Коментатор» за посиланням): [F2_Diploma_Chapter1_Клевач](https://docs.google.com/document/d/1NkcRoruu8kRjw5roId7ScxTO1OYbodlD8Ze9lwYWmXo/edit?usp=sharing)
- файл у репозиторії: [F2_Diploma_Chapter1_Klevach.docx](F2_Diploma_Chapter1_Klevach.docx)

## Нефункціональні вимоги (NFRs Matrix)

| ID | Категорія | Цільове значення |
| --- | --- | --- |
| NFR-1 | Продуктивність | p95 Latency `GET /availability` ≤ 200 мс при 200 RPS |
| NFR-2 | Продуктивність | p95 Latency `POST /bookings` ≤ 300 мс при 50 RPS |
| NFR-3 | Консистентність | 0 подвійних бронювань: 100 VU на одне місце → 1 × 201, 99 × 409 |
| NFR-4 | Надійність | Error rate (5xx) < 0,1 % |
| NFR-5 | Масштабованість | Stateless API, ≥ 2 репліки, спільний стан у PostgreSQL і Redis |
| NFR-6 | Масштабованість | Rate limit 100 запитів/хв на користувача (Redis), 429 |
| NFR-7 | Безпека | JWT (RFC 7519) Bearer: access 15 хв, refresh 7 діб з ротацією |
| NFR-8 | Безпека | Argon2id, TLS 1.2+, секрети в env / GitHub Secrets |
| NFR-9 | Комплаєнс | OWASP API Security Top 10 (2023): API1, API2, API4; GDPR |
| NFR-10 | Надійність | Відмова Redis не призводить до подвійного бронювання (`EXCLUDE USING gist`) |
| NFR-11 | Надійність | Health-checks, щодобовий `pg_dump`, RPO ≤ 24 год, RTO ≤ 1 год |
| NFR-12 | Якість коду | Покриття тестами ≥ 70 %, CI блокує merge |
| NFR-13 | Консистентність бонусів | 1 нарахування на бронювання; 20 паралельних використань бонусу → 1 успіх; баланс 0–100 |

## Календарний план

| № з/п | Назва етапу кваліфікаційної роботи | Термін виконання | Статус |
| :---: | --- | --- | :---: |
| 1 | Аналіз предметної області та програмних аналогів, формування технічного завдання | 01.10.2026 – 15.11.2026 | Done |
| 2 | Обґрунтування технологічного стеку та фіксація архітектурних рішень (ADR) | 16.11.2026 – 06.12.2026 | In Progress |
| 3 | Проєктування архітектури системи (UML, C4 Model) та логічної моделі даних | 07.12.2026 – 17.01.2027 | In Progress |
| 4 | Алгоритмізація конкурентного бронювання з блокуванням у Redis і бонусної програми, реалізація базового backend | 18.01.2027 – 26.02.2027 | To Do |
| 5 | Реалізація клієнтського інтерфейсу, контейнеризація (Docker Compose) та конвеєр CI/CD | 01.03.2027 – 28.03.2027 | To Do |
| 6 | Інструментальний аудит якості коду: модульне, інтеграційне та навантажувальне тестування | 29.03.2027 – 18.04.2027 | To Do |
| 7 | Науково-практична апробація: підготовка статті або тез доповіді | 12.04.2027 – 30.04.2027 | To Do |

> Травень 2027 р. зарезервовано під фінальний нормоконтроль і передзахист.
