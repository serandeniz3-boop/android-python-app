from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from lessons import LESSONS
from storage import load_progress, save_progress, reset_progress
from helpers import safe_toast
from config import LEVEL_XP, LESSON_XP, UNIT_BONUS_XP, QUIZ_BASE_XP, QUIZ_MAX_TRIES, QUIZ_STREAK_CAP, QUIZ_STREAK_BONUS_PER
from ui_screens import LessonListScreen, LessonScreen, ProfileScreen, IntroScreen

class PythonOgrenApp(MDApp):
    LEVEL_XP = LEVEL_XP
    QUIZ_MAX_TRIES = QUIZ_MAX_TRIES

    def build(self):
        self.progress = load_progress()
        self.sm = ScreenManager(transition=SlideTransition())
        self.list_screen = LessonListScreen(self, name="list")
        self.intro_screen = IntroScreen(self, name="intro")
        self.lesson_screen = LessonScreen(self, name="lesson")
        self.profile_screen = ProfileScreen(self, name="profile")
        self.sm.add_widget(self.list_screen)
        self.sm.add_widget(self.intro_screen)
        self.sm.add_widget(self.lesson_screen)
        self.sm.add_widget(self.profile_screen)
        return self.sm

    def toast(self, msg: str):
        safe_toast(msg)

    def save(self):
        save_progress(self.progress)

    def reset(self):
        reset_progress()
        self.progress = load_progress()

    def units(self):
        return sorted(set(l.unit for l in LESSONS))

    def unit_lessons(self, unit: int):
        ls = [l for l in LESSONS if l.unit == unit]
        return sorted(ls, key=lambda x: x.order)

    def max_unlocked_unit(self) -> int:
        completed_units = set(self.progress.get("completed_units", []))
        u = 1
        while u in completed_units:
            u += 1
        return u

    def is_unit_completed(self, unit: int) -> bool:
        completed = set(self.progress.get("completed_lessons", []))
        lessons = self.unit_lessons(unit)
        if not lessons:
            return False
        return all(l.id in completed for l in lessons)

    def go_list(self):
        self.sm.current = "list"

    def open_profile(self):
        self.sm.current = "profile"

    def open_intro(self, lesson):
        if lesson is None:
            self.go_list()
            return
        self.intro_screen.load_lesson(lesson)
        self.sm.current = "intro"

    def open_lesson(self, lesson):
        self.lesson_screen.load_lesson(lesson)
        self.sm.current = "lesson"

    def open_next_lesson(self, current_id: str):
        all_sorted = sorted(LESSONS, key=lambda l: (l.unit, l.order))
        idx = next((i for i, l in enumerate(all_sorted) if l.id == current_id), None)
        if idx is None:
            self.toast("Sonraki ders bulunamadı.")
            return
        max_u = self.max_unlocked_unit()
        for j in range(idx + 1, len(all_sorted)):
            nxt = all_sorted[j]
            if nxt.unit <= max_u:
                self.open_intro(nxt)
                return
        self.toast("Bu kadar. (Şimdilik)")

    def mark_lesson_done(self, lesson):
        completed = set(self.progress.get("completed_lessons", []))
        first_time = lesson.id not in completed
        if not first_time:
            return False
        completed.add(lesson.id)
        self.progress["completed_lessons"] = sorted(completed)
        self.progress["xp"] = int(self.progress.get("xp", 0)) + int(LESSON_XP)
        self.progress["coins"] = int(self.progress.get("coins", 0)) + 5

        if self.is_unit_completed(lesson.unit):
            cu = set(self.progress.get("completed_units", []))
            if lesson.unit not in cu:
                cu.add(lesson.unit)
                self.progress["completed_units"] = sorted(cu)
                self.progress["xp"] = int(self.progress.get("xp", 0)) + int(UNIT_BONUS_XP)
                self.progress["coins"] = int(self.progress.get("coins", 0)) + 20

        self.save()
        return True

    def is_quiz_done(self, lesson_id: str) -> bool:
        return lesson_id in set(self.progress.get("quiz_completed", []))

    def mark_quiz_done(self, lesson_id: str):
        done = set(self.progress.get("quiz_completed", []))
        done.add(lesson_id)
        self.progress["quiz_completed"] = sorted(done)
        self.save()

    def quiz_add_bonus(self) -> int:
        self.progress["quiz_streak"] = int(self.progress.get("quiz_streak", 0)) + 1
        streak = int(self.progress["quiz_streak"])
        streak_bonus = min(QUIZ_STREAK_CAP, streak) * int(QUIZ_STREAK_BONUS_PER)
        bonus = int(QUIZ_BASE_XP) + int(streak_bonus)
        self.progress["xp"] = int(self.progress.get("xp", 0)) + int(bonus)
        self.save()
        return int(bonus)

    def quiz_reset_streak(self):
        self.progress["quiz_streak"] = 0
        self.save()
