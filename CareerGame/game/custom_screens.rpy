screen hud():
    zorder 100
    frame:
        xalign 0.98
        yalign 0.02
        xpadding 14
        ypadding 10
        background Solid("#0f0f1acc")
        vbox:
            spacing 3
            text "Возраст: [gs.age] · Сезон: [gs.season]" size 15 color "#fff"
            text "Клуб: [gs.club]" size 15 color "#fff"
            $ lg = "Высшая лига" if gs.league == "first" else "Первая лига"
            text "[lg] · место [gs.current_place]" size 14 color "#4ade80" bold True
            null height 4
            text "TEC  Техника: [gs.attrs['tec']]" size 14 color "#fff"
            text "PHY  Физика: [gs.attrs['phy']]" size 14 color "#fff"
            text "VIS  Видение: [gs.attrs['vis']]" size 14 color "#fff"
            text "COM  Хладнокровие: [gs.attrs['com']]" size 14 color "#fff"
            null height 4
            text "Стресс: [gs.stress]/100" size 13 color "#ff8888"
            bar value StaticValue(gs.stress, 100) xmaximum 220 ymaximum 12
            text "Срывы: [gs.breakdowns]/3" size 13 color "#ff6666"
            if gs.ptsd:
                text "ПТСР: важные проверки труднее" size 12 color "#fca5a5"
            if gs.trait:
                text "Черта: [TRAIT_LABELS.get(gs.trait, gs.trait)]" size 12 color "#fcd34d"

    zorder 100
    frame:
        xalign 0.98
        yalign 0.02
        xpadding 15
        ypadding 10
        background Solid("#0f0f1acc")
        vbox:
            spacing 4
            text "Возраст: [gs.age]" size 16 color "#fff"
            text "Сезон: [gs.season]" size 16 color "#fff"
            text "Клуб: [gs.club]" size 16 color "#fff"
            $ lg = "Первая лига" if gs.league == "first" else "Вторая лига"
            text "Лига: [lg]" size 16 color "#fff"
            text "Место: [gs.current_place] / 8" size 16 color "#4ade80" bold True
            null height 6
            text "Стресс: [gs.stress]/100" size 14 color "#ff6666"
            text "Срывы: [gs.breakdowns]/3" size 14 color "#ff6666"
            null height 6
            text "Хладнокровие: [gs.attrs['composure']]" size 12 color "#aaa"
            text "Репутация: [gs.attrs['rep_coach']]" size 12 color "#aaa"
            text "Медиа: [gs.attrs['media']]" size 12 color "#aaa"


screen vn_dialog(speaker, text, current, total):
    modal True
    frame:
        xalign 0.5
        yalign 0.92
        xsize 1200
        ysize 240
        background Solid("#0a0a14f0")
        padding (40, 30)
        
        vbox:
            spacing 15
            if speaker:
                text speaker size 26 bold True color "#ffcc00"
            else:
                null height 31
                
            text text size 22 color "#eee"
            
            text "▼ Нажмите, чтобы продолжить" size 14 color "#666" xalign 1.0 yalign 1.0

    button:
        xfill True
        yfill True
        action Return()
        background None


screen event_choices(event):
    modal True
    add Solid("#0f0f1a90")
    vbox:
        xalign 0.5
        yalign 0.05
        spacing 10
        text event.get("title", "") size 36 bold True xalign 0.5 color "#ffcc00"
        if event.get("subtitle"):
            text event["subtitle"] size 18 italic True xalign 0.5 color "#aaa"
    vbox:
        xalign 0.5
        yalign 0.5
        spacing 12
        for choice in event.get("choices", []):
            $ avail = is_choice_available(gs, choice)
            if choice.get("check"):
                text check_hint(choice) size 14 color "#fbbf24" xalign 0.5
            textbutton choice["text"]:
                action Return(choice)
                sensitive avail
                xsize 1000
                text_size 21
                background Solid("#1e1e30")
                hover_background Solid("#3a3a55")

screen choose_trait():
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.12
        spacing 14
        text "ВЫБЕРИ ЧЕРТУ ХАРАКТЕРА" size 36 bold True xalign 0.5 color "#ffcc00"
        text "Она немного изменит твои сильные стороны и то, как ты переживаешь сезон." size 18 xalign 0.5 color "#bbb"
        textbutton "Трудяга — +10 к физике; вечеринки утомляют вдвое сильнее" action [Function(gs.set_trait, "workhorse"), Return()]
        textbutton "Скандалист — больше агрессии и внимания прессы; вечеринки могут вызвать кризис" action [Function(gs.set_trait, "scandalist"), Return()]
        textbutton "Любитель чебуреков — +5 к хладнокровию; домашняя еда помогает восстановиться" action [Function(gs.set_trait, "cheburek_fan"), Return()]
        textbutton "Хладнокровный — +5 к COM и clutch; важные матчи меньше выматывают" action [Function(gs.set_trait, "ice_cold"), Return()]

screen choose_mode():
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.2
        spacing 18
        text "АГЕНТ СПРАШИВАЕТ, КАКОЙ КАРЬЕРЫ ТЫ ХОЧЕШЬ" size 30 bold True xalign 0.5 color "#ffcc00"
        text "«Я не боюсь боли» — реалистичный режим, проверки без скидок." size 18 xalign 0.5 color "#ddd"
        text "«Хочу наслаждаться футболом» — лёгкий режим, пороги проверок ниже." size 18 xalign 0.5 color "#ddd"
        textbutton "Я не боюсь боли" action [SetField(gs, "mode_realism", True), Function(gs.set_flag, "mode_realism", True), Return()]
        textbutton "Хочу наслаждаться футболом" action [SetField(gs, "mode_realism", False), Function(gs.set_flag, "mode_realism", False), Return()]

