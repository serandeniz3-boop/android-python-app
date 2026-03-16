from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar

from translator import translate_text, TranslationError


class ScreenTranslateScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        root = MDBoxLayout(orientation="vertical")
        root.add_widget(MDTopAppBar(title="Screen Translate"))

        scroll = ScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))

        content.add_widget(MDLabel(
            text="Telefonunda gördüğün metni buraya yapıştır, anında çevir.",
            size_hint_y=None,
            height=dp(32),
        ))

        self.source_lang = MDTextField(
            hint_text="Kaynak dil kodu (auto önerilir)",
            text="auto",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
        )
        self.target_lang = MDTextField(
            hint_text="Hedef dil kodu (örn: tr, en, de)",
            text="tr",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56),
        )
        self.input_text = MDTextField(
            hint_text="Ekrandan aldığın metin",
            multiline=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(180),
        )
        self.output_text = MDTextField(
            hint_text="Çeviri sonucu",
            multiline=True,
            readonly=True,
            mode="rectangle",
            size_hint_y=None,
            height=dp(200),
        )

        content.add_widget(self.source_lang)
        content.add_widget(self.target_lang)
        content.add_widget(self.input_text)

        row = MDBoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(56))
        row.add_widget(MDRaisedButton(text="Çevir", on_release=self.on_translate))
        row.add_widget(MDRectangleFlatButton(text="Temizle", on_release=self.on_clear))
        content.add_widget(row)

        content.add_widget(self.output_text)

        scroll.add_widget(content)
        root.add_widget(scroll)
        self.add_widget(root)

    def on_translate(self, *_):
        text = (self.input_text.text or "").strip()
        if not text:
            self.app.toast("Önce çevrilecek metni gir.")
            return

        try:
            translated = translate_text(
                text=text,
                source_lang=self.source_lang.text or "auto",
                target_lang=self.target_lang.text or "tr",
            )
        except TranslationError as exc:
            self.output_text.text = str(exc)
            return

        self.output_text.text = translated or "(çeviri gelmedi)"

    def on_clear(self, *_):
        self.input_text.text = ""
        self.output_text.text = ""
