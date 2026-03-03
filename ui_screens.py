from typing import Optional, List

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.button import MDRaisedButton, MDRectangleFlatButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog

from helpers import get_progressbar_class
from engine import run_user_code
from quiz_ui import open_quiz_dialog
from shop_data import AVATARS

ProgressBarWidget = get_progressbar_class()


def calc_level(xp: int, level_xp: int) -> int:
    return max(1, (xp // level_xp) + 1)


def level_progress(xp: int, level_xp: int):
    lv = calc_level(xp, level_xp)
    base = (lv - 1) * level_xp
    in_lv = xp - base
    return lv, in_lv, level_xp


class LessonListScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.hide_locked = True

        root = MDBoxLayout(orientation="vertical")

        bar = MDTopAppBar(
            title="Python Öğren (Offline)",
            right_action_items=[["account", lambda _x: self.app.open_profile()]],
        )
        try:
            bar.anchor_title = "left"
        except Exception:
            pass
        try:
            bar.title_align = "left"
        except Exception:
            pass
        root.add_widget(bar)

        self.top_card = MDCard(padding=dp(16), size_hint_y=None, height=dp(110))
        top_box = MDBoxLayout(orientation="vertical", spacing=dp(8))
        self.top_label = MDLabel(text="", markup=True, size_hint_y=None, height=dp(24))
        self.top_bar = ProgressBarWidget(value=0, max=self.app.LEVEL_XP) if ProgressBarWidget else None
        top_box.add_widget(self.top_label)
        if self.top_bar:
            top_box.add_widget(self.top_bar)
        self.top_card.add_widget(top_box)
        root.add_widget(self.top_card)

        filter_row = MDBoxLayout(
            orientation="horizontal",
            padding=(dp(16), dp(10), dp(16), dp(10)),
            spacing=dp(12),
            size_hint_y=None,
            height=dp(56),
        )

        self.search = MDTextField(
            hint_text="Ders ara (örn: print, if)",
            mode="rectangle",
            size_hint_x=0.72,
        )
        self.search.bind(text=lambda *_: self.build_list())

        self.hide_btn = MDRectangleFlatButton(
            text="Kilitli gizle: Açık",
            size_hint_x=0.28,
            on_release=self.toggle_hide_locked,
        )

        filter_row.add_widget(self.search)
        filter_row.add_widget(self.hide_btn)
        root.add_widget(filter_row)

        scroll = ScrollView()
        self.box = MDBoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint_y=None,
        )
        self.box.bind(minimum_height=self.box.setter("height"))
        scroll.add_widget(self.box)
        root.add_widget(scroll)

        self.add_widget(root)

    def on_pre_enter(self, *args):
        self.refresh_top()
        self.build_list()

    def refresh_top(self):
        xp = int(self.app.progress.get("xp", 0))
        lv, in_lv, to_next = level_progress(xp, self.app.LEVEL_XP)
        self.top_label.text = f"[b]Level:[/b] {lv}    [b]XP:[/b] {xp}    [b]Bu level:[/b] {in_lv}/{to_next}"
        if self.top_bar:
            self.top_bar.max = to_next
            self.top_bar.value = in_lv

    def toggle_hide_locked(self, *_):
        self.hide_locked = not self.hide_locked
        state = "Açık" if self.hide_locked else "Kapalı"
        self.hide_btn.text = f"Kilitli gizle: {state}"
        self.build_list()

    def build_list(self):
        self.box.clear_widgets()
        self.refresh_top()

        completed = set(self.app.progress.get("completed_lessons", []))
        max_unlocked_unit = self.app.max_unlocked_unit()

        query = (self.search.text or "").strip().lower()
        hide_locked = bool(self.hide_locked)

        self.box.add_widget(MDLabel(
            text=f"[b]Açık Bölüm:[/b] {max_unlocked_unit}",
            markup=True,
            size_hint_y=None,
            height=dp(32),
        ))

        for u in self.app.units():
            ul = self.app.unit_lessons(u)
            done = sum(1 for l in ul if l.id in completed)
            total = len(ul)
            is_unit_locked = u > max_unlocked_unit
            lock_tag = " 🔒" if is_unit_locked else ""

            self.box.add_widget(MDLabel(
                text=f"[b]Bölüm {u}:[/b] {done}/{total}{lock_tag}",
                markup=True,
                size_hint_y=None,
                height=dp(28),
            ))

            visible_any = False
            for lesson in ul:
                is_done = lesson.id in completed
                is_locked = lesson.unit > max_unlocked_unit

                if hide_locked and is_locked:
                    continue
                if query and query not in (lesson.title or "").lower():
                    continue

                visible_any = True
                prefix = "🔒 " if is_locked else ("✅ " if is_done else "")
                btn = MDRectangleFlatButton(
                    text=f"{prefix}B{lesson.unit}-{lesson.order}: {lesson.title}",
                    size_hint=(1, None),
                    height=dp(48),
                )

                if not is_locked:
                    btn.bind(on_release=lambda _x, l=lesson: self.app.open_intro(l))
                else:
                    btn.bind(on_release=lambda _x: self.app.toast("🔒 Bu bölüm kilitli. Öncekini bitir."))

                self.box.add_widget(btn)

            if not visible_any:
                self.box.add_widget(MDLabel(
                    text="(Bu bölüm filtreye göre boş)",
                    italic=True,
                    size_hint_y=None,
                    height=dp(22),
                ))


class IntroScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.lesson = None

        root = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(
            title="Ders",
            left_action_items=[["arrow-left", lambda _x: self.app.go_list()]],
        )
        try:
            self.toolbar.anchor_title = "left"
        except Exception:
            pass
        try:
            self.toolbar.title_align = "left"
        except Exception:
            pass
        root.add_widget(self.toolbar)

        scroll = ScrollView()
        self.box = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12), size_hint_y=None)
        self.box.bind(minimum_height=self.box.setter("height"))
        scroll.add_widget(self.box)
        root.add_widget(scroll)

        self.start_btn = MDRaisedButton(text="Başla", on_release=lambda _x: self.app.open_lesson(self.lesson) if self.lesson else None)
        btn_wrap = MDBoxLayout(padding=dp(16), size_hint_y=None, height=dp(64))
        btn_wrap.add_widget(self.start_btn)
        root.add_widget(btn_wrap)

        self.add_widget(root)

    def load_lesson(self, lesson):
        self.lesson = lesson
        self.toolbar.title = f"B{lesson.unit}-{lesson.order}: {lesson.title}"
        self.box.clear_widgets()

        self.box.add_widget(MDLabel(
            text=f"[b]Hedef:[/b] {lesson.goal}\n\n[b]Kısa Tanım:[/b]\n{lesson.intro or '-'}\n\n[b]Örnek:[/b]\n{lesson.example or '-'}",
            markup=True,
            size_hint_y=None,
        ))


class LessonScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.lesson = None

        root = MDBoxLayout(orientation="vertical")

        self.toolbar = MDTopAppBar(
            title="Ders",
            left_action_items=[["arrow-left", lambda _x: self.app.open_intro(self.lesson) if self.lesson else self.app.go_list()]],
        )
        try:
            self.toolbar.anchor_title = "left"
        except Exception:
            pass
        try:
            self.toolbar.title_align = "left"
        except Exception:
            pass
        root.add_widget(self.toolbar)

        # ScrollView: klavye açılınca alanın kaybolmaması için
        scroll = ScrollView()
        self.content = MDBoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12), size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll.add_widget(self.content)
        root.add_widget(scroll)

        self.meta = MDLabel(text="", markup=True, size_hint_y=None)
        self.meta.bind(texture_size=lambda *_: setattr(self.meta, "height", self.meta.texture_size[1] + dp(10)))
        self.content.add_widget(self.meta)

        self.editor = MDTextField(hint_text="Kod", multiline=True, size_hint_y=None, height=dp(260))
        self.content.add_widget(self.editor)

        self.input_box = MDTextField(hint_text="Girdi (input için) — her input() için 1 satır", multiline=True, size_hint_y=None, height=dp(110))
        self.content.add_widget(self.input_box)

        self.expected_box = MDTextField(hint_text="Örnek Beklenen Çıktı", multiline=True, readonly=True, size_hint_y=None, height=dp(90))
        self.content.add_widget(self.expected_box)

        btn_row = MDBoxLayout(orientation="horizontal", spacing=dp(12), size_hint_y=None, height=dp(56))
        self.run_btn = MDRaisedButton(text="Çalıştır", on_release=self.on_run)
        self.check_btn = MDRaisedButton(text="Kontrol Et", on_release=self.on_check)
        self.next_btn = MDRectangleFlatButton(text="Sonraki ▶", on_release=self.on_next)
        btn_row.add_widget(self.run_btn)
        btn_row.add_widget(self.check_btn)
        btn_row.add_widget(self.next_btn)
        self.content.add_widget(btn_row)

        self.output = MDTextField(hint_text="Çıktı / Hata", multiline=True, readonly=True, size_hint_y=None, height=dp(220))
        self.content.add_widget(self.output)

        self.add_widget(root)

    def load_lesson(self, lesson):
        self.lesson = lesson
        self.toolbar.title = lesson.title

        self.meta.text = (
            f"[b]Bölüm:[/b] {lesson.unit}  [b]Ders:[/b] {lesson.order}\n"
            f"[b]Hedef:[/b] {lesson.goal}\n"
            f"[b]İpucu:[/b] {lesson.hint}\n"
            f"[b]Beklenen:[/b] {lesson.expected}"
        )

        self.editor.text = lesson.starter_code or ""
        self.input_box.text = lesson.input_example or ""
        self.expected_box.text = lesson.expected_output_example or ""
        self.output.text = ""

        self.app.progress["last_lesson_id"] = lesson.id
        self.app.save()

    def on_run(self, _btn):
        res = run_user_code(self.editor.text, self.input_box.text, timeout_s=2.5)
        if res.error:
            self.output.text = "Hata:\n" + str(res.error)
        else:
            txt = res.stdout if res.stdout else "(çıktı yok)"
            err = ("\n\nstderr:\n" + res.stderr) if res.stderr else ""
            self.output.text = "Çıktı:\n" + txt + err

    def on_check(self, _btn):
        if not self.lesson:
            return

        res = run_user_code(self.editor.text, self.input_box.text, timeout_s=2.5)
        if res.error:
            self.output.text = "Önce hatayı düzelt.\n\n" + str(res.error)
            return

        failed: List[str] = []
        checks = self.lesson.checks or []
        for label, fn in checks:
            ok = False
            try:
                ok = bool(fn(res))
            except Exception:
                ok = False
            if not ok:
                failed.append(label)

        if failed:
            out_txt = res.stdout if res.stdout else "(çıktı yok)"
            self.output.text = (
                "❌ Henüz olmadı.\n\n"
                "Takıldığın yerler:\n- " + "\n- ".join(failed) + "\n\n"
                f"İpucu: {self.lesson.hint}\n\n"
                f"Beklenen örnek çıktı:\n{self.lesson.expected_output_example}\n"
                f"Senin çıktın:\n{out_txt}"
            )
            return

        # ders tamam
        xp_before = int(self.app.progress.get('xp', 0))
        coins_before = int(self.app.progress.get('coins', 0))
        first_time = self.app.mark_lesson_done(self.lesson)
        xp_after = int(self.app.progress.get('xp', 0))
        coins_after = int(self.app.progress.get('coins', 0))
        xp_gain = max(0, xp_after - xp_before)
        coin_gain = max(0, coins_after - coins_before)

        msg = "✅ Tebrikler! Görev tamam.\n"
        if first_time:
            msg += f"(+{xp_gain} XP, +{coin_gain} coin)\n"
        self.output.text = msg + "\n" + (res.stdout if res.stdout else "(çıktı yok)")

        # quiz varsa aç
        if self.lesson.quiz:
            open_quiz_dialog(self.app, self.lesson, on_finish=lambda _ok: self._after_quiz())
            return

        if self.app.progress.get("auto_next", True):
            self.app.open_next_lesson(self.lesson.id)

    def _after_quiz(self):
        if self.app.progress.get("auto_next", True) and self.lesson:
            self.app.open_next_lesson(self.lesson.id)

    def on_next(self, _btn):
        if self.lesson:
            self.app.open_next_lesson(self.lesson.id)


