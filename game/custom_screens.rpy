default persistent.career_read_text = set()
default career_scene_stats = False
default persistent.career_panel_transparency = 12
default persistent.career_hud_collapsed = False
default career_art_only = False

init python:
    CAREER_MONTHS = ("январь", "февраль", "март", "апрель", "май", "июнь",
                     "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь")

    def career_outcome_art(sketch, event):
        aliases = {"assist": "pass", "train": "training", "miss": "miss_wide"}
        asset = aliases.get(sketch, sketch)
        if sketch == "goal" and gs.position in ("DEF", "MID"):
            asset = "goal_" + gs.position.lower()
        if event["id"] in ("S4_TRANSFER_EUROPE", "SQUAD_EXILE_TRANSFER") and gs.league == "portugal":
            asset = "transfer"
        if event["id"] == "NEW_WAGE_DELAY":
            asset = "debt"
        return asset

    def career_panel_color(color="#101b19"):
        opacity = 1.0 - persistent.career_panel_transparency / 100.0
        return Color(color).replace_opacity(opacity)

    def stress_color(fraction):
        green, amber, red = (63, 183, 129), (247, 183, 76), (232, 82, 79)
        start, end = (green, amber) if fraction < 0.5 else (amber, red)
        amount = (fraction * 2) % 1 if fraction < 1 else 1
        return "#{:02x}{:02x}{:02x}".format(*(round(a + (b - a) * amount) for a, b in zip(start, end)))

    stress_gradient = Composite((220, 12), *[layer for index in range(44)
        for layer in ((index * 5, 0), Solid(stress_color(index / 43), xysize=(5, 12)))])


style vscrollbar:
    xsize 8
    base_bar Solid("#22332c")
    thumb Solid("#729485")
    hover_thumb Solid("#a2bdb0")
    unscrollable "hide"

style career_control is button:
    xfill True
    padding (16, 11)
    background Solid("#263832")
    hover_background Solid("#385348")
    insensitive_background Solid("#202925")

style career_control_text is button_text:
    font gui.interface_text_font
    size 19
    color "#f3eee3"
    hover_color "#ffffff"
    insensitive_color "#98a39e"

style career_scene_choice is career_control:
    hover_background Solid("#385348df")

style career_scene_choice_text is career_control_text:
    outlines [(2, "#0c1514", 0, 0)]

style career_primary is career_control:
    background Solid("#e8c782")
    hover_background Solid("#f8daa1")

style career_primary_text is career_control_text:
    color "#1b211b"
    hover_color "#1b211b"
    bold True

style career_link is button:
    padding (0, 5)
    background None
    hover_background None

style career_link_text is career_control_text:
    size 14
    color "#b9c8bf"
    hover_color "#f8daa1"

screen career_text_progress(line):
    if not career_art_only:
        if renpy.is_skipping() and (_preferences.skip_unseen or line in persistent.career_read_text or config.skipping == "fast"):
            timer 0.06 action Return() modal True
        elif not renpy.is_skipping() and _preferences.afm_enable and _preferences.afm_time > 0:
            $ wait = max(0.35, _preferences.afm_time * (config.afm_bonus + len(line)) / config.afm_characters)
            timer wait action Return() modal True

screen career_art_control(show_stats=True, focus_art=False):
    key "K_h" action ToggleVariable("career_art_only")
    key "K_j" action ShowMenu("history")
    frame:
        xpos 80
        ypos 18
        padding (12, 3)
        background Solid("#101b19da")
        textbutton ("Вернуть интерфейс" if career_art_only else "Только иллюстрация"):
            style "career_link"
            action ToggleVariable("career_art_only")

    if show_stats and not career_art_only and renpy.get_screen("hud"):
        use career_hud_toggle(focus_art)

screen career_hud_toggle(focus_art=False):
    frame:
        xalign 0.975
        ypos 18
        padding (12, 3)
        background Solid("#101b19da")
        textbutton ("Свернуть статистику" if (career_scene_stats if focus_art else not persistent.career_hud_collapsed) else "Статистика"):
            style "career_link"
            action (ToggleVariable("career_scene_stats") if focus_art else ToggleField(persistent, "career_hud_collapsed"))

