import json
import random
import renpy


TRAIT_LABELS = {
    "workhorse": "Трудяга",
    "scandalist": "Скандалист",
    "cheburek_fan": "Любитель чебуреков",
    "ice_cold": "Хладнокровный",
}

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

        self.stress = 0
        self.start_stress = 0
        self.breakdowns = 0
        self.breakdown_pending = False
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
        self.national_calls = 0
        self.clubs_played = 1

    def set_trait(self, trait):
        self.trait = trait if trait in TRAIT_LABELS else "cheburek_fan"
        if self.trait == "workhorse":
            self.mod("phy", 10)
        elif self.trait == "scandalist":
            self.mod("aggression", 5)
            self.mod("media", 5)
        elif self.trait == "cheburek_fan":
            self.mod("com", 5)
        elif self.trait == "ice_cold":
            self.mod("com", 5)
            self.mod("clutch", 5)

    def mod(self, key, val):
        val = int(val)
        if key in self.hidden_attrs:
            self.hidden_attrs[key] = max(1, min(100, self.hidden_attrs.get(key, 50) + val))
            self.attrs[key] = self.hidden_attrs[key]
            return
        if key == "money":
            self.attrs[key] = self.attrs.get(key, 0) + val
        elif key in self.attrs:
            self.attrs[key] = max(1, min(100, self.attrs.get(key, 50) + val))

    def add_team_mod(self, val):
        self.team_modifiers.append(int(val))

    def set_flag(self, key, val=True):
        self.flags[key] = bool(val)
        if key == "ptsd":
            self.ptsd = bool(val)

    def has_flag(self, key):
        if key == "ptsd":
            return self.ptsd
        return self.flags.get(key, False)

    def effective_threshold(self, threshold, important=False):
        threshold = int(threshold)
        if not self.mode_realism:
            threshold -= 10
        if important and self.ptsd:
            threshold += 15
        return max(1, min(100, threshold))

    def check(self, attr, threshold, important=False):
        threshold = self.effective_threshold(threshold, important)
        value = self.hidden_attrs.get(attr, self.attrs.get(attr, 0))
        if important:
            # clutch слегка помогает именно в решающие минуты; PTSD повышает порог.
            value += round((self.hidden_attrs.get("clutch", 50) - 50) / 5.0)
        return value >= threshold

    def check_any(self, attrs_str, threshold, important=False):
        return any(self.check(a.strip(), threshold, important)
                   for a in attrs_str.split("|"))

    def add_stress(self, amount, party=False):
        amount = int(amount)
        if party and amount > 0 and self.trait == "workhorse":
            amount *= 2
        self.stress = max(0, min(100, self.stress + amount))
        if self.stress >= 100:
            self.do_breakdown()

    def do_breakdown(self):
        if self.stress < 100:
            return False
        self.breakdowns += 1
        self.stress = 40
        self.breakdown_pending = True
        if self.breakdowns >= 2:
            self.ptsd = True
            self.flags["ptsd"] = True
        return True

    def get_base_strength(self, clubs_data):
        base = 9
        if clubs_data.get(self.nation):
            for league_key in ["first", "second"]:
                for club in clubs_data[self.nation].get(league_key, []):
                    if club["name"] == self.club:
                        base = club["base"]
        return base

    def update_place(self, clubs_data):
        base = self.get_base_strength(clubs_data)
        total = sum(self.team_modifiers)
        raw_place = round(base - total / 2.0)
        league_teams = clubs_data.get(self.nation, {}).get(self.league, [])
        num_teams = max(1, len(league_teams) or 8)
        self.current_place = max(1, min(num_teams, raw_place))
        return self.current_place

    def reset_season_modifiers(self):
        self.team_modifiers = []

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
    if "stress" in effects:
        gs.add_stress(effects["stress"], party=bool(effects.get("party", False)))
    if effects.get("meal") and gs.trait == "cheburek_fan":
        gs.add_stress(-5)
        gs.mod("phy", 1)
    if effects.get("party") and gs.trait == "scandalist":
        gs.mod("media", 3)
        gs.counters["media_crises"] += 1
    if effects.get("important_match") and gs.trait == "ice_cold":
        gs.add_stress(-3)


def resolve_choice(gs, choice):
    if "check" in choice:
        chk = choice["check"]
        attr = chk["attr"]
        threshold = chk["threshold"]
        important = bool(chk.get("important", False) or choice.get("important", False))
        if "|" in attr:
            ok = gs.check_any(attr, threshold, important)
        else:
            ok = gs.check(attr, threshold, important)
        branch = "success" if ok else "fail"
        effects = choice.get(branch, {})
        apply_effects(gs, effects)
        return branch, effects
    effects = choice.get("effects", {})
    apply_effects(gs, effects)
    return "flat", effects


