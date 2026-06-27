"""
Статичные игровые данные.
"""

# ──────────────────────────────────────────────────────────────────────────
# РЕДКОСТИ ЯИЦ / ДРАКОНОВ
# ──────────────────────────────────────────────────────────────────────────
RARITIES = {
    "common":    {"name": "Обычный",      "weight": 45, "min_duel_level": 3,  "stat_mult": 1.0, "ability_slots": 1, "emoji": "⚪️", "flair": ""},
    "uncommon":  {"name": "Необычный",    "weight": 27, "min_duel_level": 4,  "stat_mult": 1.2, "ability_slots": 1, "emoji": "🟢", "flair": ""},
    "rare":      {"name": "Редкий",       "weight": 15, "min_duel_level": 5,  "stat_mult": 1.5, "ability_slots": 2, "emoji": "🔵", "flair": "✨"},
    "epic":      {"name": "Эпический",    "weight": 8,  "min_duel_level": 6,  "stat_mult": 2.0, "ability_slots": 2, "emoji": "🟣", "flair": "✨⚡️"},
    "legendary": {"name": "Легендарный",  "weight": 4,  "min_duel_level": 8,  "stat_mult": 2.8, "ability_slots": 3, "emoji": "🟡", "flair": "🌟⚡️🌟"},
    "mythic":    {"name": "Мифический",   "weight": 1,  "min_duel_level": 10, "stat_mult": 4.0, "ability_slots": 3, "emoji": "🔴", "flair": "💥🌟⚡️🌟💥"},
}
RARITY_ORDER = ["common", "uncommon", "rare", "epic", "legendary", "mythic"]

# ──────────────────────────────────────────────────────────────────────────
# СТИХИИ — теперь с разной редкостью выпадения и весами
# ──────────────────────────────────────────────────────────────────────────
# element_weight — насколько часто выпадает вид этой стихии при выборе вида
# Огонь/Вода/Земля/Ветер — обычные
# Молния/Лёд — редкие
# Свет/Тень — самые редкие и мощные
ELEMENTS = ["fire", "water", "earth", "wind", "lightning", "ice", "light", "shadow"]
ELEMENT_NAMES = {
    "fire": "Огонь", "water": "Вода", "earth": "Земля", "wind": "Ветер",
    "lightning": "Молния", "ice": "Лёд", "light": "Свет", "shadow": "Тень",
}
ELEMENT_WEIGHTS = {
    "fire": 20, "water": 20, "earth": 20, "wind": 20,
    "lightning": 8, "ice": 8,
    "light": 2, "shadow": 2,
}
# Бонусный множитель к базовым статам для редких стихий
ELEMENT_POWER_BONUS = {
    "fire": 1.0, "water": 1.0, "earth": 1.0, "wind": 1.0,
    "lightning": 1.15, "ice": 1.15,
    "light": 1.35, "shadow": 1.35,
}

# ──────────────────────────────────────────────────────────────────────────
# СПЕЦ. СПОСОБНОСТИ
# ──────────────────────────────────────────────────────────────────────────
ABILITIES = {
    "fire_breath":    {"name": "Огненное дыхание",  "element": "fire",       "base_power": 12},
    "tidal_wave":     {"name": "Волна",              "element": "water",      "base_power": 10},
    "stone_skin":     {"name": "Каменная кожа",      "element": "earth",      "base_power": 8},
    "gale_force":     {"name": "Порыв ветра",        "element": "wind",       "base_power": 10},
    "thunder_strike": {"name": "Удар молнии",        "element": "lightning",  "base_power": 16},
    "frost_bite":     {"name": "Ледяной укус",       "element": "ice",        "base_power": 14},
    "radiant_glow":   {"name": "Сияние",             "element": "light",      "base_power": 18},
    "shadow_step":    {"name": "Шаг тени",           "element": "shadow",     "base_power": 17},
}

