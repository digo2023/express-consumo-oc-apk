[app]
title = EXPRESS CONSUMO OC
package.name = expressconsumooc
package.domain = org.maicon
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,ttf,pdf,csv,xlsx
version = 1.5.0
requirements = python3,kivy==2.2.1,pyjnius,android,plyer,pypdf,openpyxl,pillow,python-dateutil
orientation = portrait
fullscreen = 0
android.api = 34
android.minapi = 28
android.ndk_api = 28
android.ndk = 25b
android.archs = arm64-v8a
# Pinagem estável: evita o python-for-android master usar Python 3.14 incompatível com Kivy.
p4a.branch = v2024.01.21
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.accept_sdk_license = True
android.private_storage = True
android.allow_backup = True
presplash.color = #050914
icon.filename = assets/icon.png
presplash.filename = assets/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1

# Versão V1.5: BuildFix definitivo com p4a v2024.01.21 + Kivy 2.2.1.