screen hud():
    zorder 10
    if not career_art_only and not any(renpy.get_screen(name) for name in ("vn_dialog", "event_choices", "event_outcome")):
        use career_hud_toggle()

    $ active_scene = next((name for name in ("vn_dialog", "event_choices") if renpy.get_screen(name)), None)
    $ focus_art = bool(active_scene and renpy.get_screen_variable("focus_art", screen=active_scene))
    if not career_art_only and (career_scene_stats if focus_art else not persistent.career_hud_collapsed):
        frame:
            xalign 0.975
            ypos 58
            xsize 270
            padding (17, 14)
            background Solid("#101b19f4")
            vbox:
                spacing 7
                text gs.club size 19 bold True color "#f6f1e5"
                $ year = 1991 + gs.season
                if gs.league == "portugal":
                    text "[year] · [gs.age] лет · Лиссабон" size 13 color "#bacbc2"
                else:
                    text "[year] · [gs.age] лет · место [gs.current_place]" size 13 color "#bacbc2"
                text "Баланс  $[gs.attrs['money']]" size 13 color "#e8c782"
                if gs.season <= 4 and not gs.has_flag("contract_terminated") and gs.trait != "investor" and gs.payroll_month < 12:
                    $ next_pay = calculate_salary(gs.club)
                    $ next_month = CAREER_MONTHS[gs.payroll_month]
                    text "Оклад $[next_pay] · [next_month]" size 12 color "#bacbc2"
                if gs.season <= 4:
                    text "На жизнь · $[MONTHLY_LIVING_COST]/мес." size 12 color "#bacbc2"
                if gs.salary_debt:
                    text "Клуб должен $[gs.salary_debt]" size 12 color "#f0a79b"
                text "Тренер · [gs.attrs['rep_coach']] / 100" size 13 color "#bacbc2"
                if gs.coach_review_due:
                    $ review_status = "Решение по заявке" if active_scene == "event_choices" and renpy.get_screen_variable("event", screen=active_scene)["id"] == "COACH_REVIEW_RETURN" else "Просмотр после ближайшего тура"
                    text review_status size 13 color "#e8c782"
                if gs.has_flag("not_in_squad") or gs.has_flag("squad_exile"):
                    text "Вне заявки" size 13 color "#f0a79b"
                if gs.suspension_matches:
                    text "Дисквалификация · [gs.suspension_matches] матч." size 13 color "#f0a79b"
                if gs.ban_months:
                    text "Отстранение · [gs.ban_months] мес." size 13 color "#f0a79b"
                add Solid("#385048") xysize (236, 1)
                for label, stat in (("Техника", "tec"), ("Физика", "phy"), ("Видение", "vis"), ("Хладнокровие", "com")):
                    fixed:
                        xysize (236, 17)
                        text label size 14 color "#cbd8cf"
                        text str(gs.attrs[stat]) xalign 1.0 size 14 bold True color "#f6f1e5"
                null height 1
                fixed:
                    xysize (236, 18)
                    text "Стресс" size 14 color "#f6f1e5"
                    text "[gs.stress] / 100" xalign 1.0 size 14 color stress_color(gs.stress / 100.0)
                fixed:
                    xysize (220, 12)
                    add Solid("#2a3b34")
                    if gs.stress:
                        add Transform(stress_gradient, crop=(0, 0, max(1, round(220 * gs.stress / 100)), 12))
                if gs.stress_warning:
                    text "На пределе · пора восстановиться" size 13 color "#f0a79b"
                text "Срывы [gs.breakdowns] / 3" size 13 color "#bacbc2"
                $ press_color = "#80cda2" if gs.rumor_score > 0 else ("#f0a79b" if gs.rumor_score < 0 else "#bacbc2")
                fixed:
                    xysize (236, 17)
                    text "Пресса" size 13 color "#bacbc2"
                    text "{:+d}".format(gs.rumor_score) xalign 1.0 size 13 color press_color
                fixed:
                    xysize (220, 5)
                    add Solid("#293b34")
                    if gs.rumor_score:
                        $ extent = max(1, round(abs(gs.rumor_score) * 1.1))
                        add Solid(press_color) xpos (110 if gs.rumor_score > 0 else 110 - extent) xysize (extent, 5)
                    add Solid("#c5cfc9") xpos 109 xysize (2, 5)
                if gs.ptsd:
                    text "ПТСР · сложнее сохранять спокойствие" size 13 color "#f0a79b"
                if gs.fatigue:
                    text "Усталость [gs.fatigue]" size 13 color "#e8c782"
                if gs.injury_months:
                    text "Восстановление · [gs.injury_months] мес." size 13 color "#f0a79b"