class ProfileScreen(MDScreen):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        root = MDBoxLayout(orientation="vertical")
        bar = MDTopAppBar(
            title="Profil",
            left_action_items=[["arrow-left", lambda _x: self.app.go_list()]],
        )
        try:
            bar.anchor_title = "left"
        except Exception:
            pass
        try:
            bar.title_align = "left"
        except Exception:
            pass
        root.add_widget(bar)

        self.info = MDLabel(text="", markup=True, padding=(dp(16), dp(16)))
        root.add_widget(self.info)

        row = MDBoxLayout(orientation="horizontal", padding=dp(16), spacing=dp(12), size_hint_y=None, height=dp(56))
        self.auto_btn = MDRectangleFlatButton(text="Otomatik: Açık", on_release=self.toggle_auto_next)
        avatar_btn = MDRectangleFlatButton(text="Avatar", on_release=lambda _x: self.open_avatar())
        reset_btn = MDRectangleFlatButton(text="Sıfırla", on_release=self.reset_all)
        row.add_widget(self.auto_btn)
        row.add_widget(avatar_btn)
        row.add_widget(reset_btn)
        root.add_widget(row)

        self.add_widget(root)

    def on_pre_enter(self, *args):
        xp = int(self.app.progress.get("xp", 0))
        lv, in_lv, to_next = level_progress(xp, self.app.LEVEL_XP)
        completed = len(set(self.app.progress.get("completed_lessons", [])))
        coins = int(self.app.progress.get("coins", 0))
        av = self.app.progress.get("avatar_id", "default")

        self.info.text = (
            f"[b]Avatar:[/b] {av}\n"
            f"[b]Level:[/b] {lv}\n"
            f"[b]XP:[/b] {xp} (bu level {in_lv}/{to_next})\n"
            f"[b]Coin:[/b] {coins}\n"
            f"[b]Tamamlanan ders:[/b] {completed}"
        )
        self.auto_btn.text = f"Otomatik: {'Açık' if self.app.progress.get('auto_next', True) else 'Kapalı'}"

    def toggle_auto_next(self, *_):
        self.app.progress["auto_next"] = not bool(self.app.progress.get("auto_next", True))
        self.app.save()
        self.on_pre_enter()

    def reset_all(self, *_):
        self.app.reset()
        self.app.toast("Sıfırlandı.")
        self.on_pre_enter()

    def open_avatar(self):
        owned = set(self.app.progress.get("owned_avatars", ["default"]))
        coins = int(self.app.progress.get("coins", 0))

        lines = []
        for a in AVATARS:
            mark = "✅" if a["id"] in owned else "🛒"
            price = int(a.get("price", 0))
            lines.append(f"{mark} {a['name']} (id={a['id']}) - {price} coin")

        text = "\n".join(lines) + f"\n\nCoin: {coins}\n\nSatın almak/seçmek için id yaz."
        input_box = MDTextField(hint_text="avatar id (örn: coder)", mode="rectangle")

        dialog = None

        def buy(*_):
            nonlocal dialog
            aid = (input_box.text or "").strip()
            if not aid:
                return
            found = next((x for x in AVATARS if x["id"] == aid), None)
            if not found:
                self.app.toast("Bulunamadı.")
                return

            owned2 = set(self.app.progress.get("owned_avatars", ["default"]))

            if aid in owned2:
                self.app.progress["avatar_id"] = aid
                self.app.save()
                self.app.toast("Avatar seçildi.")
                try:
                    dialog.dismiss()
                except Exception:
                    pass
                return

            price = int(found.get("price", 0))
            coins2 = int(self.app.progress.get("coins", 0))
            if coins2 < price:
                self.app.toast("Yetersiz coin.")
                return

            coins2 -= price
            owned2.add(aid)
            self.app.progress["coins"] = coins2
            self.app.progress["owned_avatars"] = sorted(owned2)
            self.app.progress["avatar_id"] = aid
            self.app.save()
            self.app.toast("Satın alındı ve seçildi.")
            try:
                dialog.dismiss()
            except Exception:
                pass

        content = MDBoxLayout(orientation="vertical", padding=dp(12), spacing=dp(12))
        content.add_widget(MDLabel(text=text))
        content.add_widget(input_box)

        dialog = MDDialog(
            title="Avatar",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Seç/Satın Al", on_release=buy),
                MDFlatButton(text="Kapat", on_release=lambda _x: dialog.dismiss()),
            ],
        )
        dialog.open()
