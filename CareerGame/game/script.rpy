init -1 python:
    import career_logic
    from career_logic import (
        GameState, is_choice_available, resolve_choice, is_event_available,
        apply_effects, load_events, load_clubs, generate_table,
        choice_outcome, club_start_stress, check_hint, TRAIT_LABELS
    )
    gs = GameState()
    all_events = load_events()
    clubs_data = load_clubs()

define agent = Character("Агент", color="#ffcc00")

image bg default = Solid("#0f0f1a")
image bg field = Solid("#152b15")
image bg locker = Solid("#1c1c1c")
image bg office = Solid("#2a1a1a")
image bg press = Solid("#1a2333")
image bg bar = Solid("#23182b")

label start:
    $ gs = GameState()
    scene bg default
    "Карьера."
    "История одного футболиста."
    "Начало 1992 года. Тебе 16."

    call screen create_position
    call screen create_nation
    call screen create_difficulty
    call screen create_club
    agent "Присаживаюсь рядом и говорю негромко: какой путь выбираешь?"
    agent "«Я не боюсь боли» — это путь без скидок. «Хочу наслаждаться футболом» — и проверки станут мягче."
    call screen choose_mode
    call screen choose_trait

    $ gs.age = 16
    $ gs.season = 1
    $ gs.start_stress = club_start_stress(clubs_data, gs.nation, gs.league, gs.club, gs.start_stress)
    $ gs.stress = gs.start_stress
    $ gs.update_place(clubs_data)

    show screen hud
    jump season_s1

label play_event(eid):
    $ event = all_events.get(eid)
    if event is None:
        return
    if not is_event_available(gs, event):
        return
        
    $ bg_name = event.get("bg", "default")
    scene expression "bg " + bg_name
    
    $ text_lines = event.get("text", [])
    $ i = 0
    while i < len(text_lines):
        $ pair = text_lines[i]
        call screen vn_dialog(pair[0], pair[1], i, len(text_lines))
        $ i += 1
        
    call screen event_choices(event)
    $ chosen = _return
    $ branch, effects = resolve_choice(gs, chosen)
    $ outcome_text = choice_outcome(chosen, branch)
    if outcome_text:
        call screen vn_dialog(None, outcome_text, 0, 1)
    $ gs.fired_events.append(eid)
    $ gs.update_place(clubs_data)
    
    if gs.breakdown_pending:
        call breakdown_scene
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
    scene bg locker
    "НЕРВНЫЙ СРЫВ. Первый."
    "Ты чувствуешь, как земля уходит из-под ног."
    if gs.attrs["aggression"] > 65:
        "В раздевалке ты срываешься на партнёров. Драка. Тебя отстраняют на 3 матча."
        $ gs.mod("rep_teammates", -15)
        $ gs.mod("rep_coach", -10)
        $ gs.counters["scandals_moderate"] += 1
    elif gs.attrs["media"] > 55:
        "Ты не выдерживаешь давления прессы. Скандальное интервью."
        $ gs.mod("rep_press", -20)
        $ gs.mod("media", 5)
    elif gs.attrs["professionalism"] > 60:
        "Ты сгораешь на тренировках. Врачи диагностируют перетренированность. Месяц без футбола."
        $ gs.mod("stamina", -10)
        $ gs.mod("rep_coach", -5)
    elif gs.attrs["temperament"] > 60:
        "Ты взрываешься в интервью. Клуб штрафует тебя на крупную сумму."
        $ gs.mod("rep_press", -10)
        $ gs.mod("money", -500000)
    else:
        "Ты ломаешься психологически. Врачи рекомендуют отдых. Ты теряешь форму."
        $ gs.mod("composure", -10)
        $ gs.mod("stamina", -5)
    "Ты с трудом восстанавливаешься. Это оставило след. Но ты продолжаешь."
    return