screen vn_dialog(speaker, text, current, total, portrait=None, focus_art=False):
    modal True
    $ portrait = career_portrait(speaker) if portrait is None else portrait
    key "dismiss" action If(career_art_only, SetVariable("career_art_only", False), Return())
    on "hide" action SetVariable("career_art_only", False)
    if not career_art_only:
        button:
            xfill True
            yfill True
            action Return()
            background None
        frame:
            xalign 0.5
            yalign 0.94
            xsize 1120
            background Solid(career_panel_color())
            padding (24, 18)
            hbox:
                spacing 21
                if portrait:
                    add Transform(portrait, xysize=(104, 104), fit="cover")
                vbox:
                    spacing 8
                    xsize (941 if portrait else 1070)
                    if speaker:
                        text speaker size 15 bold True color "#e8c782"
                    text text font gui.dialogue_text_font size 24 color "#f6f1e5" outlines [(2, "#0c1514", 0, 0)] line_spacing 5
                    hbox:
                        xalign 1.0
                        spacing 16
                        if total > 1:
                            text "[current + 1] / [total]" size 13 color "#aabbb1" yalign 0.5
                        textbutton "Далее  ›" action Return() style "career_link"

    use career_text_progress(text)
    use career_art_control(focus_art=focus_art)

screen event_choices(event, focus_art=False):
    modal True
    on "hide" action SetVariable("career_art_only", False)
    if career_art_only:
        key "dismiss" action SetVariable("career_art_only", False)
    else:
        frame:
            xalign 0.5
            yalign 0.94
            xsize 1120
            padding (22, 16)
            background Solid(career_panel_color())
            vbox:
                spacing 8
                text event["title"] font gui.career_heading_font size 29 color "#f6f1e5" outlines [(2, "#0c1514", 0, 0)]
                if event.get("subtitle"):
                    text event["subtitle"] size 14 color "#e8c782"
                for choice in event["choices"]:
                    $ req = choice.get("requires", {})
                    if is_choice_relevant(gs, choice):
                        $ available = is_choice_available(gs, choice)
                        button:
                            style "career_scene_choice"
                            background Solid(career_panel_color("#263832"))
                            insensitive_background Solid(career_panel_color("#202925"))
                            action Return(choice)
                            sensitive available
                            padding (14, 7)
                            vbox:
                                spacing 3
                                text choice["text"] style "career_scene_choice_text"
                                if not available:
                                    if "money" in req and gs.attrs["money"] < req["money"]:
                                        text "Не хватает денег" size 13 color "#dfb7a3" outlines [(1, "#0c1514", 0, 0)]
                                    elif "personal_training" in req:
                                        text "Нужно индивидуальное занятие по амплуа" size 13 color "#dfb7a3" outlines [(1, "#0c1514", 0, 0)]
                                    elif "new_item" in req and req["new_item"] in gs.inventory:
                                        text "Уже в коллекции" size 13 color "#dfb7a3" outlines [(1, "#0c1514", 0, 0)]
                                    else:
                                        text "Этот вариант пока недоступен" size 13 color "#dfb7a3" outlines [(1, "#0c1514", 0, 0)]
                                elif choice.get("check"):
                                    text check_hint(choice, gs, event) size 13 color "#d8c99e" outlines [(1, "#0c1514", 0, 0)]
    use career_art_control(focus_art=focus_art)