# ──────────────────────────────────────────────────────────────────────────
# ВИДЫ ДРАКОНОВ — 8 стихий × 6 редкостей = 48 уникальных видов
# Редкие стихии (молния/лёд) и мифические (свет/тень) мощнее за счёт
# ELEMENT_POWER_BONUS, который применяется в game_logic.effective_stats
# ──────────────────────────────────────────────────────────────────────────
SPECIES = {
    # ── ОГОНЬ ─────────────────────────────────────────────────────────────
    "fire_common":    {"name": "Огненный птенец",    "element": "fire",      "rarity": "common",    "base_power": 12.0, "base_defense": 7.0,  "base_speed": 9.0},
    "fire_uncommon":  {"name": "Огненный дракончик", "element": "fire",      "rarity": "uncommon",  "base_power": 13.0, "base_defense": 7.5,  "base_speed": 9.5},
    "fire_rare":      {"name": "Огненный страж",     "element": "fire",      "rarity": "rare",      "base_power": 14.0, "base_defense": 8.0,  "base_speed": 10.0},
    "fire_epic":      {"name": "Огненный вирм",      "element": "fire",      "rarity": "epic",      "base_power": 15.0, "base_defense": 8.5,  "base_speed": 10.5},
    "fire_legendary": {"name": "Огненный архонт",    "element": "fire",      "rarity": "legendary", "base_power": 16.0, "base_defense": 9.0,  "base_speed": 11.0},
    "fire_mythic":    {"name": "Огненный первородный","element": "fire",     "rarity": "mythic",    "base_power": 17.0, "base_defense": 9.5,  "base_speed": 11.5},

    # ── ВОДА ──────────────────────────────────────────────────────────────
    "water_common":    {"name": "Морской птенец",    "element": "water",     "rarity": "common",    "base_power": 9.0,  "base_defense": 10.0, "base_speed": 9.0},
    "water_uncommon":  {"name": "Морской дракончик", "element": "water",     "rarity": "uncommon",  "base_power": 9.5,  "base_defense": 11.0, "base_speed": 9.5},
    "water_rare":      {"name": "Морской страж",     "element": "water",     "rarity": "rare",      "base_power": 10.0, "base_defense": 12.0, "base_speed": 10.0},
    "water_epic":      {"name": "Морской вирм",      "element": "water",     "rarity": "epic",      "base_power": 10.5, "base_defense": 13.0, "base_speed": 10.5},
    "water_legendary": {"name": "Морской архонт",    "element": "water",     "rarity": "legendary", "base_power": 11.0, "base_defense": 14.0, "base_speed": 11.0},
    "water_mythic":    {"name": "Морской первородный","element": "water",    "rarity": "mythic",    "base_power": 11.5, "base_defense": 15.0, "base_speed": 11.5},

    # ── ЗЕМЛЯ ─────────────────────────────────────────────────────────────
    "earth_common":    {"name": "Каменный птенец",   "element": "earth",     "rarity": "common",    "base_power": 8.0,  "base_defense": 14.0, "base_speed": 6.0},
    "earth_uncommon":  {"name": "Каменный дракончик","element": "earth",     "rarity": "uncommon",  "base_power": 8.5,  "base_defense": 15.0, "base_speed": 6.5},
    "earth_rare":      {"name": "Каменный страж",    "element": "earth",     "rarity": "rare",      "base_power": 9.0,  "base_defense": 16.0, "base_speed": 7.0},
    "earth_epic":      {"name": "Каменный вирм",     "element": "earth",     "rarity": "epic",      "base_power": 9.5,  "base_defense": 17.0, "base_speed": 7.5},
    "earth_legendary": {"name": "Каменный архонт",   "element": "earth",     "rarity": "legendary", "base_power": 10.0, "base_defense": 18.0, "base_speed": 8.0},
    "earth_mythic":    {"name": "Каменный первородный","element": "earth",   "rarity": "mythic",    "base_power": 10.5, "base_defense": 19.0, "base_speed": 8.5},

    # ── ВЕТЕР ─────────────────────────────────────────────────────────────
    "wind_common":    {"name": "Ветряной птенец",    "element": "wind",      "rarity": "common",    "base_power": 8.0,  "base_defense": 6.0,  "base_speed": 15.0},
    "wind_uncommon":  {"name": "Ветряной дракончик", "element": "wind",      "rarity": "uncommon",  "base_power": 8.5,  "base_defense": 6.5,  "base_speed": 16.0},
    "wind_rare":      {"name": "Ветряной страж",     "element": "wind",      "rarity": "rare",      "base_power": 9.0,  "base_defense": 7.0,  "base_speed": 17.0},
    "wind_epic":      {"name": "Ветряной вирм",      "element": "wind",      "rarity": "epic",      "base_power": 9.5,  "base_defense": 7.5,  "base_speed": 18.0},
    "wind_legendary": {"name": "Ветряной архонт",    "element": "wind",      "rarity": "legendary", "base_power": 10.0, "base_defense": 8.0,  "base_speed": 19.0},
    "wind_mythic":    {"name": "Ветряной первородный","element": "wind",     "rarity": "mythic",    "base_power": 10.5, "base_defense": 8.5,  "base_speed": 20.0},

    # ── МОЛНИЯ (редкая стихия, +15% к статам через ELEMENT_POWER_BONUS) ──
    "lightning_common":    {"name": "Грозовой птенец",    "element": "lightning", "rarity": "common",    "base_power": 13.0, "base_defense": 5.0,  "base_speed": 13.0},
    "lightning_uncommon":  {"name": "Грозовой дракончик", "element": "lightning", "rarity": "uncommon",  "base_power": 14.0, "base_defense": 5.5,  "base_speed": 14.0},
    "lightning_rare":      {"name": "Грозовой страж",     "element": "lightning", "rarity": "rare",      "base_power": 15.0, "base_defense": 6.0,  "base_speed": 15.0},
    "lightning_epic":      {"name": "Грозовой вирм",      "element": "lightning", "rarity": "epic",      "base_power": 16.0, "base_defense": 6.5,  "base_speed": 16.0},
    "lightning_legendary": {"name": "Грозовой архонт",    "element": "lightning", "rarity": "legendary", "base_power": 17.0, "base_defense": 7.0,  "base_speed": 17.0},
    "lightning_mythic":    {"name": "Грозовой первородный","element": "lightning","rarity": "mythic",    "base_power": 18.0, "base_defense": 7.5,  "base_speed": 18.0},

    # ── ЛЁД (редкая стихия, +15% к статам через ELEMENT_POWER_BONUS) ─────
    "ice_common":    {"name": "Ледяной птенец",    "element": "ice",  "rarity": "common",    "base_power": 11.0, "base_defense": 9.0,  "base_speed": 7.0},
    "ice_uncommon":  {"name": "Ледяной дракончик", "element": "ice",  "rarity": "uncommon",  "base_power": 12.0, "base_defense": 10.0, "base_speed": 7.5},
    "ice_rare":      {"name": "Ледяной страж",     "element": "ice",  "rarity": "rare",      "base_power": 13.0, "base_defense": 11.0, "base_speed": 8.0},
    "ice_epic":      {"name": "Ледяной вирм",      "element": "ice",  "rarity": "epic",      "base_power": 14.0, "base_defense": 12.0, "base_speed": 8.5},
    "ice_legendary": {"name": "Ледяной архонт",    "element": "ice",  "rarity": "legendary", "base_power": 15.0, "base_defense": 13.0, "base_speed": 9.0},
    "ice_mythic":    {"name": "Ледяной первородный","element": "ice",  "rarity": "mythic",    "base_power": 16.0, "base_defense": 14.0, "base_speed": 9.5},

    # ── СВЕТ (мифическая стихия, +35% к статам через ELEMENT_POWER_BONUS) ─
    "light_common":    {"name": "Солнечный птенец",    "element": "light", "rarity": "common",    "base_power": 11.0, "base_defense": 9.0,  "base_speed": 11.0},
    "light_uncommon":  {"name": "Солнечный дракончик", "element": "light", "rarity": "uncommon",  "base_power": 12.0, "base_defense": 10.0, "base_speed": 12.0},
    "light_rare":      {"name": "Солнечный страж",     "element": "light", "rarity": "rare",      "base_power": 13.0, "base_defense": 11.0, "base_speed": 13.0},
    "light_epic":      {"name": "Солнечный вирм",      "element": "light", "rarity": "epic",      "base_power": 14.0, "base_defense": 12.0, "base_speed": 14.0},
    "light_legendary": {"name": "Солнечный архонт",    "element": "light", "rarity": "legendary", "base_power": 15.0, "base_defense": 13.0, "base_speed": 15.0},
    "light_mythic":    {"name": "Солнечный первородный","element": "light", "rarity": "mythic",   "base_power": 16.0, "base_defense": 14.0, "base_speed": 16.0},

    # ── ТЕНЬ (мифическая стихия, +35% к статам через ELEMENT_POWER_BONUS) ─
    "shadow_common":    {"name": "Тёмный птенец",    "element": "shadow", "rarity": "common",    "base_power": 14.0, "base_defense": 6.0,  "base_speed": 12.0},
    "shadow_uncommon":  {"name": "Тёмный дракончик", "element": "shadow", "rarity": "uncommon",  "base_power": 15.0, "base_defense": 6.5,  "base_speed": 13.0},
    "shadow_rare":      {"name": "Тёмный страж",     "element": "shadow", "rarity": "rare",      "base_power": 16.0, "base_defense": 7.0,  "base_speed": 14.0},
    "shadow_epic":      {"name": "Тёмный вирм",      "element": "shadow", "rarity": "epic",      "base_power": 17.0, "base_defense": 7.5,  "base_speed": 15.0},
    "shadow_legendary": {"name": "Тёмный архонт",    "element": "shadow", "rarity": "legendary", "base_power": 18.0, "base_defense": 8.0,  "base_speed": 16.0},
    "shadow_mythic":    {"name": "Тёмный первородный","element": "shadow", "rarity": "mythic",   "base_power": 19.0, "base_defense": 8.5,  "base_speed": 17.0},
}

