init -1 python:
    import career_logic
    from career_logic import (
        GameState, is_choice_available, is_choice_relevant, resolve_choice, is_event_available,
        apply_effects, load_events, load_clubs, generate_table, match_count_text,
        choice_outcome, choice_sketch, club_start_stress, check_hint, press_topic, match_choices_95, TRAIT_LABELS, career_random,
        transition_teams, generate_transition, upper_table_1993, league_teams, bind_event, calculate_salary, ITEMS, MONTHLY_LIVING_COST
    )
    gs = GameState()
    all_events = load_events()
    expansion_slots = {}
    for expansion_event in all_events.values():
        if expansion_event.get("slot"):
            expansion_slots.setdefault(expansion_event["slot"], []).append(expansion_event["id"])
    clubs_data = load_clubs()

default career_match_active = False
default prior_warning = False
default prior_trust = 0

init python:
    def career_save_metadata(data):
        data["career_ready"] = bool(gs.club and gs.position and gs.trait and gs.payroll_season)

    def career_resume_slot():
        slots = renpy.list_saved_games(r"^(?:[0-9]+|auto|quick)-[0-9]+$", fast=True)
        ready = [slot for slot in slots if (renpy.slot_json(slot) or {}).get("career_ready") is True]
        return max(ready, key=renpy.slot_mtime, default=None)

    config.save_json_callbacks.append(career_save_metadata)

define agent = Character("Миро Райо", color="#ffcc00")

init python:
    def career_art(key, fallback="#0f0f1a"):
        path = "images/" + key + ".jpg"
        return Transform(path, fit="cover", xysize=(1280, 720)) if renpy.loadable(path) else Solid(fallback)

    def career_portrait(speaker, emotion="neutral"):
        roles = {
            "Агент": "agent", "Миро Райо": "agent",
            "Тренер": "coach", "Виктор Тихонов": "coach",
            "Ветеран": "veteran", "Сергей Семенов": "veteran",
            "Журналист": "journalist", "Филипп Морен": "journalist",
        }
        roles.update({
            "Олег Романцев": "roman_8", "Виктор Прокопенко": "prokop_8",
            "Валерий Овчинников": "ovchin_8", "Сергей Хусаинов": "husain_8",
            "Семёнов": "veteran",
        })
        role = roles.get(speaker)
        if speaker == "Ты":
            age = max(age for age in (16, 20, 25, 35) if age <= gs.age)
            role = "hero_" + str(age)
        if not role:
            return None
        for expression in (emotion, "neutral"):
            path = "images/portraits/" + role + "_" + expression + ".jpg"
            if renpy.loadable(path):
                return path
        return None

    def career_dialog_portrait(speaker, emotion, illustration):
        if speaker == "Тренер «Бенфики»" and illustration == "review_lisbon_coach":
            return career_lisbon_portrait()
        # Full scene art already establishes the speaker's appearance.
        if illustration or speaker in ("Тренер", "Петрович", "Тихонов", "Виктор Тихонов", "Садырин"):
            return False
        return career_portrait(speaker, emotion)

    def career_lisbon_portrait():
        path = "images/career8/review_lisbon_coach.jpg"
        if renpy.loadable(path):
            source = Transform(path, fit="cover", xysize=(1280, 720))
            return Transform(source, crop=(235, 62, 285, 285))
        return False

image bg default = Solid("#0f0f1a")
image bg field = career_art("bg/luzhniki_day", "#152b15")
image bg night = career_art("bg/luzhniki_night", "#142419")
image bg dynamo = career_art("bg/dynamo", "#1b2530")
image bg locker = career_art("bg/locker_pre", "#1c1c1c")
image bg locker_post = career_art("bg/locker_post", "#1c1c1c")
image bg office = career_art("bg/office", "#2a1a1a")
image bg press = career_art("bg/press", "#1a2333")
image bg bar = career_art("bg/bar", "#23182b")
image bg s1_party_invite = career_art("career8/s1_party_invite", "#23182b")
image bg home = career_art("bg/home", "#30251f")
image bg training = career_art("bg/training", "#152b15")
image bg alley = career_art("cg/alley", "#26222a")
image bg pistol = career_art("cg/pistol", "#202622")
image bg golden_match = career_art("cg/golden_match", "#152b15")
image bg manez = career_art("bg/career8_manez", "#2b2c25")
image bg field_autumn = career_art("bg/career8_autumn", "#282918")
image bg field_snow = career_art("bg/career8_snow", "#273133")
image bg v7_street = career_art("bg/career8_market", "#252c26")
image bg v7_cabin = career_art("bg/career8_cabin", "#252c26")
image bg v7_lisbon = career_art("bg/career8_lisbon", "#152b15")
image bg career8_camp_nou = career_art("bg/career8_camp_nou", "#152b15")

label after_load:
    $ gs.migrate(clubs_data)
    $ renpy.block_rollback()
    return

label start:
    $ gs = GameState()
    scene bg default
    "Карьера."
    "История одного футболиста."
    "Начало 1992 года. Тебе 16."

    $ gs.nation = "RU"
    call screen create_position

