import os

# Buildozer/python-for-android passes args; keep Kivy from parsing them
os.environ.setdefault("KIVY_NO_ARGS", "1")
os.environ.setdefault("KIVY_LOG_LEVEL", "info")

from app import PythonOgrenApp

if __name__ == "__main__":
    PythonOgrenApp().run()
