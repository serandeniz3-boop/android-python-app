[app]

title = Screen Translate
package.name = screentranslate
package.domain = org.example

source.dir = .
source.include_exts = py,json

version = 0.1

requirements = python3,kivy,kivymd

orientation = portrait
fullscreen = 0

# If you later add audio/images/fonts, extend these:
# source.include_patterns = assets/*

[buildozer]

log_level = 2

warn_on_root = 1

[android]

# Android API / NDK
android.api = 33
android.minapi = 21
android.ndk = 25b

# Optional: reduce size by removing unused architectures
android.archs = arm64-v8a,armeabi-v7a

android.permissions = INTERNET

# If keyboard overlaps, Android usually handles it; in-app ScrollView helps.