STARTER_SPECIES_KEY = "fire_common"

# ──────────────────────────────────────────────────────────────────────────
# СТАДИИ РОСТА ДРАКОНА
# ──────────────────────────────────────────────────────────────────────────
# Дракон проходит стадии роста. На каждой стадии есть таймер.
# hatch_hours — сколько часов нужно ждать до перехода на следующую стадию
# stat_mult   — множитель к статам на этой стадии
GROWTH_STAGES = {
    "egg":     {"name": "Яйцо",       "emoji": "🥚", "hatch_hours": 0,   "stat_mult": 0.0},  # не дракон ещё
    "baby":    {"name": "Детёныш",    "emoji": "🐣", "hatch_hours": 2,   "stat_mult": 0.5},  # 2 часа → подросток
    "teen":    {"name": "Подросток",  "emoji": "🐲", "hatch_hours": 6,   "stat_mult": 0.8},  # 6 часов → взрослый
    "adult":   {"name": "Взрослый",   "emoji": "🐉", "hatch_hours": 0,   "stat_mult": 1.0},  # финальная стадия
}
GROWTH_ORDER = ["baby", "teen", "adult"]

# ──────────────────────────────────────────────────────────────────────────
# БРОНЯ
# ──────────────────────────────────────────────────────────────────────────
ARMOR_CATALOG = {
    "leather_scale":  {"name": "Кожаная чешуя",      "price": 80,  "defense_bonus": 3},
    "iron_plate":     {"name": "Железная пластина",   "price": 220, "defense_bonus": 7},
    "mythic_shell":   {"name": "Мифический панцирь",  "price": 600, "defense_bonus": 15},
}

