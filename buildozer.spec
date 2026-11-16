[app][app]
title = Test App
package.name = testapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3, kivy==2.2.0

android.permissions = android.permission.INTERNET
android.api = 30
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
android.build_tools_version = 30.0.3
android.bootstrap = sdl2
android.harfbuzz = 0
android.sdl2_ttf = 0

[buildozer]
log_level = 2
