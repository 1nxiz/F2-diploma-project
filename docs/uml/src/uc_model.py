"""Single source of truth for the Use Case diagram (names, layout, relations)."""

SUBJECT = {"name": "CoWork Booking System", "x0": 250, "y0": 40, "x1": 1160, "y1": 960}

# id: (label, cx, cy)
ACTORS = {
    "guest": ("Гість", 110, 150),
    "resident": ("Резидент", 110, 500),
    "admin": ("Адміністратор", 110, 800),
    "timer": ("Таймер (Scheduler)", 110, 930),
    "llm": ("LLM Provider", 1290, 480),
    "email": ("Email Service", 1290, 930),
}

USE_CASES = {
    "uc01": ("UC-01 Зареєструватися", 470, 100),
    "uc02": ("UC-02 Увійти в систему", 470, 180),
    "uc03": ("UC-03 Знайти вільні місця", 470, 270),
    "uc04": ("UC-04 Забронювати місце вручну", 470, 355),
    "uc05": ("UC-05 Забронювати через AI-асистента", 470, 440),
    "uc07": ("UC-07 Скасувати бронювання", 470, 640),
    "uc08": ("UC-08 Переглянути бонусний рахунок", 470, 730),
    "uc10": ("UC-10 Керувати каталогом місць", 470, 830),
    "uc11": ("UC-11 Завершити бронювання та нарахувати бали", 470, 930),
    "uc09": ("UC-09 Використати безкоштовну годину", 830, 200),
    "uc14": ("UC-14 Утримати місце (hold)", 830, 300),
    "uc12": ("UC-12 Перевірити денний ліміт 8 год", 830, 390),
    "uc13": ("UC-13 Розпізнати запит (NL → обмеження)", 830, 480),
    "uc16": ("UC-16 Оптимізувати розподіл і пояснити вибір", 830, 580),
    "uc15": ("UC-15 Уточнити запит", 470, 540),
    "uc06": ("UC-06 Підібрати групу місць поруч", 830, 690),
    "uc17": ("UC-17 Надіслати сповіщення про 100 балів", 1030, 930),
}

ASSOCIATIONS = [
    ("guest", "uc01"), ("guest", "uc02"),
    ("resident", "uc03"), ("resident", "uc04"), ("resident", "uc05"),
    ("resident", "uc07"), ("resident", "uc08"),
    ("admin", "uc10"),
    ("timer", "uc11"),
    ("llm", "uc13"),
    ("email", "uc17"),
]
GENERALIZATIONS = [("admin", "resident")]  # child -> parent
INCLUDES = [  # base -> included
    ("uc04", "uc14"), ("uc04", "uc12"),
    ("uc05", "uc14"), ("uc05", "uc12"), ("uc05", "uc13"), ("uc05", "uc16"),
]
EXTENDS = [  # extension -> base
    ("uc09", "uc04"), ("uc15", "uc05"), ("uc06", "uc05"), ("uc17", "uc11"),
]

UC_W, UC_H = 236, 62
ACTOR_W, ACTOR_H = 40, 80

# bend points for edges that would otherwise cross a use case ellipse
WAYPOINTS = {}