label breakdown_2:
    scene bg locker
    "НЕРВНЫЙ СРЫВ. Второй."
    "Ты уже не тот, что раньше. Восстанавливаться всё труднее."
    if gs.attrs["aggression"] > 65:
        "В пресс-центре ты бросаешься на журналиста. Скандал на весь мир."
        $ gs.mod("rep_press", -25)
        $ gs.counters["scandals_severe"] += 1
    elif gs.attrs["media"] > 55:
        "Ты публикуешь безумный пост в соцсетях. Клуб требует объяснений."
        $ gs.mod("rep_coach", -20)
        $ gs.mod("media", 10)
    elif gs.attrs["professionalism"] > 60:
        "Ты теряешь интерес к тренировкам. Тренер ставит тебя вне состава."
        $ gs.mod("rep_coach", -15)
        $ gs.mod("stamina", -15)
    elif gs.attrs["temperament"] > 60:
        "Ты снова срываешься. Драка в баре. Полиция. Клуб в шоке."
        $ gs.counters["scandals_severe"] += 1
        $ gs.mod("rep_fans", -20)
    else:
        "Ты замыкаешься. Ни с кем не разговариваешь. Семья на грани."
        $ gs.mod("rel_family", -30)
        $ gs.mod("composure", -15)
    "Все вокруг видят, что ты на грани. Ещё один срыв — и всё кончится."
    return

label bad_end:
    scene bg default
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

label calc_base:
    $ base_value = gs.get_base_strength(clubs_data)
    return

label finish_season(base_strength):
    python:
        num_teams = len(clubs_data["RU"][gs.league])
        total = sum(gs.team_modifiers)
        raw_place = round(base_strength - total / 2)
        place = max(1, min(num_teams, raw_place))
    if place <= 3:
        $ arc = "TITLE_RACE"
    elif place >= num_teams - 2:
        $ arc = "RELEGATION"
    else:
        $ arc = "MIDTABLE"

    $ table = generate_table(gs, clubs_data, gs.league, place)
    call screen league_table(table)

    $ gs.current_place = place
    $ gs.season_history.append({"season": gs.season, "place": place, "arc": arc})
    $ gs.award_league_place(place)

    if gs.league == "first" and place >= num_teams - 2:
        $ gs.league = "second"
        "Клуб вылетает во вторую лигу."
    elif gs.league == "second" and place <= 3:
        $ gs.league = "first"
        "Клуб выходит в первую лигу."

    call play_event("VACATION")
    if gs.stress > 50:
        call play_event("S1_HOME_FAMILY")
    if gs.stress > 50:
        call play_event("S1_HOME_PSYCH")
    if gs.has_flag("ptsd"):
        call play_event("PTSD_RECOVERY")

    $ gs.reset_season_modifiers()
    $ gs.age += 1
    $ gs.season += 1
    return

label season_s1:
    call play_event("S1_P1")
    call play_event("S1_P2")
    call play_event("S1_C1")
    call play_event("S1_C2")
    
    # Вместо одного S1_C3 вызываем 4 разных события (сработает только одно)
    call play_event("S1_ACT_GK")
    call play_event("S1_ACT_DEF")
    call play_event("S1_ACT_MID")
    call play_event("S1_ACT_FWD")
    
    call play_event("S1_HIST_GK")
    call play_event("S1_HIST_ZENIT")
    call play_event("S1_HIST_SCANDAL")
    call play_event("S1_HIST_ROTOR")
    call play_event("S1_HIST_NEW_LEAGUE")
    call play_event("S1_HIST_VERETINOV")
    call play_event("S1_HIST_PISTOL")
    call play_event("S1_E1")
    call play_event("S1_C4")
    call play_event("S1_C5")
    call play_event("S1_C6")
    call play_event("S1_C7")
    call play_event("S1_C8")
    call calc_base
    call finish_season(base_value)
    jump demo_end

label demo_end:
    scene bg default
    "Демо-версия завершена."
    "Ты прошёл первый сезон 1992 года."
    "Возраст: [gs.age]"
    "Срывы: [gs.breakdowns]"
    "Glory: [gs.glory()]"
    "Infamy: [gs.infamy()]"
    "Титулы: [gs.titles_league] лиг, [gs.titles_cup] кубков"
    "Спасибо за игру."
    return