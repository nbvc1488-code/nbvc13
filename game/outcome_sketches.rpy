init python:
    class OutcomeSketch(renpy.Displayable):
        """Draws the temporary storyboard frame for a resolved choice."""

        WIDTH, HEIGHT = 790, 320
        PAPER = (228, 219, 192, 255)
        INK = (42, 53, 50, 255)
        FAINT = (167, 160, 139, 255)
        HERO = (44, 101, 87, 255)
        OTHER = (126, 69, 60, 255)

        def __init__(self, subject, **kwargs):
            super().__init__(**kwargs)
            self.subject = subject

        def render(self, width, height, st, at):
            result = renpy.Render(self.WIDTH, self.HEIGHT)
            canvas = result.canvas()
            canvas.rect(self.PAPER, (0, 0, self.WIDTH, self.HEIGHT))
            canvas.rect((211, 201, 173, 255), (15, 15, self.WIDTH - 30, self.HEIGHT - 30), 1)
            for offset in range(34, 275, 11):
                canvas.line((216, 205, 176, 255), (16, offset), (56, offset - 8), 1)
                canvas.line((216, 205, 176, 255), (self.WIDTH - 56, offset), (self.WIDTH - 16, offset - 8), 1)
            if self.subject in ("goal", "team_goal", "miss", "blocked", "concede", "save",
                                 "shot", "assist", "intercept", "pass", "tackle", "foul", "card", "train"):
                self.pitch(canvas)
            else:
                self.scene(canvas)
            return result

        def line(self, canvas, points, color=None, width=3):
            for a, b in zip(points, points[1:]):
                canvas.line(color or self.INK, a, b, width)

        def person(self, canvas, x, y, color, pose="stand"):
            skin = (182, 139, 106, 255)
            dark = (49, 55, 53, 255)
            canvas.ellipse(self.FAINT, (x - 35, y - 3, 70, 8))
            canvas.circle(skin, (x, y - 98), 13)
            canvas.circle(self.INK, (x, y - 98), 13, 2)
            self.line(canvas, [(x - 12, y - 103), (x - 6, y - 111), (x + 9, y - 109)], dark, 3)
            self.line(canvas, [(x + 5, y - 98), (x + 10, y - 96)], dark, 1)
            shirt = [(x - 15, y - 78), (x - 5, y - 85), (x + 13, y - 81),
                     (x + 13, y - 57), (x + 3, y - 49), (x - 15, y - 52)]
            canvas.polygon(color, shirt)
            canvas.polygon(self.INK, shirt, 2)
            self.line(canvas, [(x - 8, y - 71), (x + 8, y - 70)], self.PAPER, 2)
            self.line(canvas, [(x - 9, y - 49), (x + 7, y - 49)], dark, 6)
            if pose == "kick":
                self.line(canvas, [(x - 22, y - 65), (x, y - 77), (x + 23, y - 61)], color, 4)
                self.line(canvas, [(x - 24, y), (x - 5, y - 48), (x + 25, y - 36), (x + 48, y - 47)], color, 6)
            elif pose == "down":
                self.line(canvas, [(x - 33, y - 63), (x - 1, y - 76), (x + 28, y - 79)], color, 4)
                self.line(canvas, [(x - 5, y - 48), (x - 34, y - 34), (x - 62, y - 35)], color, 6)
            else:
                hands = y - 92 if pose == "raise" else y - 47
                self.line(canvas, [(x - 27, hands), (x, y - 75), (x + 26, hands)], color, 4)
                self.line(canvas, [(x - 20, y), (x - 5, y - 48), (x + 17, y)], color, 6)

        def ball(self, canvas, point):
            canvas.circle(self.PAPER, point, 10)
            canvas.circle(self.INK, point, 10, 2)
            canvas.circle(self.INK, point, 3)

        def path(self, canvas, start, end, bend=34):
            points = []
            for i in range(21):
                t = i / 20.0
                points.append((round(start[0] + (end[0] - start[0]) * t),
                               round(start[1] + (end[1] - start[1]) * t - bend * 4 * t * (1 - t))))
            for i in range(0, 20, 2):
                self.line(canvas, points[i:i+2], self.FAINT, 3)
            self.ball(canvas, end)

        def pitch(self, canvas):
            canvas.rect((209, 211, 177, 255), (39, 169, 711, 117))
            for y in range(181, 280, 24):
                canvas.rect((201, 207, 170, 255), (40, y, 709, 10))
            for y in range(198, 289, 30):
                self.line(canvas, [(40, y), (748, y)], self.FAINT, 1)
            self.line(canvas, [(51, 282), (157, 168), (643, 168), (750, 282)], self.FAINT, 2)
            kind = self.subject
            if kind in ("goal", "team_goal", "miss", "blocked", "concede", "save", "shot"):
                for x in range(530, 706, 22):
                    self.line(canvas, [(x, 65), (x + 10, 168)], self.FAINT, 1)
                for y in range(65, 170, 17):
                    self.line(canvas, [(530, y), (706, y)], self.FAINT, 1)
                self.line(canvas, [(523, 174), (523, 60), (712, 60), (712, 174)], width=5)
                self.person(canvas, 225, 249, self.OTHER if kind in ("save", "concede", "team_goal") else self.HERO, "kick")
                if kind == "team_goal":
                    self.person(canvas, 129, 266, self.HERO, "raise")
                self.person(canvas, 596, 179, self.HERO if kind in ("save", "concede") else self.OTHER,
                            "raise" if kind in ("blocked", "save") else "down")
                target = {"goal": (683, 121), "team_goal": (670, 109), "miss": (748, 110),
                          "blocked": (587, 97), "save": (608, 88), "concede": (685, 96),
                          "shot": (484, 149)}[kind]
                self.path(canvas, (276, 204), target)
            elif kind in ("card", "foul"):
                self.person(canvas, 274, 254, self.HERO, "down" if kind == "foul" else "stand")
                self.person(canvas, 521, 230, self.OTHER, "raise")
                if kind == "card":
                    canvas.rect((175, 69, 57, 255), (546, 106, 24, 35))
                    canvas.rect(self.INK, (546, 106, 24, 35), 2)
                self.ball(canvas, (393, 247))
            elif kind == "tackle":
                self.person(canvas, 362, 243, self.HERO, "down")
                self.person(canvas, 460, 239, self.OTHER)
                self.path(canvas, (418, 229), (254, 259), 6)
            else:
                self.person(canvas, 232, 254, self.HERO, "kick")
                self.person(canvas, 590, 224, self.HERO if kind != "intercept" else self.OTHER)
                if kind == "train":
                    for x in (345, 411, 490):
                        self.line(canvas, [(x, 249), (x + 10, 225), (x + 20, 249), (x, 249)], self.OTHER)
                self.path(canvas, (280, 216), (558, 222) if kind != "assist" else (621, 192), 21)

        def scene(self, canvas):
            kind = self.subject
            self.line(canvas, [(42, 251), (747, 251)], self.FAINT, 2)
            if kind in ("contract", "money", "debt", "press", "therapy", "study", "meal", "radio", "talk", "argue"):
                self.person(canvas, 203, 245, self.HERO, "raise" if kind == "argue" else "stand")
                self.person(canvas, 587, 246, self.OTHER, "raise" if kind == "argue" else "stand")
                canvas.rect(self.INK, (291, 175, 196, 13))
                self.line(canvas, [(311, 187), (311, 248), (475, 248), (475, 187)])
                if kind in ("contract", "money", "debt", "study", "therapy"):
                    canvas.rect(self.HERO if kind == "money" else self.INK, (350, 116, 85, 59), 3)
                    for y in (129, 141, 153):
                        self.line(canvas, [(363, y), (422, y)], self.FAINT, 2)
                    if kind == "debt":
                        self.line(canvas, [(351, 117), (433, 173)], self.OTHER, 4)
                elif kind == "press":
                    self.line(canvas, [(379, 175), (401, 124)])
                    canvas.circle(self.INK, (402, 117), 10)
                elif kind == "radio":
                    canvas.rect(self.INK, (348, 122, 90, 53), 3)
                    canvas.circle(self.INK, (374, 148), 13, 2)
                    self.line(canvas, [(416, 123), (440, 84)], self.INK, 2)
                elif kind == "meal":
                    for x in (328, 383, 438):
                        canvas.ellipse(self.INK, (x, 148, 43, 16), 2)
                elif kind == "argue":
                    self.line(canvas, [(376, 81), (402, 105), (388, 110), (418, 136)], self.OTHER, 5)
                else:
                    self.line(canvas, [(320, 113), (362, 113), (375, 132), (399, 132), (399, 78), (320, 78), (320, 113)])
            elif kind in ("injury", "rest", "worry"):
                self.person(canvas, 374, 230, self.HERO, "down")
                self.line(canvas, [(260, 229), (509, 229), (509, 252), (267, 252), (267, 230)])
                if kind == "injury":
                    canvas.rect(self.OTHER, (476, 75, 17, 60))
                    canvas.rect(self.OTHER, (455, 96, 59, 17))
                elif kind == "worry":
                    self.line(canvas, [(378, 70), (385, 92), (365, 101), (382, 114)], self.OTHER)
                else:
                    canvas.circle(self.INK, (491, 103), 25, 2)
            elif kind == "fish":
                self.person(canvas, 234, 235, self.HERO)
                self.line(canvas, [(258, 180), (461, 69), (536, 173), (536, 229)])
                for x in (425, 470, 515, 560):
                    self.line(canvas, [(x, 231), (x+21, 231)], self.FAINT, 2)
            elif kind == "boots":
                self.person(canvas, 226, 248, self.HERO)
                self.line(canvas, [(347, 212), (379, 193), (395, 159), (439, 166), (443, 215), (347, 215), (347, 212)], width=4)
                self.line(canvas, [(407, 226), (466, 188), (495, 185), (511, 233), (408, 233)], width=4)
            elif kind in ("travel", "leave"):
                self.person(canvas, 244, 250, self.HERO)
                canvas.rect(self.INK, (276, 205, 44, 43), 3)
                canvas.rect(self.INK, (289, 194, 18, 11), 2)
                canvas.rect(self.FAINT, (493, 57, 127, 194), 3)
                self.line(canvas, [(354, 167), (467, 167), (450, 154), (467, 167), (450, 182)], self.HERO, 4)
            else:
                self.person(canvas, 277, 249, self.HERO, "raise" if kind == "party" else "stand")
                self.person(canvas, 499, 249, self.OTHER, "raise" if kind == "party" else "stand")
                if kind == "cinema":
                    canvas.rect(self.INK, (324, 59, 145, 81), 4)
                    self.line(canvas, [(380, 81), (380, 119), (418, 100), (380, 81)], self.HERO, 3)
                else:
                    for x, y in ((346, 87), (411, 114), (447, 68)):
                        self.line(canvas, [(x, y+19), (x, y), (x+14, y+5)], self.OTHER, 3)
                        canvas.circle(self.OTHER, (x-5, y+19), 5)

    class SeasonBackdrop(renpy.Displayable):
        """Limited-palette location boards for the 1993 chapter."""

        def __init__(self, setting, **kwargs):
            super().__init__(**kwargs)
            self.setting = setting

        def render(self, width, height, st, at):
            result = renpy.Render(1280, 720)
            canvas = result.canvas()
            indoor = self.setting == "manez"
            snowy = self.setting == "snow"
            sky = (120, 138, 147) if snowy else (99, 105, 111)
            grass = (184, 193, 192) if snowy else (89, 114, 93)
            contour = (48, 62, 65)
            canvas.rect(sky, (0, 0, 1280, 720))
            if indoor:
                canvas.rect((66, 79, 87), (0, 0, 1280, 355))
                canvas.polygon((110, 121, 122), [(0, 148), (640, 24), (1280, 148), (1280, 340), (0, 340)])
                for x in range(0, 1281, 160):
                    canvas.line((164, 165, 150), (640, 28), (x, 337), 3)
                canvas.line((200, 182, 134), (80, 213), (1200, 213), 5)
                for x in range(60, 1240, 140):
                    canvas.rect((222, 207, 167), (x, 211, 31, 7))
                grass = (92, 112, 97)
            else:
                for index in range(6):
                    y = 195 + index * 22
                    shade = (80 + index*5, 87 + index*5, 88 + index*5)
                    canvas.polygon(shade, [(0, y+32), (434, y), (858, y), (1280, y+24), (1280, y+42), (0, y+48)])
                for x in (182, 1100):
                    canvas.line(contour, (x, 90), (x, 344), 6)
                    canvas.rect((210, 202, 160), (x - 28, 87, 57, 14))
                if snowy:
                    for x, y in ((50, 132), (295, 109), (487, 151), (690, 93), (855, 112), (1174, 142)):
                        canvas.circle((215, 223, 219), (x, y), 3)
                else:
                    for x in range(36, 1250, 113):
                        canvas.ellipse((145, 108, 67), (x, 300 + x % 47, 20, 8))
            canvas.polygon(grass, [(0, 720), (0, 415), (249, 347), (1018, 347), (1280, 416), (1280, 720)])
            for index in range(7):
                y = 380 + index * 42
                canvas.line((113, 131, 118) if not snowy else (155, 172, 177), (0, y), (1280, y), 2)
            line = (223, 220, 193) if not snowy else (120, 144, 152)
            canvas.line(line, (86, 718), (360, 355), 4)
            canvas.line(line, (1195, 718), (918, 355), 4)
            canvas.line(line, (206, 556), (1067, 556), 3)
            canvas.ellipse(line, (543, 520, 194, 68), 3)
            for a, b in (((571, 366), (571, 313)), ((571, 313), (709, 313)), ((709, 313), (709, 366))):
                canvas.line((230, 223, 195), a, b, 5)
            for x in range(579, 710, 15):
                canvas.line((152, 158, 145), (x, 318), (x, 365), 1)
            return result

    class SeasonPortrait(renpy.Displayable):
        """Portrait placeholders with period clothing and expression variants."""

        DESIGNS = {
            "Олег Романцев": ((52, 54, 52), (128, 54, 49), 75, False, False),
            "Виктор Прокопенко": ((111, 100, 85), (64, 84, 119), 81, False, False),
            "Валерий Овчинников": ((92, 86, 77), (66, 105, 88), 87, False, True),
            "Сергей Хусаинов": ((51, 54, 51), (54, 58, 66), 73, True, False),
        }

        def __init__(self, speaker, emotion="neutral", **kwargs):
            super().__init__(**kwargs)
            self.speaker = speaker
            self.emotion = emotion
            if self.emotion == "happy" and self.speaker != "Олег Романцев":
                self.emotion = "neutral"

        def render(self, width, height, st, at):
            result = renpy.Render(168, 168)
            canvas = result.canvas()
            hair, coat, face_width, glasses, moustache = self.DESIGNS[self.speaker]
            paper, ink, skin = (226, 216, 190), (52, 59, 56), (189, 151, 120)
            canvas.rect(paper, (0, 0, 168, 168))
            for x in range(10, 165, 14):
                canvas.line((209, 200, 176), (x, 25), (x-7, 148), 1)
            canvas.polygon(coat, [(7, 164), (17, 128), (60, 110), (109, 110), (152, 128), (161, 164)])
            canvas.polygon((237, 227, 202), [(59, 112), (84, 130), (109, 112), (102, 145), (67, 145)])
            x = (168 - face_width) // 2
            canvas.ellipse(skin, (x, 29, face_width, 93))
            canvas.ellipse(ink, (x, 29, face_width, 93), 2)
            canvas.polygon(hair, [(x, 56), (x+2, 34), (x+16, 24), (105, 24), (x+face_width, 36),
                                  (x+face_width, 56), (113, 46), (70, 41), (56, 54)])
            slope = 5 if self.emotion == "stern" else 0
            for cx, direction in ((69, 1), (100, -1)):
                canvas.line(ink, (cx-8, 65-direction*slope), (cx+8, 65+direction*slope), 2)
                canvas.circle(ink, (cx, 72), 2)
                if glasses:
                    canvas.ellipse(ink, (cx-12, 65, 24, 15), 1)
            if glasses:
                canvas.line(ink, (81, 72), (88, 72), 1)
            canvas.line((126, 93, 75), (83, 74), (78, 91), 2)
            canvas.line((126, 93, 75), (78, 91), (90, 91), 2)
            if moustache:
                canvas.line(hair, (71, 98), (99, 98), 4)
            canvas.line(ink, (72, 104), (98, 104), 2)
            if self.emotion == "happy":
                canvas.line(ink, (72, 101), (81, 108), 2)
                canvas.line(ink, (81, 108), (98, 101), 2)
            return result
