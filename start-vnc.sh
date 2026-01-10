#!/bin/bash
Xvfb :99 -screen 0 1280x800x24 &
export DISPLAY=:99
fluxbox &  # 轻量窗口管理器

chromium-browser --no-sandbox --remote-debugging-port=9222 &  # 可选：先启动 Chrome

x11vnc -display :99 -forever -shared -rfbport 5900 -noxdamage &
websockify --web /usr/share/novnc/ 6080 localhost:5900 &
