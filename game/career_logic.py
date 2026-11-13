import json
import random
import renpy


TRAIT_LABELS = {
    "workhorse": "Трудяга",
    "leader": "Прирождённый лидер",
    "talent": "Скрытый талант",
    "glass": "Стеклянный",
    "scandalist": "Скандалист",
    "partygoer": "Кутила",
    "joker": "Балагур",
    "cheburek_fan": "Любитель чебуреков",
    "lucky": "Счастливчик",
    "trash_talker": "Трэш-токер",
    "investor": "Крипто-инвестор 90-х",
    "homesick": "Маменькин сынок",
    "ice_cold": "Хладнокровный",
}

SKILL_ALIASES = {
    **dict.fromkeys(("shooting", "dribbling", "first_touch", "defending", "heading"), "tec"),
    **dict.fromkeys(("speed", "stamina", "strength", "agility"), "phy"),
    **dict.fromkeys(("vision", "passing"), "vis"),
    "composure": "com",
}

POSITION_SKILLS = {
    "GK": ("phy", "com"), "DEF": ("phy", "com"),
    "MID": ("tec", "vis"), "FWD": ("tec", "phy"),
}


def career_random():
    return getattr(renpy, "random", random)


CHECK_HINTS = {
    "tec": "Ты вспоминаешь часы с мячом у стены.",
    "dribbling": "Ты чувствуешь мяч близко к ноге — но соперник уже рядом.",
    "first_touch": "Первое касание решит всё.",
    "phy": "Ноги тяжелеют, но ты ещё можешь ускориться.",
    "stamina": "Ты переводишь дыхание и собираешь остаток сил.",
    "strength": "Соперник давит плечом. Устоишь ли ты?",
    "speed": "Перед тобой свободный коридор — нужен рывок.",
    "agility": "Ты ловишь момент, чтобы резко сменить направление.",
    "vis": "Ты ищешь свободного партнёра среди движущихся фигур.",
    "vision": "Ты замечаешь поле целиком и ищешь тонкий пас.",
    "passing": "Точность передачи сейчас важнее силы.",
    "com": "Ты чувствуешь, как предательски дрожат колени.",
    "composure": "Ты чувствуешь, как предательски дрожат колени.",
    "professionalism": "Тренер смотрит внимательно — привычка к режиму может помочь.",
    "consistency": "Один эпизод не решает всё: важна твоя стабильность.",
    "clutch": "Стадион затих. Это тот самый решающий момент.",
}


RELATION_KEYS = {"rel_coach", "rel_agent", "rel_captain", "rel_rival", "rel_journalist"}
TOP_CLUBS = {"Спартак (М)", "ЦСКА", "Динамо (М)"}
MID_CLUBS = {"Ротор", "Асмарал", "Локомотив (М)", "Спартак (Вл)", "Торпедо", "Локомотив (НН)"}
LEGACY_MONEY_PER_DOLLAR = 100
MONTHLY_LIVING_COST = 150

ITEMS = {
    "boots": ("Футбольные бутсы", "boots"),
    "fake_boots": ("Рыночные бутсы", "boots"),
    "player": ("Кассетный плеер «Вега»", "player"),
    "programme": ("Матчевая программка", "programme"),
    "gloves": ("Вратарские перчатки", "gloves"),
    "dendy": ("Приставка Dendy", "dendy"),
    "clipping": ("Газетная вырезка", "clipping"),
    "shirt": ("Футболка соперника", "shirt"),
}

MATCH_SKILLS = {"GK": "vis", "DEF": "phy", "MID": "vis", "FWD": "tec"}


BENFICA_SALARY = 1500
BENFICA_WIN_BONUS = 500


def calculate_salary(club):
    """Monthly salary on the demo's USD scale."""
    if club == "Бенфика":
        return BENFICA_SALARY
    if club in TOP_CLUBS:
        return 1200
    if club in MID_CLUBS:
        return 500
    return 200


