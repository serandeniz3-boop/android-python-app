from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager

from helpers import safe_toast
from screen_translate_ui import ScreenTranslateScreen


class PythonOgrenApp(MDApp):
    def build(self):
        self.sm = ScreenManager()
        self.translate_screen = ScreenTranslateScreen(self, name="translate")
        self.sm.add_widget(self.translate_screen)
        return self.sm

    def toast(self, msg: str):
        safe_toast(msg)