screen create_position():
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.15
        spacing 20
        text "КЕМ ТЫ БУДЕШЬ НА ПОЛЕ?" size 40 bold True xalign 0.5 color "#ffcc00"
        null height 30
        textbutton "Вратарь" action [SetField(gs, "position", "GK"), Return()]
        textbutton "Защитник" action [SetField(gs, "position", "DEF"), Return()]
        textbutton "Полузащитник" action [SetField(gs, "position", "MID"), Return()]
        textbutton "Нападающий" action [SetField(gs, "position", "FWD"), Return()]


screen create_nation():
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.15
        spacing 20
        text "ОТКУДА ТЫ НАЧНЁШЬ?" size 40 bold True xalign 0.5 color "#ffcc00"
        null height 30
        textbutton "Россия — РПЛ" action [SetField(gs, "nation", "RU"), Return()]


screen create_difficulty():
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.15
        spacing 20
        text "ВЫБЕРИ СВОЙ УРОВЕНЬ" size 40 bold True xalign 0.5 color "#ffcc00"
        null height 30
        textbutton "Конец второй лиги (Стресс: 0)" action [SetField(gs, "difficulty", "low2"), SetField(gs, "start_stress", 0), SetField(gs, "league", "second"), Return()]
        textbutton "Топовая команда второй лиги (Стресс: 25)" action [SetField(gs, "difficulty", "top2"), SetField(gs, "start_stress", 25), SetField(gs, "league", "second"), Return()]
        textbutton "Низ первой лиги (Стресс: 50)" action [SetField(gs, "difficulty", "low1"), SetField(gs, "start_stress", 50), SetField(gs, "league", "first"), Return()]
        textbutton "Топовая команда первой лиги (Стресс: 75)" action [SetField(gs, "difficulty", "top1"), SetField(gs, "start_stress", 75), SetField(gs, "league", "first"), Return()]


screen create_club():
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.05
        spacing 10
        text "ТВОЙ ПЕРВЫЙ КЛУБ" size 40 bold True xalign 0.5 color "#ffcc00"
        $ lg = "Первая лига" if gs.league == "first" else "Вторая лига"
        text "Лига: [lg]" size 20 xalign 0.5 color "#888"
        null height 20
        for club in clubs_data.get(gs.nation, {}).get(gs.league, []):
            if club.get("difficulty") == gs.difficulty:
                $ label_text = club["name"]
                textbutton label_text action [SetField(gs, "club", club["name"]), SetField(gs, "club_difficulty", club["difficulty"]), Return()]


screen league_table(rows):
    modal True
    add Solid("#0f0f1a")
    vbox:
        xalign 0.5
        yalign 0.04
        spacing 14
        text "ТУРНИРНАЯ ТАБЛИЦА" size 36 bold True xalign 0.5 color "#ffcc00"
        $ lg_full = "Высшая лига" if gs.league == "first" else "Первая лига"
        text "Сезон [gs.season] · [lg_full]" size 18 xalign 0.5 color "#aaa"
        frame:
            xalign 0.5
            xsize 1040
            background Solid("#0a0a14")
            padding (12, 10)
            vbox:
                spacing 2
                hbox:
                    spacing 6
                    text "№" xsize 42 text_align 0.5 color "#aaa" size 15 bold True
                    text "Команда" xsize 285 color "#aaa" size 15 bold True
                    text "И" xsize 42 text_align 0.5 color "#aaa" size 15 bold True
                    text "В" xsize 42 text_align 0.5 color "#aaa" size 15 bold True
                    text "Н" xsize 42 text_align 0.5 color "#aaa" size 15 bold True
                    text "П" xsize 42 text_align 0.5 color "#aaa" size 15 bold True
                    text "ГЗ" xsize 52 text_align 0.5 color "#aaa" size 15 bold True
                    text "ГП" xsize 52 text_align 0.5 color "#aaa" size 15 bold True
                    text "О" xsize 52 text_align 0.5 color "#aaa" size 15 bold True
                for i, row in enumerate(rows):
                    $ is_player = row["name"] == gs.club
                    $ zone_col = "#4ade80" if row["zone"] == "top" else ("#ef4444" if row["zone"] == "bottom" else "#ddd")
                    $ row_bg = Solid("#29354a") if is_player else (Solid("#151b2a") if i % 2 else Solid("#101522"))
                    frame:
                        background row_bg
                        padding (8, 6)
                        xfill True
                        hbox:
                            spacing 6
                            text "[row['place']]" xsize 42 text_align 0.5 color zone_col size 17 bold is_player
                            text "[row['name']]" xsize 285 color ("#ffcc00" if is_player else zone_col) size 17 bold is_player
                            text "[row['played']]" xsize 42 text_align 0.5 color zone_col size 16
                            text "[row['w']]" xsize 42 text_align 0.5 color zone_col size 16
                            text "[row['d']]" xsize 42 text_align 0.5 color zone_col size 16
                            text "[row['l']]" xsize 42 text_align 0.5 color zone_col size 16
                            text "[row['gf']]" xsize 52 text_align 0.5 color zone_col size 16
                            text "[row['ga']]" xsize 52 text_align 0.5 color zone_col size 16
                            text "[row['pts']]" xsize 52 text_align 0.5 color ("#ffcc00" if is_player else zone_col) size 16 bold True
        hbox:
            xalign 0.5
            spacing 28
            text "Зелёный — еврокубковая тройка" size 14 color "#4ade80"
            text "Красный — зона вылета" size 14 color "#ef4444"
        textbutton "Продолжить" action Return() xalign 0.5