def match_count_text(count):
    if 11 <= count % 100 <= 14:
        noun = "матчей"
    else:
        noun = {1: "матч", 2: "матча", 3: "матча", 4: "матча"}.get(count % 10, "матчей")
    return "{} {}".format(count, noun)


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.position = None
        self.nation = None
        self.club = None
        self.league = None
        self.difficulty = None
        self.club_difficulty = None
        self.mode_realism = True
        self.trait = None
        self.age = 16
        self.season = 1
        self.rumor_score = 0
        self.suspicion = 0
        self.press_delta = 0
        self.crisis_reviewed = False
        self.charity_roll_season = 0
        self.interview_roll_season = 0
        self.transfer_offer = None
        self.usd_economy = True
        self.fixing_amount = 0
        self.first_1993 = []
        self.first_1994 = []
        self.season_fixture_scores = {}
        self.art_last = {}
        self.goalless_matches = 0
        self.next_match_phy = 0
        self.match_phy_modifier = 0
        self.zone_1993 = None
        self.snitch_matches = 0
        self.ban_months = 0
        self.paid_matches = []
        self.playoff_results = {}
        self.agent_bonus = 0
        self.payroll_season = 0
        self.payroll_month = 0
        self.living_expense_season = 0
        self.living_expense_month = 0
        self.living_spent = 0
        self.salary_debt = 0
        self.debt_club = None
        self.hold_paycheck = False
        self.club_bonus_season = 0
        self.objective_bonus_season = 0
        self.season_wins = 0
        self.inventory = {}
        self.personal_training = False

        self.stress = 0
        self.start_stress = 0
        self.breakdowns = 0
        self.breakdown_pending = False
        self.breakdown_incident = None
        self.current_place = 1
        self.ptsd = False

        # Четыре видимых характеристики героя.
        self.attrs = {
            "tec": 40, "phy": 45, "vis": 40, "com": 45,
            # Совместимость с уже написанными событиями и интерфейсом.
            "shooting": 40, "passing": 40, "dribbling": 40,
            "first_touch": 40, "defending": 40, "heading": 40,
            "speed": 50, "stamina": 50, "strength": 45, "agility": 45,
            "vision": 40, "composure": 50, "leadership": 40,
            "aggression": 50, "work_ethic": 55,
            "rep_coach": 50, "rep_fans": 50, "rep_press": 50,
            "rep_teammates": 50, "media": 30, "money": 0,
            "loyalty": 50, "ambition": 50,
            "rel_coach": 0, "rel_agent": 0, "rel_captain": 0,
            "rel_rival": 0, "rel_journalist": 0, "rel_family": 50,
        }
        self.hidden_attrs = {
            "professionalism": 50, "consistency": 45, "temperament": 50,
            "injury_prone": 35, "clutch": 40,
        }
        # Совместимость со старыми сценами, которые читают эти значения из attrs.
        self.attrs.update(self.hidden_attrs)

        self.flags = {}
        self.counters = {
            "red_cards": 0, "scandals_moderate": 0, "scandals_severe": 0,
            "doping_risk": 0, "fixing_debt": 0, "media_crises": 0,
        }
        self.team_modifiers = []
        self.match_scores = {}
        self.fired_events = []
        self.season_history = []
        self.titles_league = 0  # медали за попадание в тройку
        self.titles_gold = 0    # отдельная награда за первое место
        self.titles_cup = 0
        self.titles_lc = 0
        self.national_titles = 0
        self.goals = 0
        self.appearances = 0
        self.captain = False
        self.injury_severe = False
        self.injury_months = 0
        self.suspension_matches = 0
        self.stress_warning = False
        self.pressure_count = 0
        self.press_issues = {}
        self.family_support = 0
        self.relationship = 0
        self.coach_review_due = False
        self.exile_discussed = False
        self.board_appearances = 0
        self.board_goals = 0
        self.month = 3
        self.training_focus = None
        self.training_bonus = 0
        self.fatigue = 0
        self.opponent = None
        self.national_calls = 0
        self.clubs_played = 1

    def set_trait(self, trait):
        self.trait = trait if trait in TRAIT_LABELS else "cheburek_fan"
        bonuses = {
            "workhorse": {"phy": 10},
            "leader": {"rep_coach": 10},
            "talent": {"vis": 10},
            "glass": {"tec": 10},
            "scandalist": {"media": 10},
            "joker": {"rep_teammates": 10, "rep_coach": -10},
            "ice_cold": {"com": 5, "clutch": 5},
        }
        for key, value in bonuses.get(self.trait, {}).items():
            self.mod(key, value)

    def migrate(self, clubs_data=None):
        state = vars(self)
        needs_place = "current_place" not in state
        if "living_expense_season" not in state:
            self.living_expense_season = self.season
            self.living_expense_month = max(0, self.month - 1) if "month" in state else 0
            if state.get("payroll_season") == self.season:
                self.living_expense_month = max(self.living_expense_month, self.payroll_month)
        defaults = GameState()
        self.attrs.setdefault("money", defaults.attrs["money"])
        if not state.get("usd_economy", False):
            self.attrs["money"] = round(self.attrs["money"] / LEGACY_MONEY_PER_DOLLAR)
            self.usd_economy = True

        self.fixing_amount = state.get("fixing_amount", 3000 if self.has_flag("fixing_debt") else 0)
        self.mode_realism = state.get("mode_realism", self.flags.get("mode_realism", defaults.mode_realism))
        self.ptsd = state.get("ptsd", self.flags.get("ptsd", defaults.ptsd))

        state.setdefault("hidden_attrs", {})
        for key, value in vars(defaults).items():
            state.setdefault(key, value)

        # Saves from before the four visible skills store the original ratings.
        for skill, legacy in {"tec": "shooting", "phy": "stamina",
                              "vis": "vision", "com": "composure"}.items():
            if legacy in self.attrs:
                self.attrs.setdefault(skill, self.attrs[legacy])
        for key, value in defaults.attrs.items():
            self.attrs.setdefault(key, value)
        for key, value in defaults.hidden_attrs.items():
            self.hidden_attrs.setdefault(key, self.attrs.get(key, value))
            self.attrs[key] = self.hidden_attrs[key]
        for key, value in defaults.counters.items():
            self.counters.setdefault(key, value)

        if "S3_SENIOR_CALL" in self.fired_events:
            self.set_flag("senior_call")
        self.set_flag("not_in_squad", self.attrs["rep_coach"] < 30)
        if self.has_flag("not_in_squad"):
            self.set_flag("squad_exile")
        if needs_place and clubs_data and self.club and self.nation in clubs_data and self.league in ("first", "second"):
            self.update_place(clubs_data)

    def begin_season(self):
        self.training_focus = None
        self.training_bonus = 0
        self.agent_bonus = 0
        if self.trait == "partygoer":
            self.mod("phy", -5)
        if self.trait == "investor":
            self.set_flag("vouchers")

    def train(self, skill, fatigue=0):
        self.training_focus = skill
        self.fatigue += fatigue
        self.training_bonus = 2
        self.mod(skill, 2)

    def use_training_time(self, sessions):
        self.training_bonus = max(0, self.training_bonus - sessions)

    def grow(self):
        if self.training_focus:
            self.mod(self.training_focus, self.training_bonus)
        if self.age >= 31:
            self.mod("phy", -3)
            self.mod("tec", -2)
            if self.age >= 34:
                self.mod("vis", -1)
                self.mod("com", -1)
            return
        minimum = 4 if self.age <= 20 else 2 if self.age <= 25 else 0
        professionalism = self.hidden_attrs["professionalism"]
        for key in POSITION_SKILLS.get(self.position, ("tec", "phy")):
            growth = career_random().randint(minimum, minimum + 2)
            growth += int(professionalism >= 60) - int(professionalism <= 30)
            self.mod(key, max(0, growth - int(self.trait == "lucky")))

    def set_month(self, month):
        month = max(self.month, month)
        elapsed = month - self.month
        served = min(self.suspension_matches, elapsed)
        self.recover(elapsed)
        if elapsed:
            self.add_stress(-4 * elapsed)
            # Calendar rounds between playable scenes can serve a sporting ban.
            self.suspension_matches -= served
        self.ban_months = max(0, self.ban_months - elapsed)
        self.fatigue = max(0, self.fatigue - elapsed * 4)
        self.month = month
        if elapsed:
            self.rumor_score -= min(abs(self.rumor_score), 5 * elapsed) * (1 if self.rumor_score > 0 else -1)

        return served

    def advance_offseason(self):
        self.recover(3)
        self.ban_months = max(0, self.ban_months - 3)
        self.fatigue = 0
        self.month = 3

    def recover(self, months):
        self.injury_months = max(0, self.injury_months - months)
        self.injury_severe = self.injury_months > 0 and (self.injury_severe or self.injury_months >= 3)

    def injure(self, months):
        self.injury_months = max(self.injury_months, months)
        self.injury_severe = self.injury_severe or self.injury_months >= 3

    def transfer(self, club, league="first"):
        if club != self.club:
            self.league = league
            self.club = club
            self.clubs_played += 1

    def mod(self, key, val):
        key = SKILL_ALIASES.get(key, key)
        val = int(val)
        if key in self.hidden_attrs:
            self.hidden_attrs[key] = max(1, min(100, self.hidden_attrs.get(key, 50) + val))
            self.attrs[key] = self.hidden_attrs[key]
            return
        if key == "money":
            self.attrs[key] += val
        elif key.startswith("rep_") or key == "media":
            self.mod_rep(key, val)
        elif key in self.attrs:
            lower = -100 if key in RELATION_KEYS else 1
            self.attrs[key] = max(lower, min(100, self.attrs[key] + val))

    def mod_rep(self, rep_name, amount):
        old = self.attrs[rep_name]
        new = max(1, min(100, old + amount))
        self.attrs[rep_name] = new
        if rep_name == "rep_coach":
            if old >= 30 > new:
                self.exile_discussed = False
            self.set_flag("not_in_squad", new < 30)
            self.set_flag("squad_exile", new < 30)
        elif rep_name == "rep_fans" and old >= 20 > new:
            self.add_stress(10)
        elif rep_name == "rep_press" and old >= 30 > new:
            self.add_stress(15)

    def restore_squad(self):
        self.mod_rep("rep_coach", max(0, 30 - self.attrs["rep_coach"]))
        self.set_flag("not_in_squad", False)
        self.set_flag("squad_exile", False)
        self.coach_review_due = False
        self.exile_discussed = False

    def plan_exile_transfer(self, clubs_data):
        teams = league_teams(self, clubs_data)
        current = next(team for team in teams if team["name"] == self.club)
        others = [team for team in teams if team["name"] != self.club]
        self.transfer_offer = min(others, key=lambda team: abs(team["base"] - current["base"]))["name"] if others else None
        self.set_flag("exile_transfer_pending", self.transfer_offer is not None)

    def register_press(self, delta):
        previous = self.rumor_score
        self.rumor_score = max(-100, min(100, previous + delta))
        self.press_delta = delta
        if self.rumor_score > -15 and self.suspicion < 2:
            self.crisis_reviewed = False
        active = self.rumor_score <= -30 or self.suspicion >= 2
        self.set_flag("career_crisis", active and not self.crisis_reviewed)

    def close_crisis_talk(self):
        self.crisis_reviewed = True
        self.set_flag("career_crisis", False)

    def press_headline(self):
        if self.press_delta > 0:
            return "positive"
        if self.press_delta <= -20 or self.rumor_score <= -30 or self.suspicion >= 2:
            return "critical"
        return "negative"

    def roll_charity(self):
        if self.charity_roll_season == self.season:
            return False
        self.charity_roll_season = self.season
        return career_random().randrange(100) < 20

    def next_press_issue(self, headlines, topic, tone):
        # Remember which stories ran and rotate the copy for a repeated situation.
        key = (self.season, self.month, topic, tone)
        if key in self.press_issues:
            return None
        edition = sum(k[2:] == (topic, tone) for k in self.press_issues)
        options = headlines[topic][tone]
        self.press_issues[key] = edition
        return options[edition % len(options)]

    def roll_interview(self):
        if self.rumor_score >= -10 or self.interview_roll_season == self.season:
            return False
        self.interview_roll_season = self.season
        return career_random().randrange(100) < 30

    def prepare_1993(self, clubs_data):
        roster = clubs_data["season_1993"]
        first = list(roster["first"])
        if self.league == "first" and self.club not in first:
            first[-1] = self.club
        elif self.league == "second" and self.club in first:
            candidates = ("Зенит", "Факел", "Кубань", "Динамо-Газовик", "Шинник")
            first[first.index(self.club)] = next(name for name in candidates if name not in first)
        self.first_1993 = first
        self.zone_1993 = next((zone for zone, names in roster["zones"].items() if self.club in names),
                              roster["extra_zones"].get(self.club, "Центр"))
        self.set_flag("youth_call", self.age < 20 and
                      (self.attrs["media"] > 80 or (self.appearances >= 3 and self.attrs["rep_coach"] >= 50)))
        if self.has_flag("youth_call"):
            self.national_calls += 1
        self.playoff_results = {}

    def miss_match_reason(self):
        if self.ban_months or self.has_flag("contract_terminated"):
            return "Дисквалификация: тебя не допускают к матчам."
        if self.suspension_matches:
            self.suspension_matches -= 1
            if self.suspension_matches:
                return "Ты пропускаешь матч. Остаток дисквалификации: {}.".format(match_count_text(self.suspension_matches))
            return "Ты пропускаешь последний матч дисквалификации. Со следующего тура тебя можно заявить."
        if self.injury_months:
            return "Ты смотришь матч с трибуны. Врач пока не разрешает вернуться."
        if self.has_flag("not_in_squad") or self.has_flag("squad_exile"):
            return "Тренер оставляет тебя вне заявки. Нужно вернуть его доверие."
        return ""

    def discipline(self, incident):
        self.mod("money", -1000)
        if incident == "referee":
            self.suspension_matches = max(3, self.suspension_matches)
            self.set_flag("european_ban")

    def settle_living_expenses(self, month):
        if not self.club or self.season > 4:
            return 0
        if self.living_expense_season != self.season:
            self.living_expense_season = self.season
            self.living_expense_month = 0
        months = max(0, min(12, month) - self.living_expense_month)
        self.living_expense_month += months
        cost = months * MONTHLY_LIVING_COST
        self.living_spent += cost
        self.mod("money", -cost)
        return cost

    def advance_finances(self, month):
        self.pay_salary_through(month)
        self.settle_living_expenses(month)

    def european_offer_blocker(self):
        if self.position not in ("FWD", "MID"):
            return None
        if self.has_flag("contract_terminated"):
            return "Контракт расторгнут."
        if self.has_flag("european_ban"):
            return "Оформление перехода заблокировано федерацией."
        if self.has_flag("agent_changed"):
            return "После разрыва с агентом некому вести переговоры."
        if self.attrs["rep_coach"] < 35:
            return "Тренер пока не готов дать рекомендацию."
        if self.attrs["media"] < 60:
            return "Скауты пока не запросили переговоры."
        return None

    def pay_salary_through(self, month):
        if not self.club or self.season > 4 or self.has_flag("contract_terminated") or self.trait == "investor":
            return 0
        if self.payroll_season != self.season:
            self.payroll_season = self.season
            self.payroll_month = 0
        months = max(0, min(12, month) - self.payroll_month)
        if not months:
            return 0
        self.payroll_month += months
        salary = calculate_salary(self.club)
        if self.hold_paycheck:
            self.salary_debt += salary
            self.debt_club = self.club
            self.hold_paycheck = False
            months -= 1
        paid = months * salary
        self.mod("money", paid)
        return paid

    def collect_salary_debt(self):
        amount = self.salary_debt
        self.mod("money", amount)
        self.salary_debt = 0
        self.debt_club = None
        return amount

    def settle_salary(self):
        amount = self.pay_salary_through(12)
        if self.club_bonus_season == self.season or self.has_flag("contract_terminated") or self.trait == "investor":
            return amount
        self.club_bonus_season = self.season
        self.mod("money", self.agent_bonus)
        return amount + self.agent_bonus

    def club_goal_met(self, place, zone):
        if self.club in TOP_CLUBS:
            return place == 1
        if self.club in MID_CLUBS:
            return self.season_wins >= 3
        return zone != "bottom"

    def reward_club_goal(self):
        if self.has_flag("contract_terminated") or not self.season_history or self.objective_bonus_season == self.season:
            return 0
        season = self.season_history[-1]
        if season["season"] != self.season:
            return 0
        goal = season.get("objective_met", False)
        if goal:
            self.objective_bonus_season = self.season
            amount = calculate_salary(self.club)
            self.mod("money", amount)
            return amount
        return 0

    def receive_item(self, item, event, gifted=False):
        if item not in self.inventory:
            self.inventory[item] = {
                "year": 1991 + min(self.season, 4), "month": self.month,
                "place": event.get("subtitle") or self.club, "scene": event["title"],
                "gifted": gifted,
            }

    def reward_honesty(self):
        if self.has_flag("honest_play") and not self.has_flag("honest_bonus"):
            self.set_flag("honest_bonus")
            self.mod("money", 1000)
            return 1000
        return 0

    def reward_match(self, event, score):
        if not score or event["id"] in self.paid_matches or (event.get("national") or event.get("exhibition") or event.get("shootout_95")):
            return 0
        home, away = map(int, score.split(":"))
        club_goals, opponents = (home, away) if self.club == event["home"] else (away, home)
        self.paid_matches.append(event["id"])
        if club_goals <= opponents:
            return 0
        if not event.get("european") and not event.get("cup"):
            self.season_wins += 1
        amount = BENFICA_WIN_BONUS if self.club == "Бенфика" else {1200: 500, 500: 350, 200: 200}[calculate_salary(self.club)]
        self.mod("money", amount)
        return amount

    def add_team_mod(self, val):
        self.team_modifiers.append(int(val))

    def set_flag(self, key, val=True):
        self.flags[key] = bool(val)
        if key == "ptsd":
            self.ptsd = bool(val)
        elif key == "injury_severe":
            self.injury_severe = bool(val)

    def has_flag(self, key):
        if key == "ptsd":
            return self.ptsd
        if key == "injury_severe":
            return self.injury_severe
        return self.flags.get(key, False)

    def skill_margin(self, attr, threshold, important=False, *, away=None, endurance=False):
        attr = SKILL_ALIASES.get(attr, attr)
        threshold = int(threshold) - (0 if self.mode_realism else 10)
        value = self.hidden_attrs.get(attr, self.attrs.get(attr, 0))
        if important:
            if attr in ("tec", "phy", "vis", "com"):
                value -= 3 * (self.attrs["rep_coach"] < 40)
            value -= 10 * (self.hidden_attrs["consistency"] < 40)
            value += 10 * (self.hidden_attrs["clutch"] > 60)
            if attr == "com":
                value -= 15 * self.ptsd + 5 * (self.trait == "joker")
        if attr in ("tec", "phy", "vis", "com"):
            value -= 5 * (self.attrs["rel_coach"] < -30)
        if attr in ("vis", "tec") and self.snitch_matches:
            value -= 8
        if attr == "vis" and self.attrs["rep_teammates"] < 30:
            value -= 8
        if attr == "com":
            value -= max(0, self.stress - 60) // 8
        if attr == "com" and self.attrs["rel_rival"] < -30:
            value -= 5
        if attr == "com" and self.trait == "homesick" and away is not None:
            value += -10 if away else 5
        if attr == "phy":
            value -= self.fatigue // 3
            if endurance and self.trait == "cheburek_fan":
                value -= 8
        return value - max(1, min(100, threshold))

    def check_skill(self, attr, threshold, important=False, **context):
        return self.skill_margin(attr, threshold, important, **context) >= 0

    def check(self, attr, threshold, important=False, **context):
        return self.check_skill(attr, threshold, important, **context)

    def check_any(self, attrs_str, threshold, important=False, **context):
        return any(self.check(attr.strip(), threshold, important, **context)
                   for attr in attrs_str.split("|"))

    def add_stress(self, amount, party=False, conflict=False):
        amount = int(amount)
        if party and ((amount > 0 and self.trait == "workhorse")
                      or (amount < 0 and self.trait == "partygoer")):
            amount *= 2
        if conflict and amount > 0:
            if self.trait == "leader":
                amount *= 2
            if self.attrs["rel_captain"] > 30 or self.attrs["rep_teammates"] > 70:
                amount = max(0, amount - 6)
            elif self.attrs["rel_captain"] < -30:
                amount += 6
        self.pressure_count += int(amount > 0)
        self.stress = max(0, min(100, self.stress + amount))
        if self.stress < 85:
            self.stress_warning = False

    def settle_pressure(self, before, warned, pressure_count):
        if self.pressure_count == pressure_count or self.stress < before:
            return
        cap = 23 if self.mode_realism else 16
        self.stress = min(self.stress, before + cap)
        if self.stress < 85:
            return
        self.stress_warning = True
        if warned and self.stress == 100 and self.stress >= before:
            self.do_breakdown()

    def do_breakdown(self):
        if self.stress < 100 or self.breakdowns >= 3:
            return False
        self.breakdowns += 1
        self.stress = 40
        self.stress_warning = False
        self.breakdown_pending = True
        if self.breakdowns >= 2:
            self.set_flag("ptsd")
        if self.breakdowns < 3:
            self.apply_breakdown_consequence()
        return True

    def apply_breakdown_consequence(self):
        incident = career_random().randrange(3)
        self.breakdown_incident = incident
        if incident == 0:
            self.injure(1)
            self.mod("phy", -8)
        elif incident == 1:
            self.mod("rep_press", -20)
            self.counters["scandals_moderate"] += 1
            self.discipline("scandal")
        else:
            self.mod("rep_teammates", -15)
            self.mod("rep_coach", -10)
            self.suspension_matches = max(self.suspension_matches, 2)
            self.discipline("fight")

    def get_base_strength(self, clubs_data):
        base = 8
        if clubs_data.get(self.nation):
            for league_key in ["first", "second"]:
                for club in clubs_data[self.nation].get(league_key, []):
                    if club["name"] == self.club:
                        base = club["base"]
        return base

    def update_place(self, clubs_data):
        teams = league_teams(self, clubs_data)
        base = next(team["base"] for team in teams if team["name"] == self.club) if self.season == 4 else self.get_base_strength(clubs_data)
        total = sum(self.team_modifiers)
        num_teams = len(teams)
        estimate = 1 + (base - 1) * (num_teams - 1) / 7 if self.league == "first" else base - 8
        raw_place = round(estimate - total / 2.0)
        self.current_place = max(1, min(num_teams, raw_place))
        return self.current_place

    def reset_season_modifiers(self):
        self.team_modifiers = []
        self.match_scores = {}
        self.paid_matches = []
        self.season_wins = 0
        self.season_fixture_scores = {}

    def pick_illustration(self, art):
        if isinstance(art, str):
            return art
        key = tuple(art)
        available = [image for image in art if image != self.art_last.get(key)]
        selected = career_random().choice(available or art)
        self.art_last[key] = selected
        return selected

    def record_match(self, event, choice=None, branch=None, effects=None):
        if event.get("shootout_95"):
            result = (effects or {}).get("shootout_result")
            player_won = self.club == event["home"] if result is None else result == "win"
            home_won = player_won == (self.club == event["home"])
            self.set_flag("trophy_95", player_won)
            if player_won:
                self.award_title("cup")
            return "0:0 · пенальти " + ("8:7" if home_won else "7:8")
        baseline = event.get("historical_score") if choice is None else None
        baseline = baseline or event.get("game_score") or event.get("historical_score")
        if baseline is None:
            return ""
        outcomes = (choice or {}).get("scores", {})
        score = outcomes.get(branch, baseline)
        if branch in outcomes and event.get("reverse_player_score") and self.club == event["away"]:
            score = ":".join(reversed(score.split(":")))
        goals = list(map(int, score.split(":")))
        change = (effects or {}).get("score_change", {})
        player_side = int(self.club == event["away"])
        goals[player_side] = max(0, goals[player_side] + change.get("for", 0))
        goals[1 - player_side] = max(0, goals[1 - player_side] + change.get("against", 0))
        if self.season == 3:
            self.set_flag("away_loss", player_side == 1 and goals[1] < goals[0])
        if not (event.get("european") or event.get("exhibition") or event.get("cup")):
            self.match_scores[(event["home"], event["away"])] = tuple(goals)
        return "{}:{}".format(*goals)

    def award_title(self, kind):
        if kind == "league":
            self.titles_league += 1
        elif kind == "gold":
            self.titles_gold += 1
        elif kind == "cup":
            self.titles_cup += 1
        elif kind == "lc":
            self.titles_lc += 1
        elif kind == "national":
            self.national_titles += 1

    def award_league_place(self, place):
        place = int(place)
        if place <= 3:
            self.award_title("league")
        if place == 1:
            self.award_title("gold")

    def infamy(self):
        return self.counters["scandals_severe"] * 3 + self.counters["scandals_moderate"]

    def glory(self):
        return (self.titles_gold * 4 + self.titles_league * 2
                + self.titles_cup + self.titles_lc * 3
                + self.national_titles * 4)


