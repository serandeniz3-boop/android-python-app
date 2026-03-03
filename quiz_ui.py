from typing import Any, Dict, Callable, Optional

from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton

try:
    from kivymd.uix.list import MDList, OneLineListItem
except Exception:
    MDList = None
    OneLineListItem = None

def open_quiz_dialog(app, lesson, on_finish: Optional[Callable[[bool], None]] = None) -> None:
    q = getattr(lesson, "quiz", None)
    if (not q) or app.is_quiz_done(lesson.id):
        if on_finish:
            on_finish(True)
        return

    question = q.get("q", "") if isinstance(q, dict) else ""
    choices  = q.get("choices", []) if isinstance(q, dict) else []
    correct  = int(q.get("answer", -1)) if isinstance(q, dict) else -1
    explain  = q.get("explain", "") if isinstance(q, dict) else ""

    state = {"tries": 0, "selected": -1}

    content = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=(dp(12), dp(12), dp(12), dp(6)))
    content.size_hint_y = None
    content.bind(minimum_height=content.setter("height"))

    lbl_q = MDLabel(text=f"[b]{question}[/b]", markup=True, size_hint_y=None)
    lbl_q.bind(texture_size=lambda *_: setattr(lbl_q, "height", lbl_q.texture_size[1] + dp(10)))
    content.add_widget(lbl_q)

    if MDList is None or OneLineListItem is None:
        for i, ch in enumerate(choices):
            b = MDFlatButton(text=("○ " + str(ch)), on_release=lambda _x, idx=i: state.update(selected=idx))
            content.add_widget(b)
        scroll = None
    else:
        lst = MDList()

        def select_idx(idx: int):
            state["selected"] = idx
            items = lst.children[::-1]
            for i2 in range(len(items)):
                txt = str(choices[i2])
                items[i2].text = ("✅ " if i2 == idx else "○ ") + txt

        for i, ch in enumerate(choices):
            item = OneLineListItem(text="○ " + str(ch))
            item.bind(on_release=lambda _x, idx=i: select_idx(idx))
            lst.add_widget(item)

        scroll = ScrollView(size_hint=(1, None), height=dp(180))
        scroll.add_widget(lst)
        content.add_widget(scroll)

    lbl_info = MDLabel(text="", theme_text_color="Error", size_hint_y=None)
    lbl_info.bind(texture_size=lambda *_: setattr(lbl_info, "height", lbl_info.texture_size[1] + dp(10)))
    content.add_widget(lbl_info)

    dialog = None

    def close_after(delay_s: float, ok: bool):
        from kivy.clock import Clock
        def _close(*_a):
            nonlocal dialog
            try:
                if dialog:
                    dialog.dismiss()
            except Exception:
                pass
            if on_finish:
                on_finish(ok)
        Clock.schedule_once(_close, delay_s)

    def submit(*_):
        if state["selected"] < 0:
            lbl_info.text = "Bir şık seç."
            return

        ok = (int(state["selected"]) == int(correct))
        if ok:
            app.mark_quiz_done(lesson.id)
            bonus = app.quiz_add_bonus()
            lbl_info.theme_text_color = "Custom"
            lbl_info.text = f"Doğru ✅ (+{bonus} XP)\n{explain}".strip()
            close_after(0.6, True)
        else:
            state["tries"] += 1
            app.quiz_reset_streak()
            if state["tries"] > int(app.QUIZ_MAX_TRIES):
                safe_correct = ""
                try:
                    safe_correct = str(choices[int(correct)])
                except Exception:
                    safe_correct = ""
                lbl_info.text = f"Hakkın bitti ❌\nDoğru: {safe_correct}\n{explain}".strip()
                close_after(1.2, False)
            else:
                kalan = int(app.QUIZ_MAX_TRIES) - state["tries"] + 1
                lbl_info.text = f"Yanlış ❌ (Kalan: {kalan})"

    dialog = MDDialog(
        title="Mini Quiz",
        type="custom",
        content_cls=content,
        buttons=[MDFlatButton(text="Cevapla", on_release=submit)],
    )
    dialog.open()