screen press_snippet(headline, tone):
    modal True
    use career_text_progress(headline)
    key "dismiss" action Return()
    frame:
        xalign 0.5
        yalign 0.48
        xsize 742
        padding (31, 26)
        background Solid("#e7dcc0")
        vbox:
            xfill True
            spacing 13
            text "ФУТБОЛ · [CAREER_MONTHS[gs.month - 1]] [1991 + gs.season]" size 16 color "#425047"
            add Solid("#8d8267") xysize (680, 1)
            text headline font gui.career_heading_font size 33 color ("#752f2b" if tone == "critical" else "#25352e") line_spacing 5
            textbutton "Отложить газету" action Return() style "career_control" xalign 1.0

screen event_outcome(event, outcome, sketch, score, bonus=0):
    zorder 20
    modal True
    on "hide" action SetVariable("career_art_only", False)
    key "dismiss" action If(career_art_only, SetVariable("career_art_only", False), Return())
    $ asset = career_outcome_art(sketch, event)
    $ path = "images/career8/" + asset + ".jpg"
    add Transform(path, fit="cover", xysize=(config.screen_width, config.screen_height))
    if not career_art_only:
        add Solid("#101b19b0") yalign 1.0 ysize 28
        frame:
            xalign 0.5
            yalign 0.94
            xsize 1120
            padding (22, 16)
            background Solid(career_panel_color())
            vbox:
                xfill True
                spacing 7
                if score:
                    text "{}  {}  {}".format(event["home"], score, event["away"]) size 19 bold True color "#e8c782" outlines [(2, "#0c1514", 0, 0)]
                text outcome font gui.dialogue_text_font size 24 color "#f6f1e5" outlines [(2, "#0c1514", 0, 0)] line_spacing 4
                if bonus:
                    text "Премия за победу  +$[bonus]" size 14 color "#80cda2"
                if gs.stress_warning and not prior_warning:
                    text "Ты на пределе. Следующий тяжёлый эпизод может привести к срыву." size 15 color "#f0a79b"
                if gs.attrs["rep_coach"] != prior_trust:
                    text "Доверие тренера {:+d} · теперь {} / 100".format(gs.attrs["rep_coach"] - prior_trust, gs.attrs["rep_coach"]) size 14 color "#e8c782"
                if event.get("historical_note"):
                    text event["historical_note"] size 14 color "#b7c6bd"
                textbutton "Далее  ›" action Return() style "career_link" xalign 1.0
    use career_text_progress(outcome)
    use career_art_control(show_stats=False)


screen career_inventory():
    tag menu
    use game_menu("Вещи", scroll="viewport"):
        vbox:
            spacing 18
            text "Расходы на жизнь · $[gs.living_spent] за карьеру" size 17 color "#e8c782"
            if gs.family_support:
                text "Помощь семье · $[gs.family_support]" size 17 color "#e8c782"
            if not gs.inventory:
                text "Здесь появятся покупки, подарки и памятные вещи из матчей." size 23 color "#bacbc2"
            for item, detail in gs.inventory.items():
                $ name, image_id = ITEMS[item]
                hbox:
                    spacing 22
                    $ path = "images/career8/" + image_id + ".jpg"
                    if renpy.loadable(path):
                        add Transform(path, fit="cover", xysize=(156, 96))
                    vbox:
                        spacing 6
                        text name size 23 color "#f6f1e5"
                        text "{} · {}".format(detail["year"], detail["place"]) size 17 color "#e8c782"
                        text detail["scene"] size 17 color "#bacbc2"
                        if detail["gifted"]:
                            text "Подарено" size 15 color "#80cda2"

screen choose_trait(event=None):
    modal True
    $ legacy_call = event is None
    $ event = event or all_events["CAREER_TRAIT"]
    add Solid("#101c19")
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 18
        text "Черта характера" font gui.career_heading_font size 42 xalign 0.5 color "#e8c782"
        grid 3 4:
            spacing 12
            for choice in event["choices"]:
                button:
                    xsize 366
                    ysize 110
                    padding (14, 10)
                    background Solid("#263832")
                    hover_background Solid("#385348")
                    action ([Function(apply_effects, gs, choice["effects"]), Return()] if legacy_call else Return(choice))
                    vbox:
                        spacing 6
                        text choice["text"] size 21 color "#e8c782"
                        text choice["description"] size 16 color "#eee"