label choose_starting_league:
    call screen create_difficulty
    if _return == "back":
        call screen create_position
        jump choose_starting_league
    call screen create_club
    if _return == "back":
        jump choose_starting_league
    call play_event("AGENT_INTRO")
    call play_event("CAREER_MODE")
    call play_event("CAREER_TRAIT")

    $ gs.mod("money", 0 if gs.mode_realism else 500)
    $ gs.age = 16
    $ gs.season = 1
    $ gs.start_stress = club_start_stress(clubs_data, gs.nation, gs.league, gs.club, gs.start_stress)
    $ gs.stress = min(55, gs.start_stress * 3 // 4)
    $ gs.update_place(clubs_data)
    $ gs.begin_season()
    $ gs.advance_finances(gs.month - 1)

    show screen hud
    jump season_s1

label play_position_event(eid):
    call play_event(eid + "_" + gs.position)
    return

label career_line(speaker, line, current=0, total=1, portrait=False, focus_art=False):
    $ narrator.add_history("adv", speaker, line)
    call screen vn_dialog(speaker, line, current, total, portrait, focus_art)
    $ persistent.career_read_text.add(line)
    return

label career_set_month(month):
    $ served_matches = gs.set_month(month)
    if served_matches:
        $ ban_message = "Между сценами засчитано по дисквалификации: {}. ".format(match_count_text(served_matches))
        if gs.suspension_matches:
            $ ban_message += "Осталось: {}.".format(match_count_text(gs.suspension_matches))
        else:
            $ ban_message += "Матчевая дисквалификация закончилась."
        $ narrator.add_history("adv", "Дисквалификация", ban_message)
        $ renpy.notify(ban_message)
    return

label play_event(eid, fixture=None):
    if eid == "PRESS_SNIPPET":
        $ press_tone = gs.press_headline()
        $ headline = gs.next_press_issue(all_events[eid]["headlines"], (fixture or {}).get("topic", "club"), press_tone)
        if headline:
            $ narrator.add_history("adv", "Газета «Футбол»", headline)
            call screen press_snippet(headline, press_tone)
            $ persistent.career_read_text.add(headline)
        return
    if fixture is not None:
        $ event = dict(all_events[eid], **fixture)
    else:
        $ event = bind_event(gs, all_events.get(eid), clubs_data)
    if event and fixture is not None and fixture.get("opponent"):
        $ gs.opponent = fixture["opponent"]
    if event is None or not is_event_available(gs, event):
        return
    if event.get("month"):
        call career_set_month(event["month"])
        $ gs.advance_finances(gs.month - 1)
    if event.get("home"):
        $ gs.opponent = event["away"] if gs.club == event["home"] else event["home"]
    else:
        $ gs.opponent = event.get("opponent") or ("Луч" if eid == "S1_HIST_PISTOL" and gs.club in ("Океан", "Сахалин", "Амур") else None)
    if eid == "NEW_EXPENSES":
        $ gs.set_flag("rehab_needed", gs.injury_months > 0)
    if not is_event_available(gs, event) or not any(is_choice_available(gs, choice) for choice in event["choices"]):
        return
    $ is_match = event.get("home") or event.get("match", False)
    if gs.season == 3 and is_match:
        $ gs.set_flag("away_loss", False)
    if is_match:
        $ career_match_active = True
        $ missed = gs.miss_match_reason()
        if missed:
            "[missed]"
            $ gs.record_match(event)
            $ career_match_active = False
            if gs.coach_review_due and gs.has_flag("squad_exile"):
                call play_event("COACH_REVIEW_RETURN")
            elif gs.has_flag("squad_exile") and not gs.exile_discussed:
                call play_event("SQUAD_EXILE_RESOLVE")
                if gs.has_flag("exile_transfer_pending"):
                    $ gs.plan_exile_transfer(clubs_data)
                    call play_event("SQUAD_EXILE_TRANSFER")
            return
        $ gs.appearances += 1
        $ renpy.block_rollback()
    $ scene_illustration = gs.pick_illustration(event["art"]) if event.get("art") else None
    if scene_illustration:
        scene expression career_art("career8/" + scene_illustration)
    else:
        $ bg_name = event.get("bg", "default")
        scene expression "bg " + bg_name
    
    $ text_lines = [] if event.get("screen") == "choose_mode" else event.get("text", [])
    if eid == "NEW_WAGE_DELAY":
        $ text_lines = list(text_lines) + [[None, "Клуб должен тебе $" + str(gs.salary_debt) + "."]]
    if fixture is not None and "live_score" in fixture:
        $ text_lines = [[pair[0], pair[1].replace("{live_score}", fixture["live_score"]), *pair[2:]] for pair in text_lines]
    $ career_scene_stats = False
    $ focus_art = scene_illustration in ("review_interview_tunnel", "review_interview_room", "review_lisbon_coach") or eid == "COACH_REVIEW_RETURN"
    $ i = 0
    while i < len(text_lines):
        $ pair = text_lines[i]
        $ portrait = career_dialog_portrait(pair[0], pair[2] if len(pair) > 2 else "neutral", scene_illustration)
        call career_line(pair[0], pair[1], i, len(text_lines), portrait, focus_art)
        $ i += 1
        
    if event.get("screen") == "choose_mode":
        call screen choose_mode(event)
    elif event.get("screen") == "choose_trait":
        call screen choose_trait(event)
    else:
        call screen event_choices(event, focus_art)
    $ chosen = _return
    if renpy.is_skipping() and not _preferences.skip_after_choices:
        $ renpy.stop_skipping()
    $ prior_goals = gs.goals
    $ prior_trust = gs.attrs["rep_coach"]
    $ prior_warning = gs.stress_warning
    if not event.get("screen"):
        $ narrator.add_history("adv", "Твой выбор", chosen["text"])
    if is_match:
        $ gs.match_phy_modifier = gs.next_match_phy
        $ gs.next_match_phy = 0
    $ branch, effects = resolve_choice(gs, chosen, event)
    $ gs.match_phy_modifier = 0
    if is_match and not event.get("shootout_95"):
        $ gs.goalless_matches = 0 if gs.goals > prior_goals else gs.goalless_matches + 1
    $ renpy.block_rollback()
    $ outcome_text = choice_outcome(chosen, branch, gs.trait)
    if chosen.get("play_hurt") and effects.get("injury_months") == 3:
        $ outcome_text = "Связки не выдерживают. Врач отводит на восстановление три месяца."
    if effects.get("cg"):
        scene expression "bg " + effects["cg"]
    $ score = gs.record_match(event, chosen, branch, effects)
    $ match_bonus = gs.reward_match(event, score) if is_match else 0
    if is_match and gs.snitch_matches:
        $ gs.snitch_matches -= 1
    if gs.season <= 4 and gs.league != "portugal" and not gs.has_flag("transition_pending") and (not gs.season_history or gs.season_history[-1]["season"] < gs.season):
        $ gs.update_place(clubs_data)
    if outcome_text:
        $ sketch = gs.pick_illustration(choice_sketch(chosen, branch, gs.trait, effects))
        $ narrator.add_history("adv", event["title"], outcome_text + (" · " + score if score else ""))
        call screen event_outcome(event, outcome_text, sketch, score, match_bonus)
        $ persistent.career_read_text.add(outcome_text)
    if gs.season == 4 and (effects.get("debt") or effects.get("counters", {}).get("red_cards") or effects.get("rumor", 0) <= -15):
        $ gs.set_flag("scandal_95")
    $ gs.fired_events.append(eid)
    if event["id"] != eid:
        $ gs.fired_events.append(event["id"])
    $ prevent_press_chain = event.get("press_followup", False)

    $ renpy.block_rollback()
    if gs.breakdown_pending:
        call breakdown_scene
    $ career_match_active = False
    if abs(gs.press_delta) >= 10:
        call play_event("PRESS_SNIPPET", {"topic": press_topic(event, effects, score)})
    if not prevent_press_chain:
        if gs.has_flag("career_crisis"):
            call play_event("TALK_WITH_COACH")
        if gs.roll_interview():
            call play_event("EXCLUSIVE_INTERVIEW")
    return

label breakdown_scene:
    $ gs.breakdown_pending = False
    if gs.breakdowns >= 3:
        jump bad_end
    elif gs.breakdowns == 1:
        jump breakdown_1
    else:
        jump breakdown_2
    return

label breakdown_1:
    scene bg locker_post
    "НЕРВНЫЙ СРЫВ. Первый."
    call breakdown_consequence
    "Ты с трудом восстанавливаешься. Это оставило след."
    return

label breakdown_2:
    scene bg locker_post
    "НЕРВНЫЙ СРЫВ. Второй."
    "В решающие минуты шум трибун возвращает тебя в тот день. Ещё один срыв — и карьера закончится."
    call breakdown_consequence
    return

label breakdown_consequence:
    if gs.breakdown_incident is None:
        $ gs.apply_breakdown_consequence()
    if gs.breakdown_incident == 0:
        "На тренировке ты не слышишь свистка и идёшь в стык. Врач назначает месяц восстановления."
    elif gs.breakdown_incident == 1:
        "Ты срываешься на журналиста. Наутро твои слова печатают на первой полосе."
    else:
        "В раздевалке начинается драка. Тренер отстраняет тебя на три игры."
    $ gs.breakdown_incident = None
    return

label bad_end:
    scene bg default
    hide screen hud
    "НЕРВНЫЙ СРЫВ. Третий. Последний."
    "Ты больше не можешь. Карьера рушится."
    python:
        key_attrs = ["aggression", "media", "temperament", "loyalty", "professionalism"]
        highest = max(key_attrs, key=lambda x: gs.attrs.get(x, 0))
        ending_id = key_attrs.index(highest) + 1
    if ending_id == 1:
        jump bad_end_aggression
    elif ending_id == 2:
        jump bad_end_media
    elif ending_id == 3:
        jump bad_end_temperament
    elif ending_id == 4:
        jump bad_end_loyalty
    else:
        jump bad_end_professionalism

label bad_end_aggression:
    scene bg default
    "Ты не смог обуздать свою агрессию."
    "Драки, скандалы, отстранения — всё это накопилось."
    "Ты уходишь из футбола со скандалом. Тебя боятся, но не уважают."
    "Бывшие партнёры не хотят тебя вспоминать."
    "КОНЦОВКА: РАЗРУШЕННЫЙ БОЕЦ."
    $ renpy.full_restart()

label bad_end_media:
    scene bg default
    "Ты стал заложником собственного образа."
    "Медийность съела тебя изнутри. Пресса растерзала твою психику."
    "Ты не смог отделить себя от того, кем тебя сделали газеты."
    "Ты исчезаешь из публичного поля. Никто не помнит, каким ты был на поле."
    "КОНЦОВКА: СЛОМАННЫЙ ЗВЕЗДОЙ."
    $ renpy.full_restart()

label bad_end_temperament:
    scene bg default
    "Твой характер сломал тебя."
    "Вспышки ярости, неконтролируемые поступки, разрушенные отношения."
    "Ты остался один. С деньгами, но без друзей и без футбола."
    "Тебе не простят ни одного из твоих срывов."
    "КОНЦОВКА: ИЗГНАННИК."
    $ renpy.full_restart()

label bad_end_loyalty:
    scene bg default
    "Ты был верен до конца. Но верность тебя не спасла."
    "Ты отдал клубу всё, а взамен получил лишь выжженную психику и пустоту."
    "Клуб не сберёг тебя. Болельщики не заметили, как ты сгорел."
    "Ты уходишь тихо. Слишком поздно поняв цену."
    "КОНЦОВКА: СГОРЕВШИЙ ЗА КЛУБ."
    $ renpy.full_restart()

label bad_end_professionalism:
    scene bg default
    "Ты всегда был самым старательным."
    "Но даже стальные ломаются. Ты тренировался больше всех, играл через боль, не позволял себе слабости."
    "Твоё тело и психика не выдержали того темпа, который ты сам себе задал."
    "Ты уходишь из футбола сгоревшим, но так и не поняв, что не все награды достаются трудом."
    "КОНЦОВКА: ПЕРЕГОРЕВШИЙ."
    $ renpy.full_restart()

label finish_season(base_strength=None):
    $ table = generate_table(gs, clubs_data, gs.league)
    $ player_row = next(row for row in table if row["name"] == gs.club)
    $ place = player_row["place"]
    $ arc = "TITLE_RACE" if place <= 3 else "RELEGATION" if player_row["zone"] == "bottom" else "MIDTABLE"
    $ gs.current_place = place
    call screen league_table(table)
    $ gs.season_history.append({"season": gs.season, "place": place, "arc": arc, "objective_met": gs.club_goal_met(place, player_row["zone"])})
    if gs.league == "first":
        $ gs.award_league_place(place)
        if arc == "RELEGATION":
            $ gs.league = "second"
            "Клуб вылетает из высшей лиги."
    elif place <= 3:
        $ gs.league = "first"
        "Клуб выходит в высшую лигу."

    call season_board
    call settle_season_income
    call offseason_recovery
    return

label settle_season_income:
    $ last_living_cost = gs.settle_living_expenses(12)
    if last_living_cost:
        "Расходы на жизнь за оставшиеся месяцы: $[last_living_cost]."
    if gs.trait == "investor":
        if career_random().randrange(2):
            call play_event("VOUCHERS_UP")
        else:
            call play_event("VOUCHERS_DOWN")
    else:
        $ salary = gs.settle_salary()
        if salary:
            "Клуб перечисляет остаток оклада за сезон и надбавки. Начислено $[salary]."
    $ objective_bonus = gs.reward_club_goal()
    if objective_bonus:
        "Команда выполнила задачу клуба. Ты получаешь премию $[objective_bonus]."
    $ honesty_bonus = gs.reward_honesty()
    if honesty_bonus:
        "За честную игру клуб выплачивает премию $[honesty_bonus]."
    return

label offseason_recovery:
    call play_event("VACATION")
    call play_event("S1_HOME_FAMILY")
    call play_event("HOME_FISHING")
    call play_event("HOME_MARKET")
    call play_event("NEW_MARKET")
    call play_event("NEW_HOME_GIFT")
    if gs.attrs["rep_coach"] < 45:
        call play_event("HOME_BOOT")
    else:
        call play_event("HOME_RADIO")
    call play_event("HOME_DATE")
    call play_event("PTSD_RECOVERY")

    $ gs.grow()
    $ gs.reset_season_modifiers()
    $ gs.age += 1
    $ gs.season += 1
    $ gs.advance_offseason()
    return

label season_s1:
    call play_event("PRESEASON_TRAINING")
    call play_event("S1_P1")
    call play_event("S1_P2")
    call play_expansion("early92")
    call play_event("S1_HIST_NEW_LEAGUE")
    call play_event("S1_C1")
    call play_event("S1_C2")
    call play_position_event("S1_C3")

    call play_event("H92_BESCHASTNYKH")
    call play_event("S1_HIST_GK")
    call play_event("GK_1")
    call play_event("S1_HIST_ZENIT")
    call play_event("MATCH_ROTOR")
    call play_event("H92_KULIK_KIROV")
    call play_event("H92_MARTYANOV")
    call play_event("S1_HIST_VERETINOV")
    call play_event("H92_SMIRNOV_VODNIK")
    call play_event("H92_OSIPOV")
    call play_event("H92_TATARKIN")
    call play_event("H92_KOBELEV")
    call play_event("H92_MUKHAMADIEV")
    call play_event("H92_RYBAKOV_AWAY")
    call play_event("H92_GORBACH")
    call play_event("H92_NIDBAYKIN")
    call play_event("H92_MATVEEV")
    call play_event("S1_HIST_BONDARENKO")
    call play_event("H92_NATALUSHKO")
    call play_event("S1_HIST_KASUMOV")
    call play_event("AGENT_ROTOR")
    call play_event("S1_HIST_SCANDAL")
    call play_event("H92_KASUMOV_HATTRICK")
    call play_event("MATCH_OCEAN")
    call play_event("H92_KULIK_TORPEDO")
    call play_event("FIXING_REVIEW")
    call play_event("MATCH_ASMARAL")
    call play_event("S1_HIST_ROTOR")
    call play_event("S1_HIST_PISTOL")
    call play_event("S1_E1")
    call play_event("S1_C4")
    call play_expansion("summer92")
    if gs.injury_months:
        call play_event("NEW_EXPENSES")
    call play_event("H92_FAIZULLIN")
    call play_event("H92_SULEYMANOV")
    call play_event("MATCH_DYNAMO")
    call play_event("MATCH_DERBY")
    call play_event("S1_C5")
    call play_event("FANS_AT_GATE")
    call play_event("SPONSOR_OFFER")
    if gs.roll_charity():
        call play_event("RANDOM_CHARITY")
    scene bg locker_post
    call career_line(None, "К вечеру база опустела. Ты уже переобулся и собирался домой, когда партнёр окликнул тебя у двери.")
    call play_event("S1_C6")
    call play_event("MATCH_CSKA_HOME")
    call play_expansion("repeat")
    call play_event("H92_LIVERPOOL")
    call play_event("S1_C7")
    call play_event("MATCH_BARCA")
    call play_position_event("S1_C8")
    call finish_season()
    jump next_season

label next_season:
    if gs.season > 2:
        jump epilogue_1994
    jump season_1993

label season_board:
    scene expression career_art("career8/review_season_board")
    $ board = gs.season_history[-1]
    $ season_memo = "{} год · {} · {}-е место. За сезон сыграно матчей: {}. Голов: {}.".format(
        1991 + board["season"], gs.club, board["place"],
        gs.appearances - gs.board_appearances, gs.goals - gs.board_goals)
    $ gs.board_appearances = gs.appearances
    $ gs.board_goals = gs.goals
    call career_line("Доска команды", season_memo)
    return

label season_1993:
    $ gs.prepare_1993(clubs_data)
    $ gs.begin_season()
    $ gs.hold_paycheck = True
    $ gs.advance_finances(gs.month - 1)
    scene bg field_snow
    "Весна 1993 года. Во второй чемпионат ты входишь с опытом первого сезона."
    if gs.league == "first":
        "В Высшей лиге восемнадцать клубов. Две команды вылетят напрямую, ещё три сыграют в переходном турнире."
    else:
        $ division = gs.zone_1993
        "Твоя команда играет в зоне «[division]» Первой лиги. Победитель зоны получит место в переходном турнире."
    call play_event("NEW_WAGE_DELAY")
    call play_event("SQUAD_EXILE_RESOLVE")
    if gs.has_flag("exile_transfer_pending"):
        $ gs.plan_exile_transfer(clubs_data)
        call play_event("SQUAD_EXILE_TRANSFER")
    call play_expansion("early93")
    call play_event("FAMILY_FOLLOWUP")
    call play_event("HOME_DATE_REPLY")
    call play_event("S3_DOPING")
    call play_event("S3_SNOW")
    call play_event("PRESEASON_TRAINING")
    call play_event("S3_PRACTICE")
    call play_event("S3_AGENT")
    call play_event("S3_AGENT_FALLOUT")
    call play_event("S3_LOCKER_LESSON")
    call play_event("H93_KAMAZ_ROTOR")
    call play_event("H93_KS_ROSTOV")
    call career_set_month(6)
    call play_event("S3_CAPTAIN")
    call play_event("S3_ZONE_RACE")
    call play_event("S1_ACT_GK")
    call play_event("S1_ACT_DEF")
    call play_event("S1_ACT_MID")
    call play_event("S1_ACT_FWD")
    call play_event("S3_MEDICINE")
    call play_event("NEW_WAGE_RETURN")
    call play_event("NEW_MENTOR_RETURN")
    call play_event("NEW_MENTOR_RIVAL")
    call play_event("NEW_EXPENSES")
    call play_event("NEW_GEAR")
    call play_event("H93_OCEAN_CSKA")
    call play_event("H93_LUCH_LOKO")
    call play_event("H93_TORPEDO_VL")
    call play_event("H93_KAMYSHIN")
    call play_event("S3_PRESS_REVIEW")
    call play_event("S3_TV")
    call play_event("SPONSOR_OFFER")
    if gs.roll_charity():
        call play_event("RANDOM_CHARITY")
    call play_event("S1_E1")
    if gs.league == "first" and gs.club == "Ротор":
        $ forecast = generate_table(gs, clubs_data, "first", scores=dict(gs.match_scores))
        $ gs.set_flag("title_race_1993", any(row["name"] == gs.club for row in forecast[:3]))
    call play_event("S3_ROTOR_TITLE")
    call play_event("H93_LOKO_DERBY")
    call play_event("GK_2")
    call play_event("S3_LATE_MATCH")
    if gs.league == "first" and gs.club == "Спартак (М)":
        $ forecast = generate_table(gs, clubs_data, "first", scores=dict(gs.match_scores))
        $ gs.set_flag("title_race_1993", any(row["name"] == gs.club for row in forecast[:3]))
    call play_position_event("S3_GOLDEN_MATCH")
    call play_event("H93_DYNAMO_LUCH")
    call play_event("GK_3")
    call play_expansion("late93")
    call play_event("CIS_PROJECT_REPLY")
    call play_expansion("repeat")
    call play_event("S3_SENIOR_CALL")
    call play_position_event("S1_C8")
    call play_event("S4_LETTER_14")
    call finish_1993
    jump epilogue_1994

label finish_1993:
    $ table = generate_table(gs, clubs_data, gs.league)
    $ player_row = next(row for row in table if row["name"] == gs.club)
    $ place = player_row["place"]
    $ gs.current_place = place
    $ upper = upper_table_1993(gs, clubs_data, table)
    $ qualified = transition_teams(gs, clubs_data, table, upper)
    $ playoff = player_row["zone"] == "playoff" or (gs.league == "second" and place == 1)
    $ arc = "PLAYOFF" if playoff else ("TITLE_RACE" if gs.league == "first" and place <= 3 else ("RELEGATION" if player_row["zone"] == "bottom" else "MIDTABLE"))
    call screen league_table(table)
    $ gs.season_history.append({"season": gs.season, "league": gs.league, "place": place, "arc": arc, "objective_met": gs.club_goal_met(place, player_row["zone"])})
    if gs.league == "first":
        $ gs.award_league_place(place)
        if place == 1:
            "Финальная таблица подтверждает: твой клуб — чемпион России 1993 года."
            if gs.club == "Спартак (М)":
                call career_line("Олег Романцев", "Теперь можно праздновать. За этот сезон ты стал игроком, на которого можно положиться.", portrait=career_portrait("Олег Романцев", "happy"))
        elif player_row["zone"] == "bottom":
            $ gs.league = "second"
            "Команда вылетает напрямую. В следующем году ей предстоит играть в Первой лиге."
    if playoff:
        $ gs.set_flag("transition_pending")
        call play_event("S3_REFEREE")
        call play_position_event("S3_FIXING")
        $ playoff_table = generate_transition(gs, clubs_data, qualified)
        call screen league_table(playoff_table, True)
        $ playoff_place = next(row["place"] for row in playoff_table if row["name"] == gs.club)
        $ gs.season_history[-1]["playoff_place"] = playoff_place
        $ gs.league = "first" if playoff_place <= 3 else "second"
        $ gs.set_flag("transition_pending", False)
        if playoff_place <= 3:
            "Клуб попадает в тройку переходного турнира. В 1994 году он сыграет в Высшей лиге."
        else:
            "Клуб остаётся за пределами тройки. Следующий сезон он проведёт в Первой лиге."
    else:
        $ playoff_table = generate_transition(gs, clubs_data, qualified)
    $ gs.first_1994 = [row["name"] for row in upper[:13]] + [row["name"] for row in playoff_table[:3]]
    call season_board
    call settle_season_income
    call offseason_recovery
    return

label epilogue_1994:
    if not gs.has_flag("epilogue_done"):
        $ gs.set_flag("epilogue_done")
        call play_event("S4_SUSPICION")
        call play_event("S4_BETRAYAL_REVENGE")
        call play_event("S4_FIXING_THREATS")
        call play_event("S4_REFEREE_SCANDAL")
        call play_event("S4_FIXING_CHECK")
        call play_event("S4_DOPING_RESULT")
    if gs.has_flag("contract_terminated"):
        jump demo_end
    jump season_1994

label season_1994:
    $ gs.begin_season()
    $ gs.update_place(clubs_data)
    $ gs.advance_finances(gs.month - 1)
    scene bg field
    "Весна 1994 года. В Высшей лиге теперь шестнадцать клубов. Чемпионат проходит в два круга, а за победу по-прежнему дают два очка."
    if gs.league == "second":
        "Первую лигу объединили в один дивизион. Два первых места дают путёвку наверх."
    call play_event("SQUAD_EXILE_RESOLVE")
    if gs.has_flag("exile_transfer_pending"):
        $ gs.plan_exile_transfer(clubs_data)
        call play_event("SQUAD_EXILE_TRANSFER")
    call play_event("PRESEASON_TRAINING")
    call play_expansion("early94")
    call play_event("FAMILY_FOLLOWUP")
    call play_event("HOME_DATE_REPLY")
    call play_event("S4_MILITARY_CAMP")
    call play_event("S4_FAKE_BOOTS")
    call play_event("NEW_FAKE_PAYOFF")
    call play_event("NEW_PLAYER_TRIP")
    call play_position_event("NEW_CSKA_URAL")
    call play_position_event("NEW_DYNAMO_LOKO")
    call play_position_event("NEW_KAMAZ_VL")
    call play_position_event("S4_BARCA_SPARTAK")
    call check_airport_1994
    call play_position_event("S4_SPARTAK_DYNAMO")
    call check_airport_1994
    call play_position_event("NEW_ZENIT_CHITA")
    call play_event("S4_CASH_IN_BAGS")
    call play_event("NEW_CLIPPING")
    call league_round_1994(4, 0)
    call play_position_event("NEW_ZENIT_SHINNIK")
    call play_position_event("S4_ROTOR_SPARTAK")
    call check_airport_1994
    call play_event("S4_CHERCHESOV")
    call play_event("S4_STEWARDESS")
    call play_event("S4_PRESS_TROLLING")
    call play_event("S4_GIRLFRIEND")
    call play_event("NEW_EXPENSES")
    call play_event("S4_INJURY_RECOVERY")
    if gs.injury_months and gs.has_flag("injury_severe"):
        call play_event("NEW_EXPENSES")
    call play_event("NEW_SQUAD_REVIEW")
    if gs.has_flag("exile_transfer_pending"):
        $ gs.plan_exile_transfer(clubs_data)
        call play_event("SQUAD_EXILE_TRANSFER")
    call league_round_1994(7, 1)
    call play_position_event("S4_CSKA_SPARTAK")
    call check_airport_1994
    call play_event("S4_MOREN_TRAP")
    call play_event("S4_SPONSOR_OFFER")
    call play_event("S4_BUDOGOSSKY")
    call play_event("NEW_KAMAZ_AFTER")
    call check_airport_1994
    call play_event("S4_CSKA_BRATKI")
    call play_position_event("S4_DYNAMO_SPARTAK")
    call check_airport_1994
    call play_event("NEW_CSKA_AFTER")
    call play_event("NEW_CSKA_PRESS")
    call play_event("NEW_FAMILY_THANKS")
    call play_event("NEW_SPONSOR_BACKLASH")
    call play_event("S4_PARTNER_WIFE")
    call play_event("S4_AGENT_DEMANDS")
    call play_position_event("NEW_DYNAMO_LADA")
    call play_event("S4_MARKELOV_SCANDAL")
    call check_airport_1994
    call play_event("S4_GORELOV_TACKLE")
    call check_airport_1994
    call play_position_event("NEW_CSKA_TYUMEN")
    call play_position_event("NEW_KAMAZ_ROTOR")
    call league_round_1994(11, 2)
    call play_expansion("repeat")
    call play_expansion("late94")
    $ table = generate_table(gs, clubs_data, gs.league)
    $ player_row = next(row for row in table if row["name"] == gs.club)
    $ gs.current_place = player_row["place"]
    call screen league_table(table)
    $ gs.season_history.append({"season": 3, "league": gs.league, "place": gs.current_place, "arc": player_row["zone"], "objective_met": gs.club_goal_met(gs.current_place, player_row["zone"])})
    if gs.league == "first":
        $ gs.award_league_place(gs.current_place)
        if player_row["zone"] == "bottom":
            $ gs.league = "second"
            "По итогам чемпионата клуб покидает Высшую лигу."
    elif gs.current_place <= 2:
        $ gs.league = "first"
        "Команда завоевала путёвку в Высшую лигу."
    call season_board
    call settle_season_income
    call play_event("PTSD_RECOVERY")
    $ gs.season += 1
    $ gs.age += 1
    if gs.has_flag("european_ban"):
        call play_event("S4_EUROPE_OFFER")
    else:
        $ europe_blocker = gs.european_offer_blocker()
        if europe_blocker:
            scene bg office
            agent "[europe_blocker]"
        else:
            call play_event("S4_TRANSFER_EUROPE")
    if gs.league == "portugal":
        call play_event("S5_PORTUGAL_ADAPTATION_1")
        call play_event("S5_PORTUGAL_ADAPTATION_2")
    jump season_1995

label check_airport_1994:
    if gs.has_flag("away_loss") and "S4_FANS_AIRPORT" not in gs.fired_events:
        call play_expansion("airport94")
        call play_event("S4_FANS_AIRPORT")
    $ gs.set_flag("away_loss", False)
    return

label league_round_1994(month, round_index):
    $ roster = {team["name"]: team["base"] for team in league_teams(gs, clubs_data)}
    $ clubs = [club for club in roster if club != gs.club]
    $ reserved = {(row["home"], row["away"]) for row in all_events.values() if row.get("league_fixture") and row.get("home") and row.get("month")}
    $ fixtures = [(gs.club, other) if round_index == 1 else (other, gs.club) for other in clubs]
    $ fixtures = [pair for pair in fixtures if pair not in gs.match_scores and pair not in reserved]
    if not fixtures:
        return
    $ home, away = fixtures[round_index * len(fixtures) // 3]
    $ home_strength, away_strength = roster[home], roster[away]
    $ provisional = "1:0" if home_strength + 1 < away_strength else ("0:1" if away_strength + 2 < home_strength else "1:1")
    $ fixture = {"id": "S4_LEAGUE_ROUND_" + str(round_index), "home": home, "away": away, "game_score": provisional, "month": month, "subtitle": home + " — " + away}
    $ fixture["live_score"] = provisional
    $ round_notes = ("Скамейку гостей почти заглушает трибуна. После выноса мяч возвращается к углу вашей штрафной.", "За несколько минут до свистка соперник прессингует у бровки. Капитан просит перевести игру через центр.", "На сыром газоне мяч отскакивает дальше обычного. Соперник оставил троих впереди и ждёт потери.")
    $ opening = [None, "На табло " + provisional + ". " + round_notes[round_index]]
    $ fixture["text"] = [opening] + all_events["NEW_AWAY_" + gs.position]["text"][1:]
    call play_event("NEW_PROGRAMME", {"month": month, "subtitle": home + " — " + away + " · киоск стадиона"})
    call play_event("NEW_AWAY_" + gs.position, fixture)
    call check_airport_1994
    if round_index == 2 and fixture["id"] in gs.fired_events:
        call play_event("NEW_SHIRT", {"subtitle": home + " — " + away})
    return

label play_expansion(slot):
    $ expansion_ids = expansion_slots.get(slot, ())
    $ expansion_index = 0
    while expansion_index < len(expansion_ids):
        call play_event(expansion_ids[expansion_index])
        $ expansion_index += 1
    return

label season_1995:
    $ gs.advance_offseason()
    $ gs.reset_season_modifiers()
    $ gs.begin_season()
    $ gs.advance_finances(gs.month - 1)
    if gs.league == "portugal":
        jump season_1995_portugal

    scene bg field
    "Весна 1995 года. Теперь победа приносит три очка."
    if gs.league == "second":
        "Из Первой лиги наверх поднимутся три клуба."
    call play_event("SQUAD_EXILE_RESOLVE")
    if gs.has_flag("exile_transfer_pending"):
        $ gs.plan_exile_transfer(clubs_data)
        call play_event("SQUAD_EXILE_TRANSFER")
    call play_event("FAMILY_FOLLOWUP")
    call play_event("HOME_DATE_REPLY")
    call play_expansion("95_spring")
    call league_round_1995(4, 0)
    call career_set_month(5)
    $ gs.advance_finances(4)
    call play_expansion("95_may")
    call league_round_1995(5, 1)
    call career_set_month(6)
    $ gs.advance_finances(5)
    $ gs.set_flag("cup_final_95", gs.club in ("Динамо (М)", "Ротор"))
    call play_expansion("95_june")
    if gs.has_flag("trophy_95"):
        call play_expansion("95_trophy")
    call league_round_1995(6, 2)
    call career_set_month(7)
    $ gs.advance_finances(6)
    call play_expansion("95_summer")
    call league_round_1995(8, 3)
    call play_event("FANS_AT_GATE")
    call play_expansion("95_september")
    call career_set_month(9)
    $ gs.advance_finances(8)
    call play_expansion("95_autumn")
    call play_expansion("95_october")
    call league_round_1995(10, 4)
    call play_expansion("95_finish")
    call league_round_1995(11, 5)
    $ table = generate_table(gs, clubs_data, gs.league)
    $ player_row = next(row for row in table if row["name"] == gs.club)
    $ gs.current_place = player_row["place"]
    call screen league_table(table)
    $ gs.season_history.append({"season": 4, "league": gs.league, "place": gs.current_place, "arc": player_row["zone"], "objective_met": gs.club_goal_met(gs.current_place, player_row["zone"])})
    if gs.league == "first":
        $ gs.award_league_place(gs.current_place)
        if gs.current_place == 1:
            $ gs.set_flag("title_95")
            call play_event("95_FANS")
        if player_row["zone"] == "bottom":
            $ gs.league = "second"
    elif gs.current_place <= 3:
        $ gs.league = "first"
        "Твоя команда выходит в Высшую лигу."
    call season_board
    call settle_season_income
    call play_event("PTSD_RECOVERY")
    call play_expansion("95_transfer")
    $ gs.season += 1
    $ gs.age += 1
    jump demo_end

label league_round_1995(month, round_index):
    call career_set_month(month)
    $ gs.advance_finances(gs.month - 1)
    $ strength_95 = {row["name"]: row["base"] for row in league_teams(gs, clubs_data)}
    $ teams_95 = [club for club in strength_95 if club != gs.club]
    $ away_95 = round_index % 2 == 0
    $ scheduled_95 = {(row["home"], row["away"]) for row in all_events.values() if row.get("season_95_fixture") and not row.get("european") and not row.get("cup")}
    $ possible_95 = [(other, gs.club) if away_95 else (gs.club, other) for other in teams_95]
    $ possible_95 = [pair for pair in possible_95 if pair not in scheduled_95 and pair not in gs.match_scores]
    # Keep the trip to Vladikavkaz available for its October storyline.
    $ vladikavkaz_95 = ("Спартак (Вл)", gs.club)
    $ bribery_fixture_95 = gs.league == "first" and gs.club not in ("Спартак (М)", "Спартак (Вл)")
    if bribery_fixture_95 and round_index < 4 and vladikavkaz_95 in possible_95:
        $ possible_95.remove(vladikavkaz_95)
    if not possible_95:
        return
    $ home_95, away_club_95 = possible_95[(round_index * 3) % len(possible_95)]
    if bribery_fixture_95 and round_index == 4 and vladikavkaz_95 in possible_95:
        $ home_95 = "Спартак (Вл)"
        call play_event("95_ALANIA_BRIBE", {"opponent": "Спартак (Вл)"})
    $ match_eid_95 = {"MID": "MID_VISION", "FWD": "FWD_FINISH"}.get(gs.position, "S95_ROUND_" + gs.position)
    $ duel_95 = all_events[match_eid_95]
    $ opponent_95 = home_95 if away_95 else away_club_95
    $ state_95 = ("level" if round_index in (0, 3) or home_95 == "Спартак (Вл)" and round_index == 4 else
                  "hold" if strength_95[gs.club] <= strength_95[opponent_95] else "chase")
    $ own_score_95, rival_score_95 = {"level": (1, 1), "hold": (1, 0), "chase": (0, 1)}[state_95]
    $ live_95 = "{}:{}".format(*((rival_score_95, own_score_95) if away_95 else (own_score_95, rival_score_95)))
    $ setup_95 = {
        "level": "Сил на длинные атаки уже нет. У команд осталось время на один розыгрыш.",
        "hold": "Вы ведёте в один мяч. Соперник поднял крайних защитников, а тренер просит не раскрывать центр.",
        "chase": "Вы уступаете в один мяч. Соперник растягивает паузы, и тренер указывает на свободную зону у штрафной."
    }[state_95]
    $ fixture_95 = {"id": "S95_LEAGUE_ROUND_" + str(round_index), "home": home_95, "away": away_club_95, "game_score": live_95, "month": month, "subtitle": home_95 + " — " + away_club_95}
    $ fixture_95["text"] = [[None, "На табло " + live_95 + ". " + setup_95]] + duel_95["text"]
    $ fixture_95["choices"] = match_choices_95(duel_95["choices"], gs.position, state_95, round_index)
    if gs.has_flag("thrown_match_95"):
        $ fixture_95["choices"] += all_events["S95_FIXING_CHOICE"]["choices"]
    call play_event(match_eid_95, fixture_95)
    $ gs.set_flag("thrown_match_95", False)
    return

label season_1995_portugal:
    call play_event("S95_PORTUGAL")
    call league_round_1995(4, 0)
    call league_round_1995(5, 1)
    "Летом ты возвращаешься на базу после отпуска. В раздевалке висят новые номера, и за место в составе снова придётся бороться."
    call league_round_1995(9, 4)
    call league_round_1995(11, 5)
    call settle_season_income
    call play_event("PTSD_RECOVERY")
    $ gs.season_history.append({"season": 4, "league": "portugal", "arc": "adaptation", "objective_met": False})
    $ gs.season += 1
    $ gs.age += 1
    jump demo_end

label demo_end:
    scene bg default
    hide screen hud
    $ completed_seasons = gs.season - 1
    "Демо завершено. Сыграно сезонов: [completed_seasons]."
    $ final_balance = gs.attrs["money"]
    "Баланс: $[final_balance]. Голов: [gs.goals]. Вызовов в сборную: [gs.national_calls]."
    "Клуб на момент окончания демо: [gs.club]."
    if gs.has_flag("contract_terminated"):
        "Контракт расторгнут. Допуск приостановлен на [gs.ban_months] мес."
    elif gs.has_flag("european_ban"):
        "Европейский трансфер заблокирован."
    "Возраст: [gs.age]"
    "Срывы: [gs.breakdowns]"
    $ glory = gs.glory()
    $ infamy = gs.infamy()
    "Слава: [glory]. Скандалы: [infamy]."
    "Титулы: [gs.titles_league] лиг, [gs.titles_cup] кубков"
    "Спасибо за игру."
    return