# ──────────────────────────────────────────────────────────────────────────
# ЭКОНОМИКА
# ──────────────────────────────────────────────────────────────────────────
FEED_MEAT_COST = 3          # снизили с 5 до 3 — новичку легче
FEED_EXP_GAIN = 15
FEED_FATIGUE_DELTA = -3

TRAIN_COIN_COST = 20
TRAIN_MEAT_COST = 8         # снизили с 10 до 8
TRAIN_EXP_GAIN = 35
TRAIN_FATIGUE_DELTA = 18

FATIGUE_SOFT_CAP = 50
FATIGUE_HARD_CAP = 100
FATIGUE_DECAY_PER_HOUR = 4
FATIGUE_REST_HOURS = 6


def exp_to_next_level(level: int) -> int:
    return 50 + level * 25


# ──────────────────────────────────────────────────────────────────────────
# ЕЖЕДНЕВНЫЕ ЗАДАНИЯ
# ──────────────────────────────────────────────────────────────────────────
QUEST_TEMPLATES = {
    "login":     {"name": "Зайти в бота",                      "target": 1,      "reward_coins": 15, "reward_meat": 5,  "requires_dragon": False},
    "explore":   {"name": "Исследовать {t} локацию(и)",          "target": (1, 2), "reward_coins": 20, "reward_meat": 15, "requires_dragon": False},
    "feed":      {"name": "Покормить дракона {t} раз(а)",        "target": (1, 2), "reward_coins": 15, "reward_meat": 5,  "requires_dragon": True},
    "train":     {"name": "Потренировать дракона {t} раз(а)",    "target": (1, 1), "reward_coins": 25, "reward_meat": 0,  "requires_dragon": True},
    "duel_play": {"name": "Сыграть {t} дуэль(и)",                "target": (1, 1), "reward_coins": 30, "reward_meat": 10, "requires_dragon": True},
}
QUEST_EXTRA_COUNT = 2