def _requirements_met(gs, requirements):
    for key, value in requirements.items():
        if key == "position":
            allowed = value if isinstance(value, list) else [value]
            if gs.position not in allowed:
                return False
        elif key == "club":
            allowed = value if isinstance(value, list) else [value]
            if gs.club not in allowed:
                return False
        elif key == "flags":
            for flag, expected in value.items():
                if gs.has_flag(flag) != bool(expected):
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


def is_choice_available(gs, choice):
    return _requirements_met(gs, choice.get("requires", {}))


def is_event_available(gs, event):
    return _requirements_met(gs, event.get("requires", {}))


def check_hint(choice):
    check = choice.get("check")
    if not check:
        return ""
    attr = str(check.get("attr", "")).split("|")[0].strip()
    return CHECK_HINTS.get(attr, "Ты собираешься с мыслями перед решающим действием.")


def choice_outcome(choice, branch):
    explicit = choice.get("outcome_" + branch)
    if explicit:
        return explicit
    if branch == "success":
        return "Тебе удалось справиться с эпизодом. Команда замечает твой вклад."
    if branch == "fail":
        return "Эпизод складывается не так, как хотелось. Последствия уже отражены в твоём состоянии."
    return choice.get("outcome", "")


def club_start_stress(clubs_data, nation, league, club_name, fallback=0):
    for club in clubs_data.get(nation, {}).get(league, []):
        if club.get("name") == club_name:
            return max(0, min(99, int(club.get("start_stress", fallback))))
    return max(0, min(99, int(fallback)))


def load_json(path):
    full = renpy.loader.transfn(path)
    with open(full, "r", encoding="utf-8") as source:
        return json.load(source)


def normalize_text(text_list):
    result = []
    for item in text_list:
        if isinstance(item, str):
            result.append([None, item])
        elif isinstance(item, dict):
            result.append([item.get("speaker"), item.get("text", "")])
        else:
            result.append([None, str(item)])
    return result


def load_events():
    events = {}
    try:
        data = load_json("events/events.json")
        for event in data.get("events", []):
            if "text" in event:
                event["text"] = normalize_text(event["text"])
            events[event["id"]] = event
    except Exception as error:
        print("Failed to load events.json: %s" % error)
    return events


def load_clubs():
    return load_json("data/clubs.json")


def _wd_l(points, total):
    points = max(0, min(total * 3, points))
    wins = min(total, points // 3)
    draws = points - 3 * wins
    losses = total - wins - draws
    while draws > 5 and wins > 0:
        wins -= 1
        draws = points - 3 * wins
        losses = total - wins - draws
    if draws < 0:
        draws = 0
        losses = total - wins
    return wins, draws, max(0, losses)


def generate_table(gs, clubs_data, league_key, place):
    teams = clubs_data[gs.nation][league_key]
    count = len(teams)
    total_matches = 2 * (count - 1)
    sorted_teams = sorted(teams, key=lambda team: team["base"])
    ranks = {team["name"]: index + 1 for index, team in enumerate(sorted_teams)}
    rows = []
    for team in teams:
        if team["name"] == gs.club:
            continue
        rank = ranks[team["name"]]
        expected = 30 - (rank - 1) * (26.0 / max(1, count - 1))
        points = max(0, min(total_matches * 3, round(expected + random.randint(-3, 3))))
        wins, draws, losses = _wd_l(points, total_matches)
        goals_for = max(0, round(10 + points * 0.7 + random.randint(-3, 3)))
        goals_against = max(0, round(30 - points * 0.7 + random.randint(-3, 3)))
        rows.append({"name": team["name"], "played": total_matches,
                     "w": wins, "d": draws, "l": losses,
                     "gf": goals_for, "ga": goals_against,
                     "pts": points, "gd": goals_for - goals_against})
    rows.sort(key=lambda row: (row["pts"], row["gd"]), reverse=True)
    target = max(0, min(len(rows), int(place) - 1))
    if target == 0:
        player_points = min(total_matches * 3, rows[0]["pts"] + 3)
    elif target >= len(rows):
        player_points = max(0, rows[-1]["pts"] - 3)
    else:
        player_points = (rows[target - 1]["pts"] + rows[target]["pts"]) // 2
    wins, draws, losses = _wd_l(player_points, total_matches)
    goals_for = max(0, round(10 + player_points * 0.7 + random.randint(-3, 3)))
    goals_against = max(0, round(30 - player_points * 0.7 + random.randint(-3, 3)))
    rows.insert(target, {"name": gs.club, "played": total_matches,
                         "w": wins, "d": draws, "l": losses,
                         "gf": goals_for, "ga": goals_against,
                         "pts": player_points, "gd": goals_for - goals_against})
    for index, row in enumerate(rows):
        row["place"] = index + 1
        row["zone"] = "top" if index < 3 else ("bottom" if index >= len(rows) - 3 else "mid")
    return rows