screen choose_mode(event=None):
    modal True
    $ legacy_call = event is None
    $ event = event or all_events["CAREER_MODE"]
    add Solid("#101c19")
    hbox:
        xalign 0.5
        yalign 0.5
        spacing 46
        $ portrait = career_portrait("Миро Райо")
        frame:
            background Solid("#1e2632")
            padding (0, 0)
            xysize (268, 268)
            if portrait:
                add Transform(portrait, fit="cover", xysize=(268, 268))
            else:
                text "Миро Райо" xalign 0.5 yalign 0.5 size 24 color "#d2dae3"
        vbox:
            spacing 20
            xsize 655
            text "Режим карьеры" font gui.career_heading_font size 43 color "#f6f1e5"
            text event["text"][0][1] font gui.dialogue_text_font size 21 color "#ddd"
            for choice in event["choices"]:
                $ mode = "Реализм" if choice["effects"]["mode_realism"] else "Сюжет"
                button:
                    style "career_control"
                    action ([Function(apply_effects, gs, choice["effects"]), Return()] if legacy_call else Return(choice))
                    vbox:
                        spacing 4
                        text mode style "career_control_text" bold True
                        text ("Проверки требовательнее, ошибки обходятся дороже." if choice["effects"]["mode_realism"] else "Проверки мягче, больше пространства для ошибок.") size 16 color "#c4d0c9"

screen career_setup(title, detail, back=False):
    add Solid("#101c19")
    vbox:
        xpos 135
        ypos 61
        xsize 1010
        spacing 13
        text title font gui.career_heading_font size 46 color "#f6f1e5"
        text detail size 17 color "#b8c8bf"
        null height 12
        transclude
        if back:
            textbutton "‹ Назад" action Return("back") style "career_link"

screen create_position():
    modal True
    use career_setup("Позиция на поле", "Позиция влияет на эпизоды, в которых ты участвуешь."):
        grid 2 2:
            spacing 12
            for code, name, detail in (
                ("GK", "Вратарь", "Лови удары и руководи обороной."),
                ("DEF", "Защитник", "Останавливай атаки и страхуй партнёров."),
                ("MID", "Полузащитник", "Управляй темпом и ищи свободные зоны."),
                ("FWD", "Нападающий", "Выбирай момент для удара и завершай атаки.")
            ):
                button:
                    style "career_control"
                    xysize (499, 100)
                    action [SetField(gs, "position", code), Return()]
                    vbox:
                        spacing 6
                        text name style "career_control_text" bold True
                        text detail size 16 color "#c4d0c9"

screen create_nation():
    modal True
    use career_setup("Место старта", "Первый сезон проходит в России."):
        textbutton "Россия" action [SetField(gs, "nation", "RU"), Return()] style "career_primary"

screen create_difficulty():
    modal True
    use career_setup("Стартовая лига", "Выбери группу клубов. Сложность игровых проверок задаётся отдельно.", back=True):
        grid 2 2:
            spacing 12
            for league, tier, level, title, stress in (
                ("first", "top1", "Высшая лига", "Фавориты", 75),
                ("first", "low1", "Высшая лига", "Остальные клубы", 50),
                ("second", "top2", "Первая лига", "Лидеры", 25),
                ("second", "low2", "Первая лига", "Аутсайдеры", 0)
            ):
                button:
                    style "career_control"
                    xysize (499, 100)
                    action [SetField(gs, "league", league), SetField(gs, "difficulty", tier), SetField(gs, "start_stress", stress), Return()]
                    vbox:
                        spacing 6
                        text title style "career_control_text" bold True
                        text level size 16 color "#e8c782"