BONUS_ALL_QUESTS_COINS = 40
BONUS_ALL_QUESTS_MEAT = 20

QUEST_STREAK_BONUS_PER_DAY = 0.08
QUEST_STREAK_CAP_DAYS = 14


def quest_streak_multiplier(streak_days: int) -> float:
    return 1 + min(streak_days, QUEST_STREAK_CAP_DAYS) * QUEST_STREAK_BONUS_PER_DAY


# ──────────────────────────────────────────────────────────────────────────
# СЕЗОННЫЙ ТОП
# ──────────────────────────────────────────────────────────────────────────
SEASON_TOP_SNAPSHOT_SIZE = 20


def season_reward_for_rank(rank: int) -> tuple[int, int]:
    if rank == 1:
        return 1000, 300
    if rank <= 3:
        return 600, 200
    if rank <= 10:
        return 300, 100
    if rank <= SEASON_TOP_SNAPSHOT_SIZE:
        return 120, 50
    return 0, 0

# ──────────────────────────────────────────────────────────────────────────
# РАНГИ (по клыкам, как в Brawl Stars)
# ──────────────────────────────────────────────────────────────────────────
RANKS = [
    {"name": "Яйцо",          "emoji": "🥚",  "min_fangs": 0,    "fangs_gain": 5,  "fangs_loss": 3},
    {"name": "Птенец",        "emoji": "🐣",  "min_fangs": 30,   "fangs_gain": 6,  "fangs_loss": 4},
    {"name": "Чешуйка",       "emoji": "🐍",  "min_fangs": 80,   "fangs_gain": 7,  "fangs_loss": 5},
    {"name": "Коготь",        "emoji": "🦅",  "min_fangs": 160,  "fangs_gain": 8,  "fangs_loss": 6},
    {"name": "Дракончик",     "emoji": "🐲",  "min_fangs": 280,  "fangs_gain": 9,  "fangs_loss": 7},
    {"name": "Страж",         "emoji": "🛡️",  "min_fangs": 450,  "fangs_gain": 10, "fangs_loss": 8},
    {"name": "Вирм",          "emoji": "🐉",  "min_fangs": 680,  "fangs_gain": 11, "fangs_loss": 9},
    {"name": "Архонт",        "emoji": "⚔️",  "min_fangs": 980,  "fangs_gain": 12, "fangs_loss": 10},
    {"name": "Древний Вирм",  "emoji": "🌋",  "min_fangs": 1400, "fangs_gain": 14, "fangs_loss": 11},
    {"name": "Первородный",   "emoji": "👑",  "min_fangs": 2000, "fangs_gain": 16, "fangs_loss": 12},
]

def get_rank(fangs: int) -> dict:
    rank = RANKS[0]
    for r in RANKS:
        if fangs >= r["min_fangs"]:
            rank = r
    rank_idx = RANKS.index(rank)
    next_rank = RANKS[rank_idx + 1] if rank_idx + 1 < len(RANKS) else None
    return {"rank": rank, "next_rank": next_rank, "rank_idx": rank_idx}