def apply_effects(gs, effects):
    if not effects:
        return
    if "mode_realism" in effects:
        gs.mode_realism = effects["mode_realism"]
        gs.set_flag("mode_realism", gs.mode_realism)
    gs.goals += effects.get("goals", 0)
    gs.next_match_phy += effects.get("next_match_phy", 0)
    if "trait" in effects:
        gs.set_trait(effects["trait"])
    if "training" in effects:
        gs.train(effects["training"], effects.get("fatigue", 0))
    if "fatigue" in effects and "training" not in effects:
        gs.fatigue = max(0, gs.fatigue + effects["fatigue"])
    if "training_time" in effects:
        gs.use_training_time(effects["training_time"])
    if "recovery_months" in effects:
        gs.recover(effects["recovery_months"])
    for key, value in effects.get("attrs", {}).items():
        gs.mod(key, value)
    for key, value in effects.get("hidden_attrs", {}).items():
        gs.mod(key, value)
    for key, value in effects.get("flags", {}).items():
        gs.set_flag(key, value)
    if "team_modifier" in effects:
        gs.add_team_mod(effects["team_modifier"])
    for key, value in effects.get("counters", {}).items():
        gs.counters[key] = gs.counters.get(key, 0) + int(value)
    if "award" in effects:
        gs.award_title(effects["award"])
    if "injury_months" in effects:
        gs.injure(effects["injury_months"])
    if "suspension_matches" in effects:
        duration = min(2, effects["suspension_matches"])
        gs.suspension_matches = max(gs.suspension_matches, duration)
    if "transfer" in effects:
        gs.transfer(effects["transfer"])
    if "foreign_transfer" in effects:
        gs.transfer(effects["foreign_transfer"], "portugal")
    if "wallet_percent" in effects:
        gs.mod("money", max(0, gs.attrs["money"]) * effects["wallet_percent"] // 100)
    if "discipline" in effects:
        gs.discipline(effects["discipline"])
    if "debt" in effects:
        gs.fixing_amount += effects["debt"]
    if effects.get("restitution"):
        gs.mod("money", -gs.fixing_amount)
    if effects.get("restitution") or effects.get("clear_debt"):
        gs.fixing_amount = 0
    if effects.get("honesty_reward"):
        gs.reward_honesty()
    if "family_support" in effects:
        gs.family_support += effects["family_support"]
    if "relationship" in effects:
        gs.relationship = max(-3, min(6, gs.relationship + effects["relationship"]))
    if effects.get("coach_review"):
        gs.coach_review_due = True
    if effects.get("restore_squad"):
        gs.restore_squad()
    if effects.get("exile_transfer") and gs.transfer_offer:
        gs.transfer(gs.transfer_offer, gs.league)
        gs.mod_rep("rep_coach", max(0, 45 - gs.attrs["rep_coach"]))
        gs.restore_squad()
        gs.transfer_offer = None
    if effects.get("suspicion_chance") and career_random().randrange(100) < effects["suspicion_chance"]:
        gs.suspicion += 1
    if effects.get("doping_ban"):
        gs.ban_months = 24
        gs.set_flag("contract_terminated")
        gs.set_flag("european_ban")
        gs.set_flag("doping_risk", False)
    if "snitch_matches" in effects:
        gs.snitch_matches = effects["snitch_matches"]
    for key in ("transition_result", "referee_result"):
        if key in effects:
            gs.playoff_results[key] = tuple(map(int, effects[key].split(":")))
    if effects.get("national_call"):
        gs.national_calls += 1
        gs.set_flag("senior_call")
    if effects.get("captain"):
        gs.captain = True
    if effects.get("agent_deal"):
        if gs.attrs["rel_agent"] > 30:
            gs.agent_bonus = 600
        elif gs.attrs["rel_agent"] < -30:
            gs.mod_rep("rep_press", -15)
            gs.counters["scandals_moderate"] += 1
    if "stress" in effects:
        stress = effects.get("workhorse_stress", effects["stress"]) if gs.trait == "workhorse" else effects["stress"]
        if effects.get("party") and gs.trait == "workhorse" and stress < 0:
            stress = 15
        if effects.get("resort") and gs.trait == "cheburek_fan":
            stress -= 10
        gs.add_stress(stress, party=effects.get("party"), conflict=effects.get("conflict"))
    if effects.get("meal") and gs.trait == "cheburek_fan":
        gs.add_stress(-5)
        gs.mod("phy", 1)
    if effects.get("important_match") and gs.trait == "ice_cold":
        gs.add_stress(-3)


def resolve_choice(gs, choice, event=None):
    event = event or {}
    if "check" in choice:
        chk = choice["check"]
        attr = chk["attr"]
        threshold = chk["threshold"]
        important = bool(chk.get("important", False) or choice.get("important", False) or event.get("important", False))
        away = chk.get("away")
        if away is None and event.get("home"):
            away = gs.club != event["home"] and event["id"] != "MATCH_DERBY"
        pressure = max(0, gs.stress - 50) // 10 if "partial" in choice else 0
        margin = max(
            gs.skill_margin(skill, threshold, important, away=away, endurance=chk.get("endurance", False))
            + (gs.match_phy_modifier if skill == "phy" else 0)
            for skill in (part.strip() for part in attr.split("|"))
        ) - pressure
        if choice.get("equipment") in gs.inventory and not gs.inventory[choice["equipment"]]["gifted"]:
            margin += 2
        supports_partial = "partial" in choice
        success_margin = (3 if gs.mode_realism else 7) if supports_partial else 0
        ok = margin >= success_margin
        ok = ok and all(gs.check_skill(extra["attr"], extra["threshold"], important, away=away)
                        for extra in choice.get("extra_checks", ()))
        rng = career_random()
        partial = False
        if not ok and supports_partial:
            partial = margin >= (-7 if gs.mode_realism else -10)
        if not ok and not partial and gs.trait == "lucky":
            ok = rng.randrange(100) < 20
        branch = "success" if ok else "partial" if partial else "fail"
        effects = choice.get(branch, {})
        if branch == "fail" and choice.get("referee") and (gs.trait == "scandalist" or gs.hidden_attrs["temperament"] > 70):
            branch = "strike"
            effects = choice[branch]
        if branch == "fail" and choice.get("play_hurt"):
            injury_risk = gs.hidden_attrs["injury_prone"]
            if gs.trait == "glass" or rng.randrange(100) < min(100, injury_risk + 30 * (injury_risk > 60)):
                effects = {**effects, "injury_months": 3}
        if choice.get("provocation") and gs.trait == "trash_talker":
            effects = choice["trash_talker_" + branch]
        apply_event_effects(gs, effects, event)
        return branch, effects
    effects = choice.get("effects", {})
    apply_event_effects(gs, effects, event)
    return "flat", effects


def apply_event_effects(gs, effects, event):
    public = ("rep_fans", "rep_press", "media")
    before = {key: gs.attrs[key] for key in public}
    stress_before, warned, pressure_count = gs.stress, gs.stress_warning, gs.pressure_count
    if event.get("scandal") and gs.attrs["rel_coach"] > 50:
        attrs = dict(effects.get("attrs", {}))
        for reputation in ("rep_coach", "rep_press"):
            if attrs.get(reputation, 0) < 0:
                attrs[reputation] = min(0, attrs[reputation] + 5)
        effects = {**effects, "attrs": attrs}
        if effects.get("stress", 0) > 0:
            effects["stress"] = max(0, effects["stress"] - 5)
    media_delta = effects.get("attrs", {}).get("media", 0)
    if media_delta > 0:
        high_profile = event.get("european") or event.get("national") or event.get("scandal")
        divisor = 1 if high_profile or gs.attrs["media"] < 55 else 2 if gs.attrs["media"] < 80 else 3
        effects = {**effects, "attrs": {**effects["attrs"], "media": max(1, media_delta // divisor)}}
    if event.get("home") and gs.attrs["rep_coach"] >= 70 and effects.get("stress", 0) > 0:
        effects = {**effects, "stress": max(0, effects["stress"] - 4)}
    apply_effects(gs, effects)
    if effects.get("item"):
        gs.receive_item(effects["item"], event)
    if effects.get("gift_item") in gs.inventory:
        gs.inventory[effects["gift_item"]] = {**gs.inventory[effects["gift_item"]], "gifted": True}
    if effects.get("personal_training"):
        gs.personal_training = True
        gs.train(MATCH_SKILLS[gs.position], fatigue=2)
    if effects.get("salary_debt"):
        gs.collect_salary_debt()
    if effects.get("romance_scandal") and gs.rumor_score < 0:
        gs.add_stress(15)
        gs.mod_rep("rep_fans", -10)
        gs.set_flag("romance_scandal")
    if event.get("family"):
        relation = gs.attrs["rel_family"]
        gs.add_stress(-5 if relation > 50 else 8 if relation < 20 else 0)
    if event.get("press"):
        relation = gs.attrs["rel_journalist"]
        if relation > 30:
            gs.mod_rep("rep_press", 5)
        elif relation < -30:
            gs.mod_rep("rep_press", -5)
            gs.add_stress(5)
    changes = [gs.attrs[key] - before[key] for key in public]
    inferred = min(changes, key=lambda delta: (-abs(delta), delta))
    delta = effects.get("rumor", inferred if abs(inferred) >= 10 else 0)
    gs.register_press(delta)
    if event.get("home") and effects.get("stress", 0) > 0 and gs.has_flag("father_support"):
        gs.add_stress(-3)
        gs.set_flag("father_support", False)
    gs.settle_pressure(stress_before, warned, pressure_count)
    if event.get("id") == "TALK_WITH_COACH":
        gs.close_crisis_talk()
    if event.get("id") == "SQUAD_EXILE_RESOLVE" and gs.has_flag("squad_exile"):
        gs.exile_discussed = True


def bind_event(gs, event, clubs_data):
    if not event:
        return None
    if event["id"] == "S4_TRANSFER_EUROPE":
        terms = {"salary": format(BENFICA_SALARY, ",").replace(",", " "),
                 "win_bonus": format(BENFICA_WIN_BONUS, ",").replace(",", " ")}
        text = [[who, line.format_map(terms), *rest] for who, line, *rest in event["text"]]
        if gs.trait == "investor":
            text.append([None, "В этой карьере вместо обычного оклада действуют доходы от ваучеров. Премии за победу начисляются по условиям договора."])
        event = {**event, "text": text}
    if event["id"] == "SQUAD_EXILE_RESOLVE" and gs.coach_review_due:
        return None
    if str(gs.season) in event.get("season_text", {}):
        event = {**event, "text": normalize_text(event["season_text"][str(gs.season)])}
    if gs.position == "GK" and event["id"] in ("S1_C1", "S1_C7", "S1_E1"):
        revised = []
        for choice in event["choices"]:
            choice = dict(choice)
            if choice.get("sketch", {}).get("success") == "goal":
                choice["conclusion"] = {**choice["conclusion"], "success":
                    "Ты сохраняешь самообладание и отражаешь удар в ближний угол. Тренер кивает."}
                choice["sketch"] = {**choice["sketch"], "success": "save"}
                choice["success"] = {key: value for key, value in choice["success"].items() if key != "goals"}
            revised.append(choice)
        event = {**event, "choices": revised}
    if event.get("league_fixture") and gs.season == 3:
        teams = {row["name"] for row in league_teams(gs, clubs_data)}
        expected = event.get("fixture_league", "first")
        if gs.league != expected or not {event["home"], event["away"]} <= teams:
            if not event["id"].startswith("NEW_"):
                return None
            return {**event, "exhibition": True, "historical_note":
                    event["historical_note"] + " В этой карьере встреча проходит как контрольная."}
    opponent = event.get("fixture_opponent")
    if opponent:
        if gs.position != "GK" or gs.club == opponent or gs.league != "first" or opponent not in gs.first_1993:
            return None
        # Use the away fixture, leaving the dated home fixtures intact.
        return {**event, "home": opponent, "away": gs.club}
    if event["id"] == "S1_HOME_FAMILY" and gs.family_support:
        detail = ("Мама достаёт квитанцию за отопление и говорит, что перевод пришёл до срока."
                  if gs.has_flag("family_heating") else "Мама ставит на стол продукты, которые купила на оставленные тобой деньги.")
        event = {**event, "text": [*event["text"], [None, detail]]}
    if event["id"] == "CIS_PROJECT_REPLY":
        response = ("Запрашивая смету весной, ты надеялся найти короткий маршрут. На карте остались те же две станции."
                    if gs.has_flag("cis_project_backed") else "Организатор вспоминает твоё предупреждение о календаре и показывает два совпавших тура.")
        event = {**event, "text": [[None, response], *event["text"]]}
    if event["id"] == "HOME_DATE" and gs.relationship:
        reunion = ("У кассы Лена спрашивает, успеете ли вы снова увидеться до сборов."
                   if gs.relationship > 0 else "У кассы Лена просит сказать прямо, стоит ли ей ждать после сборов.")
        event = {**event, "text": [*event["text"], ["Лена", reunion]]}
    if event["id"] == "SQUAD_EXILE_TRANSFER" and gs.transfer_offer:
        return {**event, "subtitle": gs.transfer_offer}
    return event


def _requirements_met(gs, requirements):
    for key, value in requirements.items():
        if key == "position":
            allowed = value if isinstance(value, list) else [value]
            if gs.position not in allowed:
                return False
        elif key in ("club", "opponent", "month", "trait", "league", "zone_1993"):
            allowed = value if isinstance(value, list) else [value]
            if getattr(gs, key) not in allowed:
                return False
        elif key == "not_club":
            if gs.club in value:
                return False
        elif key == "goalless_min":
            if gs.goalless_matches < value:
                return False
        elif key == "owns":
            if (value not in gs.inventory or gs.inventory[value]["gifted"]):
                return False
        elif key == "new_item":
            if value in gs.inventory:
                return False
        elif key == "relationship_min":
            if gs.relationship < value:
                return False
        elif key == "relationship_max":
            if gs.relationship > value:
                return False
        elif key == "club_treatment":
            if gs.has_flag("contract_terminated"):
                return False
        elif key == "personal_training":
            if gs.personal_training != value:
                return False
        elif key == "salary_debt":
            if gs.salary_debt <= 0:
                return False
        elif key == "flags":
            for flag, expected in value.items():
                if gs.has_flag(flag) != bool(expected):
                    return False
        elif key == "europe_status":
            if not (gs.has_flag("european_ban") or gs.attrs["media"] > 50):
                return False
        elif key == "rumor_max":
            if gs.rumor_score > value:
                return False
        elif key == "suspicion_min":
            if gs.suspicion < value:
                return False
        elif key == "temperament_min":
            if gs.hidden_attrs["temperament"] < value:
                return False
        elif key.endswith("_max"):
            if gs.attrs[key.removesuffix("_max")] > value:
                return False
        elif key == "sponsor":
            if not (gs.attrs["media"] > 50 or gs.attrs["rep_fans"] > 60):
                return False
        elif key == "money" or key.endswith("_min"):
            attr = key.removesuffix("_min")
            if gs.attrs[attr] < value:
                return False
        elif key == "flag":
            if not gs.has_flag(str(value)):
                return False
        else:
            try:
                if not gs.check(key, int(value)):
                    return False
            except (TypeError, ValueError):
                return False
    return True


def is_choice_relevant(gs, choice):
    requirements = choice.get("requires", {})
    return _requirements_met(gs, {key: requirements[key] for key in ("club", "position") if key in requirements})


def is_choice_available(gs, choice):
    return _requirements_met(gs, choice.get("requires", {}))


def is_event_available(gs, event):
    return _requirements_met(gs, event.get("requires", {}))


def match_choices_95(choices, position, state, round_index):
    # Keep the action and illustration consistent. The score changes what a
    # successful action means and which way of playing is useful.
    successful = {
        "FWD": ("Ты бьёшь низом, пока вратарь переносит вес. Мяч остаётся в сетке.",
                "Ты бьёшь первым касанием. Вратарь опаздывает, и сетка вздрагивает."),
        "MID": ("Твой пас проходит за спины защитников. Партнёр принимает мяч и попадает в дальний угол.",
                "Ты оставляешь мяч партнёру в свободном коридоре. Он бьёт в касание и забивает."),
        "GK": ("Ты успеваешь сместиться и забираешь мяч обеими перчатками.",
               "Ты накрываешь мяч у стойки. Нападающий уже готовился к добиванию."),
        "DEF": ("Ты встречаешь подачу раньше соперника и выбиваешь мяч подальше от ворот.",
                "Ты успеваешь развернуться и выносишь мяч из штрафной. Партнёры поднимают линию.")
    }
    lead = {
        "FWD": "Ваше преимущество растёт.", "MID": "Ваше преимущество растёт.",
        "GK": "Вы сохраняете преимущество.", "DEF": "Вы сохраняете преимущество.",
    }
    chase = {
        "FWD": "Вы сравниваете счёт.", "MID": "Вы сравниваете счёт.",
        "GK": "У команды ещё есть время отыграться.", "DEF": "У команды ещё есть время отыграться.",
    }
    first = choices[0]
    ending = lead[position] if state == "hold" else chase[position] if state == "chase" else ""
    revised = {**first, "conclusion": {**first["conclusion"],
               "success": " ".join(filter(None, (successful[position][round_index % 2], ending)))}}
    if state != "level":
        revised["check"] = {**first["check"], "important": True,
                            "threshold": first["check"]["threshold"] + (4 if state == "chase" else 2)}
    return [revised, *choices[1:]]


def press_topic(event, effects, score):
    if effects.get("debt") or effects.get("counters", {}).get("red_cards") or event.get("scandal"):
        return "scandal"
    if score or event.get("match"):
        return "match"
    if event.get("press") or event.get("press_followup"):
        return "interview"
    return "club"


def check_hint(choice, gs=None, event=None):
    check = choice.get("check")
    if not check:
        return ""
    attr = str(check.get("attr", "")).split("|")[0].strip()
    hint = CHECK_HINTS.get(attr, "Ты собираешься с мыслями перед решающим действием.")
    if gs is None:
        return hint
    penalties = []
    if attr in ("phy", "agility", "stamina") and gs.fatigue >= 3:
        penalties.append("усталость")
    if "partial" in choice and gs.stress >= 60:
        penalties.append("напряжение")
    if attr in ("com", "composure") and gs.ptsd and (event or {}).get("important"):
        penalties.append("стресс после травмы")
    if penalties:
        hint += " Сейчас мешает: " + ", ".join(penalties) + "."
    equipment = choice.get("equipment")
    if equipment in gs.inventory and not gs.inventory[equipment]["gifted"]:
        hint += " Помогает экипировка."
    return hint


def choice_outcome(choice, branch, trait=None):
    if trait == "trash_talker":
        explicit = choice.get("outcome_trash_" + branch)
        if explicit:
            return explicit
    conclusion = choice.get("conclusion")
    explicit = conclusion.get(branch) if isinstance(conclusion, dict) else conclusion
    explicit = explicit or choice.get("outcome_" + branch)
    if explicit:
        return explicit
    if branch == "success":
        return "Тебе удалось справиться с эпизодом. Команда замечает твой вклад."
    if branch == "fail":
        return "Эпизод складывается не так, как хотелось. Последствия уже отражены в твоём состоянии."
    return choice.get("outcome_flat", choice.get("outcome", ""))


def choice_sketch(choice, branch, trait=None, effects=None):
    drawings = choice.get("sketch", {})
    if (effects or {}).get("injury_months") and not choice.get("scene_art"):
        return "injury"
    if trait == "trash_talker":
        variant = drawings.get("trash_" + branch)
        if variant:
            return variant
    return drawings.get(branch, "talk")


def club_start_stress(clubs_data, nation, league, club_name, fallback=0):
    for club in clubs_data.get(nation, {}).get(league, []):
        if club.get("name") == club_name:
            return max(0, min(99, int(club.get("start_stress", fallback))))
    return max(0, min(99, int(fallback)))


def load_json(path):
    with renpy.loader.load(path) as source:
        return json.load(source)


def normalize_text(text_list):
    result = []
    for item in text_list:
        if isinstance(item, str):
            result.append([None, item])
        elif isinstance(item, dict):
            result.append([item.get("speaker"), item.get("text", ""), item.get("emotion", "neutral")])
        else:
            result.append([None, str(item)])
    return result


def load_events():
    events = {}
    season = load_json("events/events.json")
    update = load_json("events/career_update.json")
    expansion = load_json("events/season_1995.json")
    review_events = load_json("events/career_review.json")
    history = load_json("data/history_1992.json")
    archive = {event["id"]: event for event in history["events"] + history["matches"]}
    for event in season["events"] + [archive[eid] for eid in season["history_ids"]] + update + expansion + review_events:
        event.setdefault("type", "🏛" if event.get("source") else "🎭")
        event["text"] = normalize_text(event.get("text", []))
        events[event["id"]] = event
    return events


def load_clubs():
    return load_json("data/clubs.json")


def teams_1993(gs, clubs_data, league, zone=None):
    data = clubs_data["season_1993"]
    first = gs.first_1993 or data["first"]
    if league == "first":
        return [{"name": name, "base": 1 + index * 7 / 17} for index, name in enumerate(first)]
    names = [name for name in data["zones"][zone] if name not in first]
    extras = [name for name in data["first"] if name not in first and
              data["extra_zones"].get(name, "Центр") == zone and name not in names]
    names = extras + names
    if gs.league == "second" and gs.zone_1993 == zone and gs.club not in names:
        names.append(gs.club)
    return [{"name": name, "base": 8 + 13 * index / max(1, len(names) - 1)} for index, name in enumerate(names)]


def league_teams(gs, clubs_data):
    if gs.season == 4:
        names = list(clubs_data["season_1995"][gs.league])
        if gs.club not in names:
            names[-1] = gs.club
        start, spread = (8, 13) if gs.league == "second" else (1, 7)
        return [{"name": name, "base": start + spread * index / (len(names) - 1)}
                for index, name in enumerate(names)]
    if gs.season >= 3 and gs.league == "first":
        names = list(gs.first_1994 or clubs_data["season_1994"]["first"])
        if gs.club not in names:
            names[-1] = gs.club
        ranking = clubs_data["season_1994"]["first"]
        return [{"name": name, "base": 1 + 7 * (ranking.index(name) if name in ranking else 15) / 15}
                for name in names]
    if gs.season >= 3 and gs.league == "second":
        first = gs.first_1994 or clubs_data["season_1994"]["first"]
        archive = clubs_data["season_1994"]
        names = [name for name in archive["second"] if name not in first]
        relegated = [name for name in gs.first_1993 if name not in first and name not in names]
        names = (names + relegated)[:22]
        if gs.club not in names:
            names[-1] = gs.club
        return [{"name": name, "base": 8 + 13 * index / max(1, len(names) - 1)}
                for index, name in enumerate(names)]
    if gs.season == 2 and gs.first_1993:
        return teams_1993(gs, clubs_data, gs.league, gs.zone_1993)
    leagues = clubs_data[gs.nation]
    teams = list(leagues[gs.league])
    if not any(team["name"] == gs.club for team in teams):
        other = "second" if gs.league == "first" else "first"
        player = next(team for team in leagues[other] if team["name"] == gs.club)
        teams.append(player)
    return teams


def _standings(teams, fixtures, gs, performance, scores, strength_scale=None):
    rows = {team["name"]: dict(name=team["name"], played=0, w=0, d=0, l=0,
                             gf=0, ga=0, pts=0, gd=0) for team in teams}
    rng = career_random()
    scale = strength_scale or (2.6 if gs.league == "first" else 7)
    for home, away in fixtures:
        key = (home["name"], away["name"])
        if key not in scores:
            strength = (away["base"] - home["base"]) / scale
            strength += performance * ((home["name"] == gs.club) - (away["name"] == gs.club))
            home_goals = max(0, min(7, round(rng.uniform(-1, 3) + strength + 0.3)))
            away_goals = max(0, min(7, round(rng.uniform(-1, 3) - strength)))
            scores[key] = home_goals, away_goals
        home_goals, away_goals = scores[key]
        for team, scored, conceded in ((home, home_goals, away_goals), (away, away_goals, home_goals)):
            row = rows[team["name"]]
            row["played"] += 1
            row["gf"] += scored
            row["ga"] += conceded
            row["gd"] += scored - conceded
            row["w" if scored > conceded else "d" if scored == conceded else "l"] += 1
            row["pts"] = (3 if gs.season >= 4 else 2) * row["w"] + row["d"]
    return sorted(rows.values(), key=lambda row: (row["pts"], row["w"], row["gd"], row["gf"]), reverse=True)


def generate_table(gs, clubs_data, league_key, place=None, scores=None):
    teams = league_teams(gs, clubs_data)
    performance = sum(gs.team_modifiers) / 8
    if gs.season >= 2:
        performance = max(-1.8, min(1.8, performance))
    if scores is None:
        scores = dict(gs.season_fixture_scores) if gs.season in (3, 4) else {}
        scores.update(gs.match_scores)
    fixtures = [(home, away) for home in teams for away in teams if home != away]
    if gs.season == 1 and league_key == "first":
        opening = [fixture for fixture in fixtures if fixture[0]["group"] == fixture[1]["group"]]
        qualifiers = set()
        for group in ("A", "B"):
            members = [team for team in teams if team["group"] == group]
            games = [fixture for fixture in opening if fixture[0]["group"] == group]
            qualifiers.update(row["name"] for row in _standings(members, games, gs, performance, scores)[:4])
        rows = []
        for qualified in (True, False):
            members = [team for team in teams if (team["name"] in qualifiers) == qualified]
            games = [(home, away) for home, away in fixtures if home in members and away in members]
            rows.extend(_standings(members, games, gs, performance, scores))
    else:
        rows = _standings(teams, fixtures, gs, performance, scores)
        if gs.season in (3, 4):
            gs.season_fixture_scores = scores
    relegation_places = {3: 5, 4: 3}.get(gs.season, 0) if league_key == "second" else 0
    if league_key == "first":
        relegation_places = {1: 5, 4: 1}.get(gs.season, 2)
    top_places = {2: 1, 3: 2}.get(gs.season, 3) if league_key == "second" else 3
    for index, row in enumerate(rows):
        row["place"] = index + 1
        row["zone"] = ("top" if index < top_places else
                       "bottom" if index >= len(rows) - relegation_places else "mid")
        if gs.season == 2 and league_key == "first" and 14 <= row["place"] <= 16:
            row["zone"] = "playoff"
    return rows



def upper_table_1993(gs, clubs_data, regular_table):
    if gs.league == "first":
        return regular_table
    first = teams_1993(gs, clubs_data, "first")
    fixtures = [(home, away) for home in first for away in first if home != away]
    return _standings(first, fixtures, gs, 0, {}, strength_scale=2.6)


def transition_teams(gs, clubs_data, regular_table, upper=None):
    if upper is None:
        upper = upper_table_1993(gs, clubs_data, regular_table)
    eligible = [row["name"] for row in upper[13:16]]
    for zone in clubs_data["season_1993"]["zones"]:
        if gs.league == "second" and zone == gs.zone_1993:
            eligible.append(regular_table[0]["name"])
            continue
        members = teams_1993(gs, clubs_data, "second", zone)
        fixtures = [(home, away) for home in members for away in members if home != away]
        eligible.append(_standings(members, fixtures, gs, 0, {}, strength_scale=7)[0]["name"])
    return eligible


def generate_transition(gs, clubs_data, qualified):
    catalog = {team["name"]: team for team in teams_1993(gs, clubs_data, "first")}
    for zone in clubs_data["season_1993"]["zones"]:
        catalog.update((team["name"], team) for team in teams_1993(gs, clubs_data, "second", zone))
    teams = [{"name": name, "base": min(9, catalog[name]["base"])} for name in qualified]
    fixtures = [(home, away) for index, home in enumerate(teams) for away in teams[index + 1:]]
    player_games = [(home["name"], away["name"]) for home, away in fixtures
                    if gs.club in (home["name"], away["name"])]
    scores = {}
    for game, action in zip(player_games[-2:], ("transition_result", "referee_result")):
        if action in gs.playoff_results:
            score = gs.playoff_results[action]
            scores[game] = score if game[0] == gs.club else score[::-1]
    locked = set(scores)
    rows = _standings(teams, fixtures, gs, 0, scores, strength_scale=3.8)
    referee = gs.playoff_results.get("referee_result")
    transition = gs.playoff_results.get("transition_result")
    # The written decisive branches determine survival. Adjust only simulated,
    # unplayed fixtures if the initial standings contradict that consequence.
    desired = None
    if referee:
        desired = referee[0] > referee[1]
    elif transition and transition[0] < transition[1]:
        desired = False
    qualifies = any(row["name"] == gs.club for row in rows[:3])
    if player_games and desired is not None and desired != qualifies:
        score = (1, 0) if desired else (0, 1)
        for game in player_games:
            if game not in locked:
                scores[game] = score if game[0] == gs.club else score[::-1]
        rows = _standings(teams, fixtures, gs, 0, scores, strength_scale=3.8)
    for index, row in enumerate(rows, 1):
        row["place"] = index
        row["zone"] = "top" if index <= 3 else "bottom"
    return rows