screen create_club():
    modal True
    $ league = "Высшая лига" if gs.league == "first" else "Первая лига"
    use career_setup("Первый клуб", league + " · сравни стартовый стресс и выбери команду.", back=True):
        viewport:
            xysize (1010, 402)
            mousewheel True
            draggable True
            pagekeys True
            scrollbars "vertical"
            vbox:
                spacing 7
                for club in clubs_data.get(gs.nation, {}).get(gs.league, []):
                    if club.get("difficulty") == gs.difficulty:
                        button:
                            style "career_control"
                            action [SetField(gs, "club", club["name"]), SetField(gs, "club_difficulty", club["difficulty"]), Return()]
                            fixed:
                                xysize (920, 25)
                                text club["name"] style "career_control_text"
                                text "Стресс {}".format(min(55, club["start_stress"] * 3 // 4)) xalign 1.0 yalign 0.5 size 16 color "#e8c782"

screen league_columns(values, foreground, position_color=None, heading=False, player=False):
    hbox:
        for index, (value, width) in enumerate(zip(values, (52, 314, 76, 76, 76, 76, 88, 88, 96))):
            fixed:
                xysize (width, 32)
                text str(value):
                    xalign (0.0 if index == 1 else 0.5)
                    yalign 0.5
                    color (position_color if index == 0 and position_color else foreground)
                    bold (heading or player or index == 8)
                    size (14 if heading else 17)

screen league_table(rows, transition=False):
    modal True
    zorder 20
    add Solid("#101c19")
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 12
        text ("Переходной турнир" if transition else "Турнирная таблица") font gui.career_heading_font size 42 xalign 0.5 color "#e8c782"
        $ lg_full = "Высшая лига" if gs.league == "first" else "Первая лига"
        $ year = 1991 + gs.season
        $ league_caption = "Москва · ноябрь — декабрь" if transition else lg_full
        if not transition and gs.season == 2 and gs.league == "second":
            $ league_caption = league_caption + " · " + gs.zone_1993
        text "[year] · [league_caption]" size 18 xalign 0.5 color "#aaa"
        frame:
            xalign 0.5
            xsize 1002
            background Solid("#0a0a14")
            padding (10, 8)
            vbox:
                use league_columns(("№", "Команда", "И", "В", "Н", "П", "ГЗ", "ГП", "О"), "#aeb9c8", heading=True)
                viewport:
                    ysize 448
                    mousewheel True
                    draggable True
                    scrollbars "vertical"
                    vbox:
                        spacing 2
                        for i, row in enumerate(rows):
                            if gs.season == 1 and gs.league == "first" and i in (0, 8):
                                text ("Чемпионская группа" if i == 0 else "Группа за сохранение места") xoffset 12 size 14 color "#aeb9c8"
                            $ is_player = row["name"] == gs.club
                            $ zone_color = {"top": "#4ade80", "bottom": "#ef6060", "playoff": "#e8c782"}.get(row["zone"], "#ddd")
                            $ row_color = "#252016" if is_player else zone_color
                            $ position_color = {"top": "#165331", "bottom": "#7c2525"}.get(row["zone"], row_color) if is_player else zone_color
                            $ row_bg = "#e4bd50" if is_player else ("#151b2a" if i % 2 else "#101522")
                            frame:
                                background Solid(row_bg)
                                padding (0, 0)
                                use league_columns(tuple(row[key] for key in ("place", "name", "played", "w", "d", "l", "gf", "ga", "pts")), row_color, position_color, player=is_player)
        hbox:
            xalign 0.5
            spacing 28
            if transition:
                text "Зелёный — путёвка в Высшую лигу" size 14 color "#4ade80"
            elif gs.league == "first":
                text "Зелёный — тройка лидеров" size 14 color "#4ade80"
                if gs.season == 2:
                    text "Золотой — переходной турнир" size 14 color "#e8c782"
                text "Красный — прямой вылет" size 14 color "#ef6060"
            else:
                text ("Зелёный — победитель зоны" if gs.season == 2 else "Зелёный — повышение") size 14 color "#4ade80"
        textbutton "Продолжить":
            action Return()
            xalign 0.5
            padding (18, 6)
            text_idle_color "#f4f6f8"
            background Solid("#202936")
            hover_background Solid("#364453")