# ──────────────────────────────────────────────────────────────────────────
# БОССЫ ЛОКАЦИЙ
# ──────────────────────────────────────────────────────────────────────────
LOCATION_BOSSES = {
    "forest": [
        {"name": "Лесной Тролль",    "emoji": "👹", "base_power": 15, "base_defense": 10, "base_speed": 6,  "reward_meat": 25, "reward_coins": 30, "egg_chance": 0.2},
        {"name": "Гигантский Волк",  "emoji": "🐺", "base_power": 20, "base_defense": 8,  "base_speed": 14, "reward_meat": 30, "reward_coins": 40, "egg_chance": 0.25},
        {"name": "Лесной Дух",       "emoji": "🌿", "base_power": 28, "base_defense": 15, "base_speed": 10, "reward_meat": 40, "reward_coins": 60, "egg_chance": 0.35},
    ],
    "mountains": [
        {"name": "Горный Великан",   "emoji": "🗿", "base_power": 25, "base_defense": 20, "base_speed": 4,  "reward_meat": 35, "reward_coins": 50, "egg_chance": 0.25},
        {"name": "Каменный Голем",   "emoji": "🪨", "base_power": 18, "base_defense": 30, "base_speed": 3,  "reward_meat": 40, "reward_coins": 55, "egg_chance": 0.3},
        {"name": "Горный Дракон",    "emoji": "🐉", "base_power": 35, "base_defense": 22, "base_speed": 12, "reward_meat": 55, "reward_coins": 80, "egg_chance": 0.4},
    ],
    "caves": [
        {"name": "Пещерный Паук",    "emoji": "🕷️", "base_power": 22, "base_defense": 12, "base_speed": 18, "reward_meat": 30, "reward_coins": 45, "egg_chance": 0.3},
        {"name": "Тёмный Страж",     "emoji": "💀", "base_power": 30, "base_defense": 18, "base_speed": 8,  "reward_meat": 45, "reward_coins": 65, "egg_chance": 0.35},
        {"name": "Подземный Вирм",   "emoji": "🐛", "base_power": 40, "base_defense": 25, "base_speed": 6,  "reward_meat": 60, "reward_coins": 90, "egg_chance": 0.45},
    ],
}

# Названия драконов по видам
SPECIES_NAMES = {
    "fire_common":         "Пепельный Искрик",
    "fire_uncommon":       "Огненный Коготь",
    "fire_rare":           "Вулканий",
    "fire_epic":           "Инферно",
    "fire_legendary":      "Пламенный Архонт",
    "fire_mythic":         "Солнечный Вирм",
    "water_common":        "Брызгун",
    "water_uncommon":      "Волновой Клык",
    "water_rare":          "Морской Рыцарь",
    "water_epic":          "Тёмный Прилив",
    "water_legendary":     "Океанский Владыка",
    "water_mythic":        "Левиафан",
    "earth_common":        "Булыжник",
    "earth_uncommon":      "Каменный Зуб",
    "earth_rare":          "Гранитный Страж",
    "earth_epic":          "Горный Колосс",
    "earth_legendary":     "Каменный Архонт",
    "earth_mythic":        "Титан Земли",
    "wind_common":         "Ветерок",
    "wind_uncommon":       "Вихревой Коготь",
    "wind_rare":           "Штормовой Клинок",
    "wind_epic":           "Циклон",
    "wind_legendary":      "Повелитель Бурь",
    "wind_mythic":         "Вечный Ураган",
    "lightning_common":    "Искровик",
    "lightning_uncommon":  "Грозовой Укус",
    "lightning_rare":      "Разрядник",
    "lightning_epic":      "Громовержец",
    "lightning_legendary": "Молниевый Архонт",
    "lightning_mythic":    "Небесный Тиран",
    "ice_common":          "Снежок",
    "ice_uncommon":        "Ледяной Клык",
    "ice_rare":            "Морозный Страж",
    "ice_epic":            "Ледяной Колосс",
    "ice_legendary":       "Вечная Зима",
    "ice_mythic":          "Ледяной Первородный",
    "light_common":        "Лучик",
    "light_uncommon":      "Солнечный Клык",
    "light_rare":          "Рассветный Страж",
    "light_epic":          "Небесный Судья",
    "light_legendary":     "Сияющий Архонт",
    "light_mythic":        "Солнечный Первородный",
    "shadow_common":       "Тенёк",
    "shadow_uncommon":     "Тёмный Коготь",
    "shadow_rare":         "Ночной Охотник",
    "shadow_epic":         "Теневой Вирм",
    "shadow_legendary":    "Тёмный Архонт",
    "shadow_mythic":       "Тень Бездны",
}


def species_display_name(species_key: str) -> str:
    """Красивое название вида (из SPECIES_NAMES), с фолбэком на старое имя,
    если для вида ещё не задано имя из таблицы."""
    return SPECIES_NAMES.get(species_key) or SPECIES[species_key]["name"]